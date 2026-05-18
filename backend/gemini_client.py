"""
Shared Gemini AI client for all routers.
Import: from gemini_client import get_gemini, call_gemini, load_profile
"""
import os
from supabase_client import supabase


def load_profile(user_id: str) -> dict:
    try:
        res = supabase.table("shop_profiles").select("shop_info").eq("id", user_id).execute()
        return res.data[0].get("shop_info", {}) if res.data else {}
    except Exception:
        return {}


def get_gemini():
    """Returns (genai_module, error_str). genai is None if setup fails."""
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return None, "AI features are not yet enabled. Please contact support."
        genai.configure(api_key=api_key)
        return genai, None
    except ImportError:
        return None, "The 'google-generativeai' package is not installed."


def call_gemini(client, system: str, prompt: str, max_tokens: int = 1200,
                model: str = "gemini-2.5-flash-lite") -> tuple:
    """Returns (text, error_str). text is None if call fails."""
    try:
        gemini_model = client.GenerativeModel(
            model_name=model,
            system_instruction=system,
            generation_config={"max_output_tokens": max_tokens},
        )
        response = gemini_model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        err = str(e)
        if "quota" in err.lower() or "resource_exhausted" in err.lower():
            return None, "AI service quota reached. Please try again in a moment."
        if "api_key" in err.lower() or "permission" in err.lower():
            return None, "AI service is not configured correctly. Please contact support."
        return None, "AI service error. Please try again."


def shop_context(profile: dict) -> str:
    """Build a compact shop identity string for injection into system prompts."""
    name     = profile.get("shop_name") or "our shop"
    phone    = profile.get("phone") or ""
    website  = profile.get("website") or ""
    address  = profile.get("address") or profile.get("location") or ""
    owner    = profile.get("owner_name") or f"The Team at {name}"
    tone     = profile.get("tone") or "warm and professional"
    review   = (profile.get("review_links") or {}).get("google", "")
    return (
        f"Shop: {name} | Owner: {owner} | Phone: {phone} | "
        f"Address: {address} | Website: {website} | Tone: {tone}"
        + (f" | Google Review: {review}" if review else "")
    )
