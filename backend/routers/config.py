"""
Router: Config — save and load API keys and app settings.
POST /api/config/save
GET  /api/config
"""
import json
import os
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

_DATA_DIR = "/data" if os.path.isdir("/data") else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)
CONFIG_PATH = os.path.join(_DATA_DIR, "config.json")

router = APIRouter()


def _load_config() -> dict:
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_config(data: dict) -> dict:
    cfg = _load_config()
    cfg.update({k: v for k, v in data.items() if v is not None})
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg


class ConfigSaveRequest(BaseModel):
    anthropic_api_key: Optional[str] = None


@router.get("/config")
def get_config():
    cfg = _load_config()
    # Mask the key for display — only show last 4 chars
    masked = {}
    if cfg.get("anthropic_api_key"):
        key = cfg["anthropic_api_key"]
        masked["anthropic_api_key"] = "sk-ant-..." + key[-4:] if len(key) > 8 else "****"
        masked["anthropic_api_key_set"] = True
    else:
        masked["anthropic_api_key"] = ""
        masked["anthropic_api_key_set"] = False
    return {"success": True, "config": masked}


@router.post("/config/save")
def save_config(body: ConfigSaveRequest):
    try:
        data = {k: v for k, v in body.dict().items() if v}
        _save_config(data)
        # Also inject into the running process environment immediately
        if body.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = body.anthropic_api_key
        return {"success": True, "message": "Configuration saved."}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
