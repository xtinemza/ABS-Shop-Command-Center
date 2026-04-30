"""
Router: Profile & Health
Uses Supabase for multi-tenant storage.
"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import get_current_user
from supabase_client import supabase
from models.responses import ProfileResponse, HealthResponse

router = APIRouter()

# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ProfileSaveRequest(BaseModel):
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    hours: Optional[str] = None
    services: Optional[object] = None   # str or list
    business_type: Optional[str] = None
    website: Optional[str] = None
    tagline: Optional[str] = None
    tone: Optional[str] = None
    google_review_link: Optional[str] = None

class SetupRequest(BaseModel):
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    hours: Optional[str] = None
    services: Optional[object] = None
    business_type: Optional[str] = None
    website: Optional[str] = None
    tagline: Optional[str] = None
    tone: Optional[str] = None
    google_review_link: Optional[str] = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_to_supabase(user_id: str, updates: dict) -> dict:
    """Merge updates into existing profile in Supabase."""
    # First, get current profile
    res = supabase.table("profiles").select("shop_info").eq("id", user_id).execute()
    
    current_info = {}
    if res.data and res.data[0].get("shop_info"):
        current_info = res.data[0]["shop_info"]

    # Merge simple scalar fields
    scalar_fields = [
        "shop_name", "owner_name", "phone", "street", "city", "state", "zip",
        "hours", "business_type", "website", "tagline", "tone", "google_review_link"
    ]
    for field in scalar_fields:
        if field in updates and updates[field] is not None:
            current_info[field] = updates[field]

    # Services as list
    if updates.get("services"):
        if isinstance(updates["services"], list):
            current_info["services"] = updates["services"]
        else:
            current_info["services"] = [s.strip() for s in str(updates["services"]).split(",")]

    # Update in Supabase
    update_res = supabase.table("profiles").update({
        "shop_info": current_info
    }).eq("id", user_id).execute()
    
    return update_res.data[0]["shop_info"] if update_res.data else current_info

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/profile", response_model=ProfileResponse)
def get_profile(user=Depends(get_current_user)):
    try:
        res = supabase.table("profiles").select("shop_info").eq("id", user.id).execute()
        profile = res.data[0].get("shop_info", {}) if res.data else {}
        return ProfileResponse(success=True, profile=profile)
    except Exception as exc:
        return ProfileResponse(success=False, profile={}, error=str(exc))


@router.post("/profile/save", response_model=ProfileResponse)
def save_profile(body: ProfileSaveRequest, user=Depends(get_current_user)):
    try:
        updated = _save_to_supabase(user.id, body.dict(exclude_unset=True))
        return ProfileResponse(success=True, profile=updated)
    except Exception as exc:
        return ProfileResponse(success=False, profile={}, error=str(exc))


@router.post("/setup", response_model=ProfileResponse)
def setup(body: SetupRequest, user=Depends(get_current_user)):
    try:
        updated = _save_to_supabase(user.id, body.dict(exclude_unset=True))
        return ProfileResponse(success=True, profile=updated)
    except Exception as exc:
        return ProfileResponse(success=False, profile={}, error=str(exc))


@router.get("/health", response_model=HealthResponse)
def health(user=Depends(get_current_user)):
    try:
        res = supabase.table("profiles").select("shop_info").eq("id", user.id).execute()
        profile = res.data[0].get("shop_info", {}) if res.data else {}
        # Setup is complete if shop_name exists
        setup_complete = bool(profile.get("shop_name"))
        return HealthResponse(status="ok", setup_complete=setup_complete)
    except Exception:
        # If user is not authenticated or error occurs, assume health check needs setup
        return HealthResponse(status="ok", setup_complete=False)
