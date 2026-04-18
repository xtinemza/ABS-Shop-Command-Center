# Shop Expense Categorization & Reporting — Workflow
## Module 13 | Shop Command Center

**Purpose:** Log and categorize shop expenses, generate monthly and annual reports with category breakdowns, vendor summaries, trend comparisons, and expense-to-revenue ratios for bookkeeping and financial review.

---

## Input / Output Summary

| Input | Source |
|-------|--------|
| Expense entries (date, amount, vendor, description, category) | User provides |
| Optional revenue figure for ratio calculation | User provides |
| Report period (month/quarter/year) | User selects |

| Output | Location |
|--------|----------|
| Expense database | `data/expenses.json` |
| Expense report (text) | `output/expenses/expense_report_[period].txt` |

---

## Standard Expense Categories

| Category | Examples |
|----------|---------|
| `parts` | Bulk part orders, individual parts for jobs |
| `labor` | Payroll, subcontracted labor |
| `rent` | Shop rent/lease payments |
| `utilities` | Electric, gas, water, internet, phone |
| `insurance` | Liability, property, workers comp |
| `marketing` | Advertising, postage, website, social ads |
| `tools_equipment` | New tools, equipment purchases or leases |
| `training` | Certifications, courses, trade shows |
| `waste_disposal` | Oil recycling, hazmat disposal |
| `office_supplies` | Paper, ink, forms, software subscriptions |
| `vehicle_fleet` | Shop vehicles, registration, fuel |
| `licenses_permits` | Business license, EPA permits, inspection licenses |
| `professional_services` | Accountant, attorney, consultant fees |
| `miscellaneous` | Anything that doesn't fit above |

---

## Phase 1 — Load Context

**Step 1.1** — Load shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 1.2** — Ask the user:
> What expense work do you need today?
> - **A** — Log one or more expenses
> - **B** — List recent expenses
> - **C** — Generate an expense report

**Step 1.3** — If logging expenses, ask:
> Do you have revenue data to include? (Optional — used for expense-to-revenue ratio)
> If yes, collect total revenue for the period.

---

## Phase 2A — Log Expenses

Accept expenses in any format: typed list, CSV-style, or one at a time. For each expense, collect:

| Field | Required? |
|-------|-----------|
| Date | Yes (YYYY-MM-DD) |
| Amount | Yes |
| Vendor | Recommended |
| Description | Yes |
| Category | Yes (see table above) |
| Payment method | Optional |
| Receipt reference | Optional |

Run for each expense:
```bash
python tools/expenses/categorize_expenses.py \
    --action add \
    --date "2025-04-02" \
    --amount 847.50 \
    --vendor "AutoZone Commercial" \
    --description "Brake pads and rotors bulk order" \
    --category parts \
    --payment_method "Business Visa" \
    --receipt_ref "AZ-INV-88234"
```

If the user provides multiple expenses at once, log each with a separate command.

**Category Assistance:** If the user is unsure of a category, suggest the most appropriate one based on the description. Use the category table as your guide. Never leave a category blank.

---

## Phase 2B — List Recent Expenses

```bash
python tools/expenses/categorize_expenses.py --action list
```

Optionally filter by month:
```bash
python tools/expenses/categorize_expenses.py --action list --month "2025-04"
```

---

## Phase 2C — Generate Expense Report

Ask the user:
1. **Period**: month, quarter, or year
2. **Month/Year**: which specific period (default to current)
3. **Revenue** (optional): total revenue for the period

**Monthly report:**
```bash
python tools/expenses/generate_expense_report.py \
    --period month \
    --month 4 \
    --year 2025 \
    --format detailed
```

**Annual report:**
```bash
python tools/expenses/generate_expense_report.py \
    --period year \
    --year 2025 \
    --format summary
```

With revenue for ratio calculation:
```bash
python tools/expenses/generate_expense_report.py \
    --period month \
    --month 4 \
    --year 2025 \
    --revenue 52000 \
    --format detailed
```

---

## Phase 3 — Confirm and Summarize

After logging:
- Confirm each entry with amount, category, and vendor
- Mention the running total for the month

After generating a report:
- Display the report inline
- State the file path where it was saved
- Highlight any categories that are unusually high (over 30% of total spend)

---

## Edge Case Rules

**If the user provides a CSV or list:** Process each row as a separate `add` command. Confirm the count at the end ("Logged 7 expenses totaling $X").

**If the category is unclear:** Suggest the best match and confirm before logging. Don't guess silently.

**If revenue is not provided:** Skip the expense-to-revenue ratio. Do not estimate or fabricate revenue figures.

**If only one month of data exists:** Skip trend/comparison section in the report. Note that trend analysis requires at least two months of data.

**If an expense seems unusually high:** Flag it in the summary with a note ("This is larger than typical — verify this entry").

**If the user wants to correct an entry:** Use `--action list` to find the entry, then advise them to add a correcting entry (negative amount) for the same date and category.

---

## Quality Standards

- Categories must be consistent. The same type of recurring expense (e.g., electric bill) must always use the same category.
- Never estimate or fill in missing financial figures. Mark unknown amounts as requiring verification.
- Reports must include: category totals with percentages, top vendors, and month-over-month trend when data allows.
- All outputs save to `output/expenses/` with a descriptive filename including the period.
- The report should be ready for handoff to a bookkeeper — no cleanup required.
