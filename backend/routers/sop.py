"""
Router: Module 10 — SOP Library
POST /api/sop/generate
"""
import os
import sys
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

_TOOLS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
if _TOOLS_ROOT not in sys.path:
    sys.path.insert(0, _TOOLS_ROOT)

from models.responses import ModuleResponse
from utils import capture_output, read_output_files

router = APIRouter()


class SopRequest(BaseModel):
    procedure: Optional[str] = ""      # built-in procedure key, or "all", or ""
    category: Optional[str] = ""       # unused currently, kept for future filtering
    title: Optional[str] = ""          # title for custom SOP
    custom: Optional[str] = ""         # free-form description for custom SOP
    custom_rules: Optional[str] = ""   # shop-specific additions


@router.post("/sop/generate", response_model=ModuleResponse)
def generate_sop(body: SopRequest):
    try:
        from sop import generate_sop as sop_module

        profile = sop_module.load_profile()
        shop_name = profile.get("shop_name", "Your Shop") or "Your Shop"

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "sop")
        )
        os.makedirs(output_dir, exist_ok=True)

        procedure = body.procedure or ""
        custom = body.custom or ""
        title = body.title or "Custom Procedure"
        custom_rules = body.custom_rules or ""

        def run():
            print(f"\nGenerating SOP")
            print()

            if custom:
                # Free-form custom SOP
                content = sop_module.render_custom_sop(custom, title, shop_name, custom_rules)
                safe_key = title.lower().replace(" ", "_").replace("/", "_")[:40]
                filename = f"sop_{safe_key}.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(content)
                print(f"  Saved output/sop/{filename}")
                print(f"\nDone - custom SOP saved.")

            elif procedure == "all":
                saved = []
                for key, proc in sop_module.PROCEDURES.items():
                    content = sop_module.render_sop(key, proc, shop_name, custom_rules)
                    filename = f"sop_{key}.txt"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, "w", encoding="utf-8") as fh:
                        fh.write(content)
                    saved.append(filename)
                    print(f"  Generated: {filename}")
                print(f"\nDone - {len(saved)} SOPs saved to output/sop/")

            elif procedure:
                # Resolve aliases
                key = sop_module.PROCESS_ALIASES.get(procedure, procedure)
                proc = sop_module.PROCEDURES.get(key)
                if not proc:
                    print(f"  Unknown procedure: {procedure}")
                    print(f"  Available: {', '.join(sop_module.PROCEDURES.keys())}")
                    return
                content = sop_module.render_sop(key, proc, shop_name, custom_rules)
                filename = f"sop_{key}.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(content)
                print(f"  Saved output/sop/{filename}")
                print(f"\nDone - SOP saved.")

            else:
                # List available procedures
                print("Available SOP procedures:")
                for key, proc in sop_module.PROCEDURES.items():
                    print(f"  {key:<25}  {proc['title']}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("sop")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
