"""
Router: Module 13 — Expense Reports
POST /api/expenses/log     — acknowledge an expense log entry
POST /api/expenses/report  — Gemini generates expense analysis and trend report
"""
import os, sys
from typing import Optional
from fastapi import APIRouter, Depends
from auth import get_current_user
from pydantic import BaseModel

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from models.responses import ModuleResponse
from gemini_client import load_profile, get_gemini, call_gemini, shop_context

router = APIRouter()

EXPENSE_CATEGORIES = [
    "parts", "labor", "rent", "utilities", "insurance", "marketing",
    "tools", "training", "equipment", "office_supplies", "taxes",
    "professional_services", "vehicle", "miscellaneous",
]


class ExpenseLogRequest(BaseModel):
    action:         Optional[str]   = "add"
    date:           Optional[str]   = ""
    amount:         Optional[float] = 0.0
    vendor:         Optional[str]   = ""
    description:    Optional[str]   = ""
    category:       Optional[str]   = "miscellaneous"
    payment_method: Optional[str]   = ""
    receipt_ref:    Optional[str]   = ""
    month:          Optional[str]   = ""
    expense_data:   Optional[str]   = ""   # paste of expense records for report generation
    period:         Optional[str]   = "month"
    revenue:        Optional[str]   = ""   # optional revenue figure for ratio analysis
    year:           Optional[int]   = None
    format:         Optional[str]   = "summary"


@router.post("/expenses/log", response_model=ModuleResponse)
def log_expense(body: ExpenseLogRequest, user=Depends(get_current_user)):
    """Acknowledge expense entry. Actual persistence is handled by the frontend/Supabase."""
    try:
        action = (body.action or "add").strip()
        amount = body.amount or 0.0
        desc   = (body.description or "").strip()
        cat    = (body.category or "miscellaneous").strip()
        vendor = (body.vendor or "").strip()
        date   = (body.date or "").strip()

        if action == "add":
            if not desc and not amount:
                return ModuleResponse(success=False, output="", files=[],
                                      error="Please provide amount and description.")
            msg = f"Expense logged: ${amount:,.2f} — {cat}"
            if vendor: msg += f" | {vendor}"
            if date:   msg += f" | {date}"
            if desc:   msg += f"\n{desc}"
            return ModuleResponse(success=True, output=msg, files=[], content={}, error=None)

        return ModuleResponse(success=True, output=f"Expense action '{action}' processed.",
                              files=[], content={}, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/expenses/report", response_model=ModuleResponse)
def expense_report(body: ExpenseLogRequest, user=Depends(get_current_user)):
    try:
        profile   = load_profile(user.id)
        ctx       = shop_context(profile)
        shop_name = profile.get("shop_name") or "our shop"

        expense_data = (body.expense_data or "").strip()
        period       = (body.period or "month").strip()
        revenue      = (body.revenue or "").strip()
        month        = (body.month or "").strip()

        if not expense_data:
            return ModuleResponse(success=False, output="", files=[],
                                  error="Please provide expense data to generate a report.")

        client, err = get_gemini()
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        period_label = month or period

        system = (
            f"You generate expense analysis reports for the owner of an independent auto repair shop.\n"
            f"{ctx}\n\n"
            f"RULES:\n"
            f"- Be analytical and direct — this is an internal financial report\n"
            f"- Calculate category totals and percentages of total spend\n"
            f"- Flag any category that looks unusually high vs. industry norms\n"
            f"- Provide 2–3 specific, actionable cost-reduction suggestions\n"
            f"- If revenue is provided, calculate key expense-to-revenue ratios\n"
            f"- Typical benchmarks: parts ~40%, labor overhead ~20%, rent ~8–12%, "
            f"marketing ~3–5%, insurance ~3–5%\n"
            f"- Shop: {shop_name}\n"
        )

        prompt = (
            f"Generate an expense analysis report for {shop_name}.\n"
            f"Period: {period_label}\n"
            + (f"Revenue this period: {revenue}\n" if revenue else "")
            + f"\nExpense data:\n{expense_data}\n\n"
            + "Structure:\n"
            + "## EXPENSE REPORT — [PERIOD]\n"
            + "## CATEGORY BREAKDOWN (category | amount | % of total)\n"
            + "## TOP SPENDING AREAS\n"
            + (f"## EXPENSE-TO-REVENUE RATIOS\n" if revenue else "")
            + "## FLAGS & ANOMALIES\n"
            + "## COST REDUCTION OPPORTUNITIES\n"
            + "## TREND NOTES (if multiple months of data provided)"
        )

        text, err = call_gemini(client, system, prompt, max_tokens=1400)
        if err:
            return ModuleResponse(success=False, output="", files=[], error=err)

        safe_period = period_label.replace(" ", "_").replace("/", "-") or period
        filename    = f"expense_report_{safe_period}.txt"
        content_map = {filename: text}
        output_log  = f"Generated expense report: {period_label}"

        return ModuleResponse(success=True, output=output_log, files=[filename],
                              content=content_map, error=None)

    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
