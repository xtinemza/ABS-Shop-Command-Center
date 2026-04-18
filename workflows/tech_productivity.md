# Technician Productivity & Labor Summary — Workflow
## Module 16 | Shop Command Center

**Purpose:** Generate daily, weekly, or monthly reports showing per-technician efficiency rates, revenue per hour, comeback rates, and flagged performance issues. Designed as a management tool — framed constructively, not punitively.

---

## Input / Output Summary

| Input | Source |
|-------|--------|
| Period (day/week/month) | User selects |
| Date or week | User provides |
| Per-technician data | User provides |

**Required data per technician:**
| Field | Description |
|-------|-------------|
| Name | Technician name |
| Hours clocked | Total hours on the clock |
| Hours billed | Labor hours billed to customers |
| Jobs completed | Number of jobs/repair orders finished |
| Revenue generated | Total labor revenue attributed to this tech |
| Comebacks | Jobs that came back for re-repair |

| Output | Location |
|--------|----------|
| Individual tech data (JSON) | `data/tech_data.json` |
| Productivity report | `output/tech_productivity/productivity_report_[period].txt` |

---

## Phase 1 — Load Context

**Step 1.1** — Load shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 1.2** — Ask the user:
> What period does this report cover?
> - **day** — a single day
> - **week** — a full work week
> - **month** — a calendar month

**Step 1.3** — Ask for the specific date or period:
> What date or week are we reporting? (e.g., "April 14, 2025" or "week of April 7")

---

## Phase 2 — Collect Technician Data

Ask for the technician roster and data. Accept any format — the user may provide it as a list, table, or one tech at a time.

For each technician, collect:
- Name
- Hours clocked (time on the clock)
- Hours billed (labor hours on customer invoices)
- Jobs completed (number of repair orders)
- Revenue generated (total billed labor dollars)
- Comebacks (0 if none)

**Step 2.1** — Pass all technicians at once using JSON format:

```bash
python tools/tech_productivity/generate_summary.py \
    --period week \
    --date "2025-04-14" \
    --technicians '[
        {"name": "Mike R.", "hours_clocked": 40, "hours_billed": 44.5,
         "jobs_completed": 22, "revenue_generated": 9200, "comebacks": 1},
        {"name": "Sara T.", "hours_clocked": 38, "hours_billed": 35.0,
         "jobs_completed": 18, "revenue_generated": 7400, "comebacks": 0},
        {"name": "Dave K.", "hours_clocked": 40, "hours_billed": 41.0,
         "jobs_completed": 20, "revenue_generated": 8500, "comebacks": 2}
    ]'
```

**Step 2.2** — Alternatively, add technicians one at a time and compile:

```bash
# Add each tech (saved to data/tech_data.json)
python tools/tech_productivity/generate_summary.py \
    --period week --date "2025-04-14" \
    --tech "Mike R." --hours_clocked 40 --hours_billed 44.5 \
    --jobs_completed 22 --revenue_generated 9200 --comebacks 1

# Compile into final report
python tools/tech_productivity/generate_summary.py \
    --period week --date "2025-04-14" --compile
```

---

## Phase 3 — Review and Deliver

Display the full report. Point out:
- Top performer for the period
- Any techs flagged for low efficiency (below 80%)
- Any comebacks above 5% comeback rate
- Shop-wide totals and averages

Ask: "Would you like to save this report and move on, or discuss any of these numbers?"

---

## Edge Case Rules

**If efficiency is above 100%:** Normal. This means the tech billed more than they clocked (flat-rate billing). Flag for informational purposes only — not a problem.

**If hours_billed is 0:** Flag as incomplete data. Do not include in efficiency calculations. Note it in the report.

**If comebacks are high (above 5% of jobs):** Flag in red. Note the specific tech and suggest reviewing their recent work orders — do not assume fault.

**If the user can't provide all fields:** Note what's missing. Generate a partial report with available data. Flag the missing fields clearly.

**If data for a previous period exists:** Show week-over-week or month-over-month comparison when the same technicians appear in both periods.

---

## Performance Benchmarks

| Metric | Target | Flag if Below |
|--------|--------|--------------|
| Efficiency (billed/clocked) | 90–110% | Flag below 80% |
| Revenue per billed hour | $65–$120+ | Varies by shop rate |
| Comeback rate | < 3% | Flag above 5% |
| Jobs per day (8-hr shift) | 3–5 typical | Context-dependent |

---

## Quality Standards

- Never fabricate numbers. If data is missing or incomplete, note it explicitly.
- Frame findings constructively — this is a management tool, not a disciplinary record.
- Efficiency above 100% is a positive signal, not a data error.
- All times are in hours (decimal). 40.5 = 40 hours 30 minutes.
- The report must show shop totals and averages, not just individual stats.
- Reports save to `output/tech_productivity/` with a period-specific filename.
