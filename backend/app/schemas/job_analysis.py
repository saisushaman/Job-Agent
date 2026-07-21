"""Job analysis schemas (Phase 4).

The model produces evidence-based, structured analysis of a manually imported job.
Eligibility is NOT trusted from the model — it is recomputed deterministically by
``compute_eligibility`` so hard rules (citizenship required => never apply) always hold.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Region(str, Enum):
    USA = "USA"
    EUROPE = "EUROPE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class SponsorshipUS(str, Enum):
    SPONSORSHIP_EXPLICIT = "SPONSORSHIP_EXPLICIT"
    SPONSORSHIP_LIKELY = "SPONSORSHIP_LIKELY"
    SPONSORSHIP_UNCLEAR = "SPONSORSHIP_UNCLEAR"
    SPONSORSHIP_UNLIKELY = "SPONSORSHIP_UNLIKELY"
    NO_SPONSORSHIP = "NO_SPONSORSHIP"
    WORK_AUTH_REQUIRED = "WORK_AUTH_REQUIRED"


class VisaSupportEU(str, Enum):
    VISA_SUPPORT_EXPLICIT = "VISA_SUPPORT_EXPLICIT"
    VISA_SUPPORT_LIKELY = "VISA_SUPPORT_LIKELY"
    VISA_SUPPORT_UNCLEAR = "VISA_SUPPORT_UNCLEAR"
    VISA_SUPPORT_UNLIKELY = "VISA_SUPPORT_UNLIKELY"
    NO_VISA_SUPPORT = "NO_VISA_SUPPORT"
    EU_WORK_AUTH_REQUIRED = "EU_WORK_AUTH_REQUIRED"


class Eligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    REVIEW = "REVIEW"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class EnglishCompatibility(str, Enum):
    ENGLISH_OK = "ENGLISH_OK"
    OTHER_LANGUAGE_REQUIRED = "OTHER_LANGUAGE_REQUIRED"
    UNCLEAR = "UNCLEAR"


class Relocation(str, Enum):
    REMOTE = "REMOTE"
    RELOCATION_SUPPORTED = "RELOCATION_SUPPORTED"
    RELOCATION_REQUIRED = "RELOCATION_REQUIRED"
    ONSITE_NO_RELOCATION = "ONSITE_NO_RELOCATION"
    NOT_MENTIONED = "NOT_MENTIONED"


class JobAnalysisResult(BaseModel):
    """Structured output the model must return (validated + retried)."""

    region: Region = Region.UNKNOWN
    sponsorship_us: SponsorshipUS | None = None
    visa_support_eu: VisaSupportEU | None = None
    work_authorization_required: bool = False
    citizenship_required: bool = False
    citizenship_evidence: str | None = Field(
        None, description="Exact quote from the job text indicating citizenship is required."
    )
    security_clearance_required: bool = False
    relocation: Relocation = Relocation.NOT_MENTIONED
    english_compatibility: EnglishCompatibility = EnglishCompatibility.UNCLEAR
    technical_skills: list[str] = Field(default_factory=list)
    experience_years_min: int | None = None
    experience_level: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    sponsorship_evidence: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    summary: str = ""

    # Filled in deterministically after the model responds (see compute_eligibility).
    eligibility: Eligibility = Eligibility.REVIEW


# Categories that mean the candidate (who needs sponsorship) cannot take the job.
_US_BLOCKING = {SponsorshipUS.NO_SPONSORSHIP, SponsorshipUS.WORK_AUTH_REQUIRED}
_US_REVIEW = {SponsorshipUS.SPONSORSHIP_UNCLEAR, SponsorshipUS.SPONSORSHIP_UNLIKELY}
_US_OK = {SponsorshipUS.SPONSORSHIP_EXPLICIT, SponsorshipUS.SPONSORSHIP_LIKELY}
_EU_BLOCKING = {VisaSupportEU.NO_VISA_SUPPORT, VisaSupportEU.EU_WORK_AUTH_REQUIRED}
_EU_REVIEW = {VisaSupportEU.VISA_SUPPORT_UNCLEAR, VisaSupportEU.VISA_SUPPORT_UNLIKELY}
_EU_OK = {VisaSupportEU.VISA_SUPPORT_EXPLICIT, VisaSupportEU.VISA_SUPPORT_LIKELY}


def compute_eligibility(result: JobAnalysisResult) -> Eligibility:
    """Deterministic eligibility for a sponsorship-needing candidate.

    Hard exclusions win: citizenship or a clearance (which implies citizenship) => never
    apply. Otherwise derive from the sponsorship/visa category.
    """
    if result.citizenship_required or result.security_clearance_required:
        return Eligibility.NOT_ELIGIBLE

    if result.region is Region.USA and result.sponsorship_us is not None:
        if result.sponsorship_us in _US_BLOCKING:
            return Eligibility.NOT_ELIGIBLE
        if result.sponsorship_us in _US_OK:
            return Eligibility.ELIGIBLE
        if result.sponsorship_us in _US_REVIEW:
            return Eligibility.REVIEW

    if result.region is Region.EUROPE and result.visa_support_eu is not None:
        if result.visa_support_eu in _EU_BLOCKING:
            return Eligibility.NOT_ELIGIBLE
        if result.visa_support_eu in _EU_OK:
            return Eligibility.ELIGIBLE
        if result.visa_support_eu in _EU_REVIEW:
            return Eligibility.REVIEW

    # Work authorization required but no positive sponsorship signal -> not eligible.
    if result.work_authorization_required and not (
        result.sponsorship_us in _US_OK or result.visa_support_eu in _EU_OK
    ):
        return Eligibility.NOT_ELIGIBLE

    return Eligibility.REVIEW


# --- API request/response shapes ---


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    country: str | None = None
    city: str | None = None
    url: str | None = None
    description: str | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    country: str | None
    city: str | None
    url: str | None
    description: str | None


class JobAnalysisOut(BaseModel):
    job_id: int
    region: Region
    eligibility: Eligibility
    citizenship_required: bool
    result: JobAnalysisResult
