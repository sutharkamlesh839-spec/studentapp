import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test-studentos.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-that-is-long-enough-for-local-tests")
os.environ.setdefault("APP_ENV", "test")
