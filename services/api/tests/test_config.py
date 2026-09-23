from app.core.config import Settings


def test_comma_separated_cors_origins_are_normalized() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins="http://localhost:3000, https://app.example.com",
    )

    assert settings.cors_origins == [
        "http://localhost:3000",
        "https://app.example.com",
    ]
