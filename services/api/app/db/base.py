from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Single metadata registry used by SQLAlchemy and Alembic."""


metadata = Base.metadata
