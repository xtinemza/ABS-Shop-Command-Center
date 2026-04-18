"""
Router: Module 13 — Expense Reports
POST /api/expenses/log
POST /api/expenses/report
"""
import argparse
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


class ExpenseLogRequest(BaseModel):
    action: Optional[str] = "add"        # add, list, summary
    date: Optional[str] = ""
    amount: Optional[float] = 0.0
    vendor: Optional[str] = ""
    description: Optional[str] = ""
    category: Optional[str] = "miscellaneous"
    payment_method: Optional[str] = ""
    receipt_ref: Optional[str] = ""
    month: Optional[str] = ""            # YYYY-MM filter for list/summary


class ExpenseReportRequest(BaseModel):
    period: Optional[str] = "month"     # month, year
    month: Optional[int] = None
    year: Optional[int] = None
    format: Optional[str] = "summary"  # summary, detailed


@router.post("/expenses/log", response_model=ModuleResponse)
def log_expense(body: ExpenseLogRequest):
    try:
        from expenses import categorize_expenses
        from datetime import datetime

        expenses = categorize_expenses.load_expenses()
        today = datetime.now().strftime("%Y-%m-%d")

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "expenses")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            action=body.action or "add",
            date=body.date or today,
            amount=body.amount or 0.0,
            vendor=body.vendor or "",
            description=body.description or "",
            category=body.category or "miscellaneous",
            payment_method=body.payment_method or "",
            receipt_ref=body.receipt_ref or "",
            month=body.month or "",
        )

        def run():
            action = args.action
            print(f"\nExpense action: {action}")
            print()

            if action == "add":
                if not args.amount or not args.description:
                    print("  ERROR: amount and description are required for add action.")
                    return

                entry_date = args.date or today
                entry = {
                    "date": entry_date,
                    "amount": round(args.amount, 2),
                    "vendor": args.vendor,
                    "description": args.description,
                    "category": args.category,
                    "payment_method": args.payment_method,
                    "receipt_ref": args.receipt_ref,
                    "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                expenses.append(entry)
                categorize_expenses.save_expenses(expenses)
                month_prefix = entry_date[:7]
                month_total = sum(e["amount"] for e in expenses if e["date"].startswith(month_prefix))
                print(f"  Expense logged: ${args.amount:,.2f} — {args.category}")
                print(f"  Date: {entry_date} | Vendor: {args.vendor or '(not specified)'}")
                print(f"  Description: {args.description}")
                print(f"  Month-to-date ({month_prefix}): ${month_total:,.2f}")

            elif action == "list":
                if not expenses:
                    print("  No expenses on file.")
                    return
                month_filter = args.month or ""
                if month_filter:
                    display = [e for e in expenses if e["date"].startswith(month_filter)]
                    print(f"  {len(display)} expenses for {month_filter}")
                else:
                    display = expenses
                    print(f"  {len(display)} total expenses")
                for e in sorted(display, key=lambda x: x["date"], reverse=True)[:20]:
                    print(f"  {e['date']}  ${e['amount']:>8,.2f}  [{e['category']:<20}]  {e['description'][:40]}")

            elif action == "summary":
                month_filter = args.month or ""
                if month_filter:
                    display = [e for e in expenses if e["date"].startswith(month_filter)]
                    period_label = month_filter
                else:
                    display = expenses
                    period_label = "All time"
                total = sum(e["amount"] for e in display)
                from collections import defaultdict
                by_cat = defaultdict(float)
                for e in display:
                    by_cat[e["category"]] += e["amount"]
                print(f"  Expense Summary — {period_label}")
                print(f"  {'─' * 40}")
                for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
                    pct = (amt / total * 100) if total else 0
                    print(f"  {cat:<22}  ${amt:>9,.2f}  ({pct:.1f}%)")
                print(f"  {'─' * 40}")
                print(f"  {'TOTAL':<22}  ${total:>9,.2f}")

            else:
                print(f"  Unknown action: {action}")

        stdout, error = capture_output(run)
        file_paths, content_map = read_output_files("expenses")

        return ModuleResponse(
            success=error is None,
            output=stdout,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))


@router.post("/expenses/report", response_model=ModuleResponse)
def expense_report(body: ExpenseReportRequest):
    try:
        from expenses import generate_expense_report
        from datetime import datetime

        now = datetime.now()

        output_dir = os.path.abspath(
            os.path.join(_TOOLS_ROOT, "..", "output", "expenses")
        )
        os.makedirs(output_dir, exist_ok=True)

        args = argparse.Namespace(
            period=body.period or "month",
            month=body.month or now.month,
            year=body.year or now.year,
            format=body.format or "summary",
            revenue=None,
        )

        old_argv = sys.argv
        stdout_buf = ""
        error = None
        try:
            sys.argv = [
                "generate_expense_report.py",
                "--period", args.period,
                "--month", str(args.month),
                "--year", str(args.year),
                "--format", args.format,
            ]
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    generate_expense_report.main()
                except SystemExit:
                    pass
            stdout_buf = buf.getvalue()
        except Exception as exc:
            error = str(exc)
        finally:
            sys.argv = old_argv

        file_paths, content_map = read_output_files("expenses")

        return ModuleResponse(
            success=error is None,
            output=stdout_buf,
            files=file_paths,
            content=content_map,
            error=error,
        )
    except Exception as exc:
        return ModuleResponse(success=False, output="", files=[], error=str(exc))
