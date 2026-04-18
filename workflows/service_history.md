# Module 5 — Vehicle Service History Report Generator

## Purpose
Generate a clean, branded, print-ready service history report for any customer vehicle. Shows every service on record, flags upcoming maintenance, and gives the customer a professional summary they can keep in the glove box or attach to a vehicle listing.

---

## Inputs Required

| Field | Required | Notes |
|-------|----------|-------|
| Customer name | Yes | First and last |
| Vehicle | Yes | Year, Make, Model (e.g. "2019 Toyota Camry") |
| Current mileage | Yes | Used to calculate upcoming services |
| VIN | Optional | Adds credibility; used for recall tie-in |
| Service records | Yes | See format below |

### Service Record Format
Accept records in any of these formats — the tool handles all of them:

**Semicolon-delimited (inline):**
```
01/15/2024, 62000, Oil & Filter Change, Mike T., $45, Synthetic 5W-30
04/20/2024, 64500, Front Brake Pads & Rotors, Dave R., $350, Replaced both sides
```

**JSON array (structured):**
```json
[
  {"date": "01/15/2024", "mileage": 62000, "service": "Oil & Filter Change", "tech": "Mike T.", "cost": 45, "notes": "Synthetic 5W-30"},
  {"date": "04/20/2024", "mileage": 64500, "service": "Front Brake Pads & Rotors", "tech": "Dave R.", "cost": 350, "notes": "Replaced both sides"}
]
```

Fields per record: `date`, `mileage`, `service`, `tech` (optional), `cost` (optional), `notes` (optional).

---

## Phase 1 — Load Context

**Step 1.** Load the shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 2.** Ask the user for the customer name and vehicle info:
> "Who is this report for? Give me: Customer name, vehicle year/make/model, current mileage, and VIN if you have it."

**Step 3.** Ask for the service records:
> "Paste in the service history — one record per line, or as a JSON list. Include: date, mileage, service performed, technician (optional), cost (optional), any notes (optional)."

Wait for the user to provide complete records before proceeding. Do not proceed with fabricated or estimated records.

---

## Phase 2 — Generate the Report

Once you have all inputs, run the tool:

```bash
python tools/service_history/generate_report.py \
    --customer "Sarah Mitchell" \
    --vehicle "2019 Toyota Camry SE" \
    --mileage 67000 \
    --vin "4T1B11HK9KU123456" \
    --records '[{"date":"01/15/2024","mileage":62000,"service":"Oil & Filter Change","tech":"Mike T.","cost":45,"notes":"Synthetic 5W-30"},{"date":"04/20/2024","mileage":64500,"service":"Front Brake Pads & Rotors","tech":"Dave R.","cost":350,"notes":"Replaced both sides"},{"date":"08/10/2024","mileage":66800,"service":"Tire Rotation & Balance","tech":"Mike T.","cost":35,"notes":"Torqued to spec"}]'
```

**If the user provides records as plain text (not JSON),** collect them and convert to JSON format before running the tool. Parse: date, mileage, service name, tech name, cost, notes.

**If a field is missing from a record** (e.g., no tech name or no cost), that's fine — pass an empty string. Do not fabricate values.

---

## Phase 3 — Review & Deliver

After the tool runs, confirm the output file was saved to `output/service_history/`.

Present a brief summary to the user:
```
✅ Service History Report complete.

Customer: Sarah Mitchell
Vehicle: 2019 Toyota Camry SE
Records documented: 3
Total services: $430.00
Last service: 08/10/2024
Next recommended: Oil & Filter Change (within ~1,200 miles)

Saved to: output/service_history/service_history_report.txt
```

Offer to:
- Display the full report inline
- Re-run with an updated record list (if the user wants to add or correct something)
- Generate an inspection form for this vehicle (Module 7)

---

## Decision Rules

**If records are incomplete or ambiguous:** Ask one clarifying question at a time. Do not guess dates or costs — leave the field blank rather than fabricating it.

**If the user only has paper records:** Ask them to read each one aloud (date, mileage, service, cost). You transcribe and pass to the tool.

**If VIN is not available:** Pass `--vin ""` — the report will omit that field gracefully.

**If the tool fails:** Log the error, try once more. If it fails again, tell the user and ask if they want the report generated manually.

**If the user wants to add records after the report is generated:** Re-run the tool with the full updated record list. The tool overwrites the previous file.

---

## Quality Standards

- Never fabricate service records, costs, dates, or technician names. Only include what the user provides.
- Upcoming service recommendations are based on standard mileage intervals — mark them as "General Guidance."
- If there is not enough mileage history to assess a system's status, mark it "Unable to Assess."
- The report must be formatted cleanly enough to hand directly to a customer or include in a vehicle listing packet.
- All dollar amounts must display with commas and two decimal places (e.g., $1,450.00).

---

## Input / Output Summary

| | Details |
|---|---|
| **Input** | Customer name, vehicle, mileage, VIN (optional), service records |
| **Tool** | `tools/service_history/generate_report.py` |
| **Output file** | `output/service_history/service_history_report.txt` |
| **Contents** | Shop header, customer/vehicle info, chronological service log, summary stats, upcoming services, shop footer |
