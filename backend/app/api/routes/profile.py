"""Candidate profile routes (Phase 5)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.matching import ProfileOut, ProfileUpdate
from app.services.profile import get_or_create_profile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)) -> ProfileOut:
    return ProfileOut.model_validate(get_or_create_profile(db))


@router.put("", response_model=ProfileOut)
def update_profile(
    body: ProfileUpdate, db: Session = Depends(get_db)
) -> ProfileOut:
    profile = get_or_create_profile(db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return ProfileOut.model_validate(profile)
