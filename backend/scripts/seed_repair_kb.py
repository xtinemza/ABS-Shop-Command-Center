"""
Seed the repair_knowledge table in Supabase with embeddings from:
  - backend/knowledge_base/obd_codes.json  (all P/C/B/U codes)
  - vehicles knowledge base (known issues per vehicle)

Usage:
  python backend/scripts/seed_repair_kb.py

Requirements:
  - GEMINI_API_KEY in environment (or backend/.env)
  - SUPABASE_URL and SUPABASE_KEY (service role key) in environment

The script is idempotent: it checks for existing entries by obd_code
or vehicle_make+model+content hash before inserting.
"""

import json
import os
import sys
import hashlib
import time

# Allow imports from backend/
_SCRIPT_DIR = os.path.dirname(__file__)
_BACKEND_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, ".."))
sys.path.insert(0, _BACKEND_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_BACKEND_DIR, ".env"))
except ImportError:
    pass

from kb_loader import kb


def get_embedding(genai, text: str) -> list:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
    )
    return result["embedding"]


def build_obd_text(code: str, data: dict) -> str:
    causes = ", ".join(data.get("causes", []))
    tests  = ", ".join(data.get("tests", []))
    symptoms = ", ".join(data.get("symptoms", []))
    return (
        f"OBD Code {code}: {data.get('name', '')}\n"
        f"System: {data.get('system', '')}\n"
        f"Symptoms: {symptoms}\n"
        f"Common causes: {causes}\n"
        f"Diagnostic tests: {tests}\n"
        f"Advisor summary: {data.get('advisor_summary', '')}"
    )


def build_vehicle_text(key: str, data: dict) -> str:
    issues = data.get("common_issues") or data.get("known_issues") or []
    if not issues:
        return ""
    issues_str = "; ".join(str(i) for i in issues[:8])
    engine = data.get("engine") or data.get("engines") or ""
    return (
        f"Vehicle: {key}\n"
        f"Engine: {engine}\n"
        f"Known issues: {issues_str}"
    )


def content_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def seed():
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set.")
        sys.exit(1)

    genai.configure(api_key=api_key)

    from supabase_client import supabase

    print("=== Repair Knowledge Seeder ===\n")

    # ── 1. OBD codes ──────────────────────────────────────────────────────────
    obd_kb = kb("obd_codes")
    if obd_kb:
        print(f"Found {len(obd_kb)} OBD codes. Seeding...")
        inserted = 0
        skipped  = 0
        for code, data in obd_kb.items():
            if code.startswith("_"):
                continue
            # Check if already seeded
            existing = supabase.table("repair_knowledge") \
                .select("id") \
                .eq("obd_code", code) \
                .limit(1) \
                .execute()
            if existing.data:
                skipped += 1
                continue

            text = build_obd_text(code, data)
            try:
                embedding = get_embedding(genai, text)
            except Exception as e:
                print(f"  ⚠ Embedding failed for {code}: {e}")
                time.sleep(2)
                continue

            row = {
                "source_type":  "obd_code",
                "obd_code":     code,
                "vehicle_make": None,
                "vehicle_model": None,
                "content":      text,
                "metadata": {
                    "severity": data.get("severity"),
                    "system":   data.get("system"),
                    "makes":    data.get("makes"),
                },
                "embedding": embedding,
            }
            supabase.table("repair_knowledge").insert(row).execute()
            inserted += 1
            print(f"  ✓ {code} — {data.get('name', '')[:50]}")
            time.sleep(0.1)  # stay within free-tier embedding rate limits

        print(f"\nOBD codes: {inserted} inserted, {skipped} skipped (already exist)\n")
    else:
        print("No OBD KB found — skipping OBD codes.\n")

    # ── 2. Vehicle known issues ────────────────────────────────────────────────
    vehicles_kb = kb("vehicles")
    if vehicles_kb:
        print(f"Found {len(vehicles_kb)} vehicle entries. Seeding known issues...")
        inserted = 0
        skipped  = 0
        for veh_key, data in vehicles_kb.items():
            if veh_key.startswith("_") or not isinstance(data, dict):
                continue
            text = build_vehicle_text(veh_key, data)
            if not text:
                continue

            chash = content_hash(text)
            existing = supabase.table("repair_knowledge") \
                .select("id") \
                .eq("source_type", "vehicle_issue") \
                .eq("metadata->>content_hash", chash) \
                .limit(1) \
                .execute()
            if existing.data:
                skipped += 1
                continue

            parts = veh_key.split(" ", 1)
            make  = parts[0] if parts else ""
            model = parts[1] if len(parts) > 1 else ""

            try:
                embedding = get_embedding(genai, text)
            except Exception as e:
                print(f"  ⚠ Embedding failed for {veh_key}: {e}")
                time.sleep(2)
                continue

            row = {
                "source_type":   "vehicle_issue",
                "obd_code":      None,
                "vehicle_make":  make,
                "vehicle_model": model,
                "content":       text,
                "metadata":      {"content_hash": chash},
                "embedding":     embedding,
            }
            supabase.table("repair_knowledge").insert(row).execute()
            inserted += 1
            print(f"  ✓ {veh_key}")
            time.sleep(0.1)

        print(f"\nVehicle issues: {inserted} inserted, {skipped} skipped\n")
    else:
        print("No vehicles KB found — skipping vehicle issues.\n")

    print("=== Seeding complete ===")


if __name__ == "__main__":
    seed()
