from pydantic import BaseModel
from typing import Dict, List, Optional


class ModuleResponse(BaseModel):
    success: bool
    output: str                          # Full generated text (captured stdout)
    files: List[str]                     # Paths of files saved
    content: Optional[Dict[str, str]] = None  # { filename: file_content }
    error: Optional[str] = None


class ProfileResponse(BaseModel):
    success: bool
    profile: dict
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    setup_complete: bool
