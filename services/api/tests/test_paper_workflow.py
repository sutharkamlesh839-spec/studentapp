from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.models.audit import AuditLog
from app.models.rbac import Permission, Role, role_permissions
from app.models.user import User
from app.services.auth_service import AuthService


async def provision_user(db: AsyncSession, email: str, role_code: str, permissions: tuple[str, ...] = ()) -> tuple[User, str]:
    role = await db.scalar(select(Role).where(Role.code == role_code))
    if not role:
        role = Role(code=role_code, name=role_code.title(), is_system=True)
        db.add(role)
        await db.flush()
    for permission_code in permissions:
        permission = await db.scalar(select(Permission).where(Permission.code == permission_code))
        if not permission:
            permission = Permission(code=permission_code, description=permission_code.replace(".", " ").title())
            db.add(permission)
            await db.flush()
        assigned = await db.scalar(
            select(role_permissions.c.permission_id).where(
                role_permissions.c.role_id == role.id,
                role_permissions.c.permission_id == permission.id,
            )
        )
        if assigned is None:
            await db.execute(role_permissions.insert().values(role_id=role.id, permission_id=permission.id))
    user = User(
        email=email,
        normalized_email=email,
        password_hash=hash_password("SecurePass123"),
        full_name=role_code.title(),
    )
    user.roles.append(role)
    db.add(user)
    await db.flush()
    _, session = await AuthService.create_session(db, user)
    token = create_access_token(user_id=str(user.id), session_id=str(session.id), role_codes=[role_code])
    await db.commit()
    return user, token


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_paper_assignment_isolation_review_and_notification(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    student, student_token = await provision_user(db_session, "student@papers.example", "student")
    faculty_a, faculty_a_token = await provision_user(db_session, "faculty-a@papers.example", "faculty", ("evaluation.mark",))
    _, faculty_b_token = await provision_user(db_session, "faculty-b@papers.example", "faculty", ("evaluation.mark",))
    _, admin_token = await provision_user(db_session, "admin@papers.example", "admin", ("user.manage",))

    uploaded = await client.post(
        "/api/v1/papers/upload",
        headers=auth(student_token),
        data={"title": "September answer sheet", "subject": "Advanced Accounting"},
        files={"file": ("answer-sheet.pdf", b"%PDF-1.4\nanswer sheet", "application/pdf")},
    )
    assert uploaded.status_code == 201
    paper = uploaded.json()
    paper_id = paper["id"]
    assert paper["status"] == "submitted"
    assert paper["assigned_to"] is None

    # An unassigned submission is visible to its student and admin, never to faculty.
    assert (await client.get("/api/v1/papers", headers=auth(student_token))).json()[0]["id"] == paper_id
    assert (await client.get("/api/v1/papers", headers=auth(faculty_a_token))).json() == []
    assert (await client.get("/api/v1/papers", headers=auth(faculty_b_token))).json() == []
    assert len((await client.get("/api/v1/papers", headers=auth(admin_token))).json()) == 1

    assigned = await client.patch(
        f"/api/v1/papers/{paper_id}/assign",
        headers=auth(admin_token),
        json={"faculty_id": str(faculty_a.id)},
    )
    assert assigned.status_code == 200
    assert assigned.json()["status"] == "assigned"
    assert assigned.json()["assigned_to"] == str(faculty_a.id)

    assert len((await client.get("/api/v1/papers", headers=auth(faculty_a_token))).json()) == 1
    assert (await client.get("/api/v1/papers", headers=auth(faculty_b_token))).json() == []
    assert (await client.get(f"/api/v1/papers/{paper_id}/download", headers=auth(faculty_b_token))).status_code == 403
    assert (await client.post(
        f"/api/v1/papers/{paper_id}/annotated",
        headers=auth(faculty_b_token),
        data={"marks": "72", "feedback": "Not your paper."},
        files={"file": ("review.pdf", b"%PDF-1.4\nwrong reviewer", "application/pdf")},
    )).status_code == 403

    reviewed = await client.post(
        f"/api/v1/papers/{paper_id}/annotated",
        headers=auth(faculty_a_token),
        data={"marks": "72.5", "feedback": "Good structure. Revisit the consolidation adjustment in question two."},
        files={"file": ("reviewed-answer-sheet.pdf", b"%PDF-1.4\nreviewed answer sheet", "application/pdf")},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "evaluated"
    assert reviewed.json()["marks"] == 72.5
    assert reviewed.json()["annotated_file_name"] == "reviewed-answer-sheet.pdf"

    student_view = (await client.get("/api/v1/papers", headers=auth(student_token))).json()[0]
    assert student_view["feedback"].startswith("Good structure")
    assert (await client.get(f"/api/v1/papers/{paper_id}/annotated-download", headers=auth(student_token))).status_code == 200
    notifications = (await client.get("/api/v1/notifications", headers=auth(student_token))).json()
    assert any(item["kind"] == "evaluation" for item in notifications)

    audit_actions = (await db_session.scalars(select(AuditLog.action))).all()
    assert "paper.submitted" in audit_actions
    assert "paper.assigned" in audit_actions
    assert "paper.annotated" in audit_actions
    assert "paper.evaluated" in audit_actions


async def test_paper_upload_rejects_non_pdf(client: AsyncClient, db_session: AsyncSession) -> None:
    _, student_token = await provision_user(db_session, "pdf-only@example.com", "student")
    response = await client.post(
        "/api/v1/papers/upload",
        headers=auth(student_token),
        data={"title": "Not a PDF", "subject": "Law"},
        files={"file": ("answer-sheet.docx", b"not a PDF", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 415
    assert response.json()["detail"] == "Paper file type is not permitted"
