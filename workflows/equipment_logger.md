# Equipment Maintenance & Calibration Logger — Workflow SOP
## Module 9 | Shop Command Center

**Purpose:** Track all shop equipment with purchase dates, maintenance schedules, calibration intervals, and service history. Generate maintenance alerts and formal compliance reports ready for insurance or regulatory review.

---

## Inputs Required

| Field | Required | Notes |
|-------|----------|-------|
| Equipment name | Yes (add) | e.g., "BendPak 2-Post Lift" |
| Equipment type | Yes (add) | e.g., Vehicle Lift, Tire Machine, Scan Tool |
| Equipment ID | Yes (update/maintenance) | Unique ID assigned at add |
| Purchase date | Recommended | YYYY-MM-DD format |
| Last service date | Recommended | YYYY-MM-DD format |
| Maintenance interval | Recommended | Number of days between services |
| Next service date | Optional | Auto-calculated if interval + last service provided |

## Outputs Produced

| File | Location | Description |
|------|----------|-------------|
| `data/equipment_log.json` | `data/` | Live equipment database |
| `equipment_status_report.txt` | `output/equipment/` | Full status report with overdue flags |
| `maintenance_alerts.txt` | `output/equipment/` | Alert-focused report for daily review |

---

## Phase 1 — Load Context

### Step 1: Load shop profile
```bash
python tools/shared/load_profile.py
```

### Step 2: Determine starting point
Ask the user:
- "Do you have existing equipment to log, or are we building from scratch?"
- "I can walk you through each piece of equipment one at a time, or you can describe them all and I'll run the commands."

Common shop equipment categories to cover:
- Vehicle lifts (2-post, 4-post, scissor)
- Tire equipment (tire machine, balancer)
- Alignment rack
- Scan tools / diagnostic equipment
- Air compressor
- Fluid exchange machines (oil drain, coolant flush, transmission)
- Battery charger / load tester
- Brake lathe
- Welding equipment
- Lifts / jacks / jack stands

---

## Phase 2 — Add Equipment

### Add a new piece of equipment
```bash
python tools/equipment/log_equipment.py \
    --action add \
    --name "BendPak 2-Post Lift" \
    --type "Vehicle Lift" \
    --equipment_id "LIFT-001" \
    --purchase_date "2022-03-15" \
    --last_service "2024-01-15" \
    --next_service "2024-04-15" \
    --notes "90-day lubrication and inspection schedule. Serial: BP-2024-1234"
```

### Update an existing record
```bash
python tools/equipment/log_equipment.py \
    --action update \
    --equipment_id "LIFT-001" \
    --last_service "2024-10-15" \
    --next_service "2025-01-15" \
    --notes "Replaced hydraulic seals. Passed annual inspection."
```

### Log a maintenance event
```bash
python tools/equipment/log_equipment.py \
    --action log_maintenance \
    --equipment_id "LIFT-001" \
    --notes "Lubricated all pivot points. Inspected cables. No issues found." \
    --last_service "2024-10-15" \
    --next_service "2025-01-15"
```

### List all equipment
```bash
python tools/equipment/log_equipment.py --action list
```

### Generate full status report
```bash
python tools/equipment/log_equipment.py --action generate_report
```

---

## Phase 3 — Generate Alerts & Reports

The `generate_report` action produces a full Equipment Status Report saved to `output/equipment/`.

The report includes:
- Complete equipment list with status (current / upcoming / overdue)
- Overdue items flagged with days past due
- Items due within 30 days highlighted
- Maintenance history summary per piece of equipment
- Compliance-ready format (suitable for insurance or regulatory review)

### Run generate_alerts.py for a focused alert view
```bash
# Default: 90-day horizon
python tools/equipment/generate_alerts.py

# Tighter horizon (30 days)
python tools/equipment/generate_alerts.py --horizon 30
```

---

## Phase 4 — Review & Act

After generating the report:
1. Present overdue items first — ask if the user wants to schedule maintenance now.
2. Present upcoming items (within 30 days) — flag on the shop calendar.
3. Ask if any equipment was recently serviced and needs the log updated.

**Edge Case — Equipment just serviced, no next date known:**
Use the maintenance interval from the previous record to calculate the next service date. Ask the user to confirm.

**Edge Case — New equipment with no service history:**
Add it with today as the `last_service` date and calculate `next_service` based on the manufacturer's recommended interval. Note in `--notes` that this is a new-equipment baseline.

**Edge Case — Calibration-required equipment (scan tools, alignment racks):**
Use the `--notes` field to track calibration dates and intervals until a dedicated calibration field is added. Format: `"Calibration due: 2025-06-01. Annual interval."`

---

## Quality Standards

- **Dates must be exact** — YYYY-MM-DD format only. No approximations.
- **Overdue items must be flagged prominently** with days past due.
- **The compliance report** must read as a professional document — shop name, date, formatted table.
- **All equipment must have a next service date** before the record is saved. If unknown, estimate and flag it with a note.
- **Maintenance history** must be preserved — never overwrite, always append.
- **Equipment IDs** should be consistent: LIFT-001, TIRE-001, SCAN-001, COMP-001, etc.

---

## Decision Rules

| Situation | Action |
|-----------|--------|
| No equipment in log | Walk user through adding each item; suggest common shop equipment list |
| Equipment overdue | Flag clearly, ask if they want to schedule and log maintenance now |
| No next service date provided | Calculate from last_service + interval; confirm with user |
| Equipment out of service | Update notes; mark status as OUT-OF-SERVICE in notes field |
| User wants to delete equipment | Use `--action update --notes "RETIRED: [date] [reason]"` instead of deleting — preserves history |
| Calibration tracking needed | Use notes field: "CAL DUE: YYYY-MM-DD" until dedicated field added |
