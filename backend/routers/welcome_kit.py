"""
Router: Module 2 — Welcome Kit
POST /api/welcome-kit/generate
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


class WelcomeKitRequest(BaseModel):
    component: Optional[str] = "all"
    discount: Optional[str] = "10% off your next service visit — up to $50 in savings. Valid for 90 days."
    referral_offer: Optional[str] = "$25 off your next service for you, and $25 off for the friend you refer."
    service_performed: Optional[str] = ""


@router.post("/welcome-kit/generate", response_model=ModuleResponse)
def generate_welcome_kit(body: WelcomeKitRequest):
    try:
        from welcome_kit import generate_kit

        profile = generate_kit.load_profile()
        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "welcome_kit")
        )
        os.makedirs(output_dir, exist_ok=True)

        component = body.component or "all"
        discount = body.discount or "10% off your next service visit. Valid for 90 days."
        referral_offer = body.referral_offer or "$25 off for you and your referral."
        service_performed = body.service_performed or ""

        components = (
            generate_kit.COMPONENT_ORDER if component == "all" else [component]
        )

        def run():
            print(f"\nGenerating welcome kit components")
            print(f"   Shop : {generate_kit.pval(profile, 'shop_name', '[Not Set]')}")
            print()
            generated = []
            for name in components:
                content = generate_kit.build_component(
                    name, profile, discount, referral_offer, service_performed
                )
                if content is None:
                    print(f"  Unknown component: {name}")
                    continue
                filename = f"{name}.txt"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as fh:
                    fh.write(content)
                print(f"  Saved output/welcome_kit/{filename}")
                generated.append(filename)
            print(f"\nDone - {len(generated)} component(s) saved to output/welcome_kit/")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("welcome_kit")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
