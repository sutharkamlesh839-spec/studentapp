from httpx import AsyncClient


async def test_registration_login_and_refresh(client: AsyncClient) -> None:
    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Priya Shah",
            "email": "priya@example.com",
            "mobile": "",
            "password": "SecurePass123",
        },
    )
    assert registration.status_code == 201
    assert registration.json()["user"]["roles"] == ["student"]

    profile = await client.get("/api/v1/auth/me")
    assert profile.status_code == 200
    assert profile.json()["email"] == "priya@example.com"

    refresh = await client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    assert refresh.json()["user"]["full_name"] == "Priya Shah"


async def test_duplicate_email_is_rejected(client: AsyncClient) -> None:
    payload = {"full_name": "Priya Shah", "email": "same@example.com", "password": "SecurePass123"}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    duplicate = await client.post("/api/v1/auth/register", json=payload)
    assert duplicate.status_code == 409
