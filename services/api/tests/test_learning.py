from httpx import AsyncClient


async def test_student_learning_workspaces_are_persisted(client: AsyncClient) -> None:
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Learning Student",
            "email": "learning@example.com",
            "password": "SecurePass123",
        },
    )
    assert registration.status_code == 201

    syllabus = await client.get("/api/v1/syllabus")
    assert syllabus.status_code == 200
    assert len(syllabus.json()) >= 1

    task = await client.post(
        "/api/v1/planner",
        json={"title": "MCQ sprint", "subject": "Taxation", "due_date": "2026-09-25", "minutes": 30},
    )
    assert task.status_code == 201
    task_id = task.json()["id"]

    updated = await client.patch(f"/api/v1/planner/{task_id}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    query = await client.post(
        "/api/v1/queries",
        json={"subject": "Taxation", "title": "A doubt", "body": "Please explain this topic."},
    )
    assert query.status_code == 201
    assert (await client.get("/api/v1/queries")).json()[0]["title"] == "A doubt"

    analytics = await client.get("/api/v1/analytics/summary")
    assert analytics.status_code == 200
    assert analytics.json()["completed_tasks"] == 1
