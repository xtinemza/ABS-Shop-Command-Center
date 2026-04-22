"""
Router: Profile & Health  (GET /api/profile, POST /api/profile/save,
                            POST /api/setup, GET /api/health)
"""
import json
import os
import sys
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

# Ensure shared tools are importable
_TOOLS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tools")
)
if _TOOLS_ROOT not in sys.path:
    sys.path.insert(0, _TOOLS_ROOT)

# Use /data (Render persistent disk) in production, fall back to repo data/ locally
_DATA_DIR = "/data" if os.path.isdir("/data") else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROFILE_PATH = os.path.join(_DATA_DIR, "shop_profile.json")

from models.responses import ProfileResponse, HealthResponse
from utils import capture_output

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_profile() -> dict:
    if not os.path.exists(PROFILE_PATH):
        return {}
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_profile(updates: dict) -> dict:
    """Merge updates into existing profile and write to disk."""
    profile = _load_profile()

    # Merge simple scalar fields
    scalar_fields = [
        "shop_name", "owner_name", "location", "address",
        "phone", "hours", "business_type", "website", "tagline", "tone",
    ]
    for field in scalar_fields:
        if field in updates and updates[field] is not None:
            profile[field] = updates[field]

    # Services as list
    if updates.get("services"):
        if isinstance(updates["services"], list):
            profile["services"] = updates["services"]
        else:
            profile["services"] = [s.strip() for s in str(updates["services"]).split(",")]

    # Nested: review_links
    if updates.get("google_review"):
        profile.setdefault("review_links", {})["google"] = updates["google_review"]
    if updates.get("yelp_review"):
        profile.setdefault("review_links", {})["yelp"] = updates["yelp_review"]

    # Nested: social_media
    if updates.get("facebook"):
        profile.setdefault("social_media", {})["facebook"] = updates["facebook"]
    if updates.get("instagram"):
        profile.setdefault("social_media", {})["instagram"] = updates["instagram"]

    # Mark setup complete when minimum fields present
    required = ["shop_name", "owner_name", "location", "phone"]
    if all(profile.get(f) for f in required):
        profile["setup_complete"] = True

    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as fh:
        json.dump(profile, fh, indent=2, ensure_ascii=False)

    return profile


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ProfileSaveRequest(BaseModel):
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    hours: Optional[str] = None
    services: Optional[object] = None   # str or list
    business_type: Optional[str] = None
    website: Optional[str] = None
    tagline: Optional[str] = None
    tone: Optional[str] = None
    google_review: Optional[str] = None
    yelp_review: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None


class SetupRequest(BaseModel):
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    hours: Optional[str] = None
    services: Optional[object] = None
    business_type: Optional[str] = None
    website: Optional[str] = None
    tagline: Optional[str] = None
    tone: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/profile", response_model=ProfileResponse)
def get_profile():
    try:
        profile = _load_profile()
        return ProfileResponse(success=True, profile=profile)
    except Exception as exc:
        return ProfileResponse(success=False, profile={}, error=str(exc))


@router.post("/profile/save", response_model=ProfileResponse)
def save_profile(body: ProfileSaveRequest):
    try:
        updated = _save_profile(body.dict())
        return ProfileResponse(success=True, profile=updated)
    except Exception as exc:
        return ProfileResponse(success=False, profile={}, error=str(exc))


@router.post("/setup", response_model=ProfileResponse)
def setup(body: SetupRequest):
    try:
        updated = _save_profile(body.dict())
        return ProfileResponse(success=True, profile=updated)
    except Exception as exc:
        return ProfileResponse(success=False, profile={}, error=str(exc))


@router.get("/health", response_model=HealthResponse)
def health():
    profile = _load_profile()
    setup_complete = bool(profile.get("setup_complete"))
    return HealthResponse(status="ok", setup_complete=setup_complete)
