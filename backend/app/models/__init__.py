"""ORM models. Importing this package registers every model on ``Base.metadata``
so Alembic autogeneration and ``create_all`` see them."""

from app.database.session import Base
from app.models.application import Application
from app.models.job import Job

__all__ = ["Base", "Job", "Application"]
