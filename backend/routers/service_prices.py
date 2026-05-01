import os
import sys
from fastapi import APIRouter, Body, Depends, HTTPException

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from auth import get_current_user
from supabase_client import supabase
from knowledge_base import kb_loader

router = APIRouter()

@router.get("/service-prices/")
def get_service_prices(user=Depends(get_current_user)):
    """Return the current service prices from Supabase for the logged in shop."""
    try:
        res = supabase.table("profiles").select("service_prices").eq("id", user.id).execute()
        if res.data:
            return res.data[0].get("service_prices", {})
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/service-prices/")
def update_service_prices(prices: dict = Body(...), user=Depends(get_current_user)):
    """Update service prices in Supabase for the logged in shop."""
    try:
        supabase.table("profiles").update({
            "service_prices": prices
        }).eq("id", user.id).execute()
        
        # We can't invalidate a global cache easily in a multi-tenant app, 
        # so we will rely on fetching it per request in the future, 
        # or clearing a local cache if implemented.
        kb_loader.invalidate_cache("service_prices.json")
        
        return {"success": True, "prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
