"""ORM models. Importing this package registers every model on ``Base.metadata``
so Alembic autogeneration and ``create_all`` see them."""

from app.database.session import Base
from app.models.application import Application, ApplicationEvent
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.job_match import JobMatch
from app.models.resume import Resume, ResumeVersion

__all__ = [
    "Base",
    "Job",
    "Application",
    "ApplicationEvent",
    "JobAnalysis",
    "JobMatch",
    "CandidateProfile",
    "Resume",
    "ResumeVersion",
]
