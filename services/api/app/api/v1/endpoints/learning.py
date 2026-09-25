from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import DB, CurrentUser, require_permission
from app.models.learning import (
    MCQQuestion,
    MCQResponse,
    Notification,
    PracticeTest,
    RevisionItem,
    StudyPlanTask,
    SupportQuery,
    SyllabusItem,
    TestAttempt,
)
from app.models.resources import ResourceProgress
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.learning import (
    AnalyticsSummary,
    MCQAnswerRequest,
    MCQAnswerResponse,
    MCQCreate,
    MCQMistakeResponse,
    NotificationResponse,
    PlanTaskCreate,
    PlanTaskResponse,
    PlanTaskUpdate,
    QueryCreate,
    QueryReply,
    QueryResponse,
    RevisionCreate,
    RevisionResponse,
    RevisionUpdate,
    SyllabusCreate,
    SyllabusResponse,
    SyllabusUpdate,
    TestAttemptResponse,
    TestCreate,
    TestResponse,
    TestSubmitRequest,
)
from app.schemas.learning import (
    MCQResponse as MCQResponseSchema,
)

router = APIRouter(tags=["learning"])
ContentPublisher = Depends(require_permission("content.publish"))
QueryAnswerer = Depends(require_permission("query.answer"))

DEFAULT_SYLLABUS = (
    ("Advanced Accounting", "Consolidated financial statements"),
    ("Advanced Accounting", "Accounting standards"),
    ("Corporate & Other Laws", "Companies Act fundamentals"),
    ("Corporate & Other Laws", "Meetings and management"),
    ("Taxation", "Income tax basics"),
    ("Taxation", "GST fundamentals"),
)


def mcq_response(question: MCQQuestion) -> MCQResponseSchema:
    return MCQResponseSchema(
        id=question.id,
        prompt=question.prompt,
        options=question.options,
        subject=question.subject,
        chapter=question.chapter,
        difficulty=question.difficulty,
        created_at=question.created_at,
    )


def syllabus_response(item: SyllabusItem) -> SyllabusResponse:
    progress = round((item.completed_topics / item.total_topics) * 100, 2) if item.total_topics else 0
    return SyllabusResponse(
        id=item.id,
        subject=item.subject,
        chapter=item.chapter,
        total_topics=item.total_topics,
        completed_topics=item.completed_topics,
        status=item.status,
        progress=progress,
        updated_at=item.updated_at,
    )


def test_response(test: PracticeTest) -> TestResponse:
    return TestResponse(
        id=test.id,
        title=test.title,
        description=test.description,
        duration_minutes=test.duration_minutes,
        marks=test.marks,
        question_count=len(test.question_ids or []),
        status=test.status,
        created_at=test.created_at,
    )


@router.get("/mcqs", response_model=list[MCQResponseSchema])
async def list_mcqs(
    db: DB,
    _current_user: CurrentUser,
    subject: str | None = None,
    chapter: str | None = None,
    limit: int = 20,
) -> list[MCQResponseSchema]:
    query = select(MCQQuestion).where(MCQQuestion.is_active.is_(True)).order_by(MCQQuestion.created_at.desc()).limit(min(limit, 100))
    if subject:
        query = query.where(MCQQuestion.subject == subject)
    if chapter:
        query = query.where(MCQQuestion.chapter == chapter)
    return [mcq_response(item) for item in (await db.scalars(query)).all()]


@router.post("/mcqs", response_model=MCQResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_mcq(payload: MCQCreate, db: DB, current_user: User = ContentPublisher) -> MCQResponseSchema:
    question = MCQQuestion(**payload.model_dump(), created_by=current_user.id)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return mcq_response(question)


@router.delete("/mcqs/{question_id}", response_model=MessageResponse)
async def delete_mcq(question_id: UUID, db: DB, _current_user: User = ContentPublisher) -> MessageResponse:
    question = await db.get(MCQQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="MCQ not found")
    question.is_active = False
    await db.commit()
    return MessageResponse(message="MCQ archived")


@router.post("/mcqs/{question_id}/answer", response_model=MCQAnswerResponse)
async def answer_mcq(question_id: UUID, payload: MCQAnswerRequest, db: DB, current_user: CurrentUser) -> MCQAnswerResponse:
    question = await db.get(MCQQuestion, question_id)
    if not question or not question.is_active:
        raise HTTPException(status_code=404, detail="MCQ not found")
    if payload.selected_option >= len(question.options):
        raise HTTPException(status_code=422, detail="Selected option is not available")
    correct = payload.selected_option == question.correct_option
    db.add(
        MCQResponse(
            user_id=current_user.id,
            question_id=question.id,
            selected_option=payload.selected_option,
            is_correct=correct,
        )
    )
    await db.commit()
    total = await db.scalar(select(func.count(MCQResponse.id)).where(MCQResponse.user_id == current_user.id)) or 0
    score = await db.scalar(select(func.count(MCQResponse.id)).where(MCQResponse.user_id == current_user.id, MCQResponse.is_correct.is_(True))) or 0
    return MCQAnswerResponse(
        correct=correct,
        correct_option=question.correct_option,
        explanation=question.explanation,
        score=round((score / total) * 100) if total else 0,
    )


@router.get("/mcqs/mistakes", response_model=list[MCQMistakeResponse])
async def list_mcq_mistakes(db: DB, current_user: CurrentUser) -> list[MCQMistakeResponse]:
    rows = await db.execute(
        select(MCQResponse, MCQQuestion)
        .join(MCQQuestion, MCQQuestion.id == MCQResponse.question_id)
        .where(MCQResponse.user_id == current_user.id, MCQResponse.is_correct.is_(False))
        .order_by(MCQResponse.created_at.desc())
        .limit(100)
    )
    return [
        MCQMistakeResponse(
            id=response.id,
            question_id=question.id,
            prompt=question.prompt,
            subject=question.subject,
            chapter=question.chapter,
            selected_option=response.selected_option,
            correct_option=question.correct_option,
            explanation=question.explanation,
            created_at=response.created_at,
        )
        for response, question in rows.all()
    ]


@router.get("/syllabus", response_model=list[SyllabusResponse])
async def get_syllabus(db: DB, current_user: CurrentUser) -> list[SyllabusResponse]:
    items = list((await db.scalars(select(SyllabusItem).where(SyllabusItem.user_id == current_user.id).order_by(SyllabusItem.subject, SyllabusItem.chapter))).all())
    if not items:
        items = [SyllabusItem(user_id=current_user.id, subject=subject, chapter=chapter) for subject, chapter in DEFAULT_SYLLABUS]
        db.add_all(items)
        await db.commit()
    return [syllabus_response(item) for item in items]


@router.post("/syllabus", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
async def create_syllabus_item(payload: SyllabusCreate, db: DB, current_user: CurrentUser) -> SyllabusResponse:
    item = SyllabusItem(user_id=current_user.id, **payload.model_dump())
    item.status = "completed" if item.completed_topics >= item.total_topics else "in_progress" if item.completed_topics else "not_started"
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return syllabus_response(item)


@router.patch("/syllabus/{item_id}", response_model=SyllabusResponse)
async def update_syllabus(item_id: UUID, payload: SyllabusUpdate, db: DB, current_user: CurrentUser) -> SyllabusResponse:
    item = await db.scalar(select(SyllabusItem).where(SyllabusItem.id == item_id, SyllabusItem.user_id == current_user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Syllabus item not found")
    item.completed_topics = min(payload.completed_topics, item.total_topics)
    item.status = "completed" if item.completed_topics >= item.total_topics else payload.status
    await db.commit()
    await db.refresh(item)
    return syllabus_response(item)


@router.get("/planner", response_model=list[PlanTaskResponse])
async def get_plan(db: DB, current_user: CurrentUser) -> list[PlanTaskResponse]:
    tasks = (await db.scalars(select(StudyPlanTask).where(StudyPlanTask.user_id == current_user.id).order_by(StudyPlanTask.due_date, StudyPlanTask.created_at))).all()
    return [PlanTaskResponse.model_validate(task) for task in tasks]


@router.post("/planner", response_model=PlanTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_plan_task(payload: PlanTaskCreate, db: DB, current_user: CurrentUser) -> PlanTaskResponse:
    task = StudyPlanTask(user_id=current_user.id, **payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return PlanTaskResponse.model_validate(task)


@router.patch("/planner/{task_id}", response_model=PlanTaskResponse)
async def update_plan_task(task_id: UUID, payload: PlanTaskUpdate, db: DB, current_user: CurrentUser) -> PlanTaskResponse:
    task = await db.scalar(select(StudyPlanTask).where(StudyPlanTask.id == task_id, StudyPlanTask.user_id == current_user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Plan task not found")
    task.completed = payload.completed
    await db.commit()
    await db.refresh(task)
    return PlanTaskResponse.model_validate(task)


@router.get("/revision", response_model=list[RevisionResponse])
async def get_revision(db: DB, current_user: CurrentUser) -> list[RevisionResponse]:
    items = (await db.scalars(select(RevisionItem).where(RevisionItem.user_id == current_user.id).order_by(RevisionItem.due_at))).all()
    return [RevisionResponse.model_validate(item) for item in items]


@router.post("/revision", response_model=RevisionResponse, status_code=status.HTTP_201_CREATED)
async def create_revision(payload: RevisionCreate, db: DB, current_user: CurrentUser) -> RevisionResponse:
    item = RevisionItem(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RevisionResponse.model_validate(item)


@router.patch("/revision/{item_id}", response_model=RevisionResponse)
async def update_revision(item_id: UUID, payload: RevisionUpdate, db: DB, current_user: CurrentUser) -> RevisionResponse:
    item = await db.scalar(select(RevisionItem).where(RevisionItem.id == item_id, RevisionItem.user_id == current_user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Revision item not found")
    item.status = payload.status
    await db.commit()
    await db.refresh(item)
    return RevisionResponse.model_validate(item)


@router.get("/tests", response_model=list[TestResponse])
async def list_tests(db: DB, _current_user: CurrentUser) -> list[TestResponse]:
    tests = (await db.scalars(select(PracticeTest).where(PracticeTest.status != "archived").order_by(PracticeTest.created_at.desc()))).all()
    return [test_response(item) for item in tests]


@router.post("/tests", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(payload: TestCreate, db: DB, current_user: User = ContentPublisher) -> TestResponse:
    question_ids = [str(question_id) for question_id in payload.question_ids]
    if question_ids:
        count = await db.scalar(select(func.count(MCQQuestion.id)).where(MCQQuestion.id.in_(payload.question_ids), MCQQuestion.is_active.is_(True))) or 0
        if count != len(question_ids):
            raise HTTPException(status_code=422, detail="One or more MCQs are not available")
    test = PracticeTest(**payload.model_dump(exclude={"question_ids"}), question_ids=question_ids, created_by=current_user.id)
    db.add(test)
    await db.commit()
    await db.refresh(test)
    return test_response(test)


@router.post("/tests/{test_id}/submit", response_model=TestAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_test(test_id: UUID, payload: TestSubmitRequest, db: DB, current_user: CurrentUser) -> TestAttemptResponse:
    test = await db.get(PracticeTest, test_id)
    if not test or test.status == "archived":
        raise HTTPException(status_code=404, detail="Test not found")
    question_ids = [UUID(value) for value in (test.question_ids or [])]
    questions = list((await db.scalars(select(MCQQuestion).where(MCQQuestion.id.in_(question_ids)))).all()) if question_ids else []
    correct = sum(1 for question in questions if payload.answers.get(str(question.id)) == question.correct_option)
    score = (correct / len(questions) * test.marks) if questions and test.marks else float(correct)
    attempt = TestAttempt(test_id=test.id, user_id=current_user.id, answers=payload.answers, score=score)
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return TestAttemptResponse(id=attempt.id, test_id=test.id, score=attempt.score, total_questions=len(questions), correct_answers=correct, submitted_at=attempt.submitted_at)


@router.get("/queries", response_model=list[QueryResponse])
async def list_queries(db: DB, current_user: CurrentUser) -> list[QueryResponse]:
    roles = {role.code for role in current_user.roles}
    query = select(SupportQuery).order_by(SupportQuery.created_at.desc())
    if not roles.intersection({"admin", "super_admin", "faculty"}):
        query = query.where(SupportQuery.user_id == current_user.id)
    items = (await db.scalars(query)).all()
    return [QueryResponse.model_validate(item) for item in items]


@router.post("/queries", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def create_query(payload: QueryCreate, db: DB, current_user: CurrentUser) -> QueryResponse:
    item = SupportQuery(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return QueryResponse.model_validate(item)


@router.post("/queries/{query_id}/reply", response_model=QueryResponse)
async def reply_query(query_id: UUID, payload: QueryReply, db: DB, current_user: User = QueryAnswerer) -> QueryResponse:
    item = await db.get(SupportQuery, query_id)
    if not item:
        raise HTTPException(status_code=404, detail="Query not found")
    item.answer = payload.answer
    item.status = "answered"
    item.assigned_to = current_user.id
    await db.commit()
    await db.refresh(item)
    notification = Notification(user_id=item.user_id, title="Your query has a reply", body=item.title, kind="query")
    db.add(notification)
    await db.commit()
    return QueryResponse.model_validate(item)


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(db: DB, current_user: CurrentUser) -> list[NotificationResponse]:
    items = (await db.scalars(select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(100))).all()
    return [NotificationResponse.model_validate(item) for item in items]


@router.patch("/notifications/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(notification_id: UUID, db: DB, current_user: CurrentUser) -> MessageResponse:
    item = await db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id))
    if not item:
        raise HTTPException(status_code=404, detail="Notification not found")
    item.read_at = datetime.now(UTC)
    await db.commit()
    return MessageResponse(message="Notification marked as read")


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def analytics_summary(db: DB, current_user: CurrentUser) -> AnalyticsSummary:
    attempts = await db.scalar(select(func.count(MCQResponse.id)).where(MCQResponse.user_id == current_user.id)) or 0
    correct = await db.scalar(select(func.count(MCQResponse.id)).where(MCQResponse.user_id == current_user.id, MCQResponse.is_correct.is_(True))) or 0
    completed_resources = await db.scalar(
        select(func.count(ResourceProgress.id)).where(
            ResourceProgress.user_id == current_user.id,
            ResourceProgress.completed.is_(True),
        )
    ) or 0
    completed_tasks = await db.scalar(select(func.count(StudyPlanTask.id)).where(StudyPlanTask.user_id == current_user.id, StudyPlanTask.completed.is_(True))) or 0
    pending_revision = await db.scalar(select(func.count(RevisionItem.id)).where(RevisionItem.user_id == current_user.id, RevisionItem.status != "completed")) or 0
    test_attempts = await db.scalar(select(func.count(TestAttempt.id)).where(TestAttempt.user_id == current_user.id)) or 0
    open_queries = await db.scalar(select(func.count(SupportQuery.id)).where(SupportQuery.user_id == current_user.id, SupportQuery.status == "open")) or 0
    return AnalyticsSummary(
        mcq_attempts=attempts,
        mcq_accuracy=round((correct / attempts) * 100, 2) if attempts else 0,
        completed_resources=completed_resources,
        completed_tasks=completed_tasks,
        pending_revision=pending_revision,
        test_attempts=test_attempts,
        open_queries=open_queries,
    )
