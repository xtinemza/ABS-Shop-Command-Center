"""
Shop Command Center — Knowledge Base Loader
Lazy-loads per-module JSON files from backend/knowledge_base/.

Usage:
    from kb_loader import kb, kb_context

    data  = kb("seasonal")          # returns full dict for the module
    blurb = kb_context("seasonal")  # returns a compact string for AI prompt injection
"""

import json
import os
import functools

_KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")

# ── Module → filename map ──────────────────────────────────────────────────────
# Maps the canonical module key to its JSON file (without .json extension).
# Also accepts the aliases listed in the right column.

_MODULE_FILES = {
    # Core reference data
    "vehicles":        "vehicles",
    "service_prices":  "service_prices",

    # Operational modules (matches CLAUDE.md Module Routing Table)
    "appointments":    "appointments",
    "welcome_kit":     "welcome_kit",
    "wait_time":       "wait_time",
    "declined":        "declined",
    "service_history": "service_history",
    "estimates":       "estimates",
    "inspection":      "inspection",
    "recall":          "recall",
    "equipment":       "equipment",
    "sop":             "sop",
    "warranty":        "warranty",
    "expenses":        "expenses",
    "seasonal":        "seasonal",
    "referrals":       "referrals",
    "tech":            "tech",
    "milestones":      "milestones",
    "parts":           "parts",
}

# Common aliases so callers don't have to remember the exact key
_ALIASES = {
    "appointment_reminders": "appointments",
    "wait":                  "wait_time",
    "declined_services":     "declined",
    "history":               "service_history",
    "estimate":              "estimates",
    "mpi":                   "inspection",
    "recalls":               "recall",
    "tools":                 "equipment",
    "sops":                  "sop",
    "expense":               "expenses",
    "referral":              "referrals",
    "productivity":          "tech",
    "technician":            "tech",
    "milestone":             "milestones",
    "inventory":             "parts",
    "parts_inventory":       "parts",
    "prices":                "service_prices",
    "price":                 "service_prices",
    "vehicle":               "vehicles",
    "cars":                  "vehicles",
}


@functools.lru_cache(maxsize=None)
def kb(module: str) -> dict:
    """
    Return the full knowledge-base dict for *module*.
    Results are cached in-process (lru_cache) after the first load.
    Returns {} if the module file is not found or fails to parse.
    """
    key = _ALIASES.get(module.lower(), module.lower())
    filename = _MODULE_FILES.get(key)
    if not filename:
        return {}
    path = os.path.join(_KB_DIR, f"{filename}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def kb_context(module: str, max_chars: int = 1200) -> str:
    """
    Return a compact, prompt-ready string summarising the module's KB data.
    Strips internal keys that start with '_' (metadata/description fields).
    Truncates to *max_chars* so it stays token-lean when injected into a prompt.
    """
    data = kb(module)
    if not data:
        return ""

    # Remove metadata keys
    clean = {k: v for k, v in data.items() if not k.startswith("_")}

    # Flatten to a compact string
    parts = []
    for key, value in clean.items():
        if isinstance(value, dict):
            inner = "; ".join(f"{k}: {v}" for k, v in list(value.items())[:8])
            parts.append(f"{key.upper()}: {inner}")
        elif isinstance(value, list):
            parts.append(f"{key.upper()}: {', '.join(str(i) for i in value[:8])}")
        else:
            parts.append(f"{key.upper()}: {value}")

    result = " | ".join(parts)
    if len(result) > max_chars:
        result = result[:max_chars].rsplit(" | ", 1)[0] + " | ..."
    return result


def kb_section(module: str, section: str):
    """
    Return a specific top-level section from a module's KB dict.
    Useful when only one part of the KB is needed (e.g. kb_section('sop', 'procedures')).
    Returns None if module or section is not found.
    """
    data = kb(module)
    return data.get(section)


def available_modules() -> list:
    """Return a sorted list of all loadable module keys."""
    return sorted(_MODULE_FILES.keys())


def reload(module: str = None):
    """
    Clear the lru_cache so files are re-read from disk.
    Pass a module name to reload one file (invalidates entire cache — Python limitation).
    Pass None to reload everything.
    """
    kb.cache_clear()
