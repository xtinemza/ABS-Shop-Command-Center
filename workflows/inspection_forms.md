# Module 7 — Vehicle Intake & Inspection Forms

## Purpose
Two-mode module: generate a blank technician inspection checklist (print and fill out in the shop), or take completed inspection results and produce a formatted, color-coded customer report. The customer report is plain-language, ready to hand over at vehicle delivery or email.

---

## Two Modes

| Mode | Command Flag | What It Does |
|------|-------------|--------------|
| **Blank Form** | `--mode form` | Generates a printable multi-point inspection checklist with all sections and rating boxes |
| **Completed Report** | `--mode report` | Takes inspection results as JSON and generates a customer-facing report with status indicators |

---

## Inputs Required

### Mode: `form` (blank checklist)

| Field | Required | Notes |
|-------|----------|-------|
| Vehicle | Optional | Pre-fills the vehicle line on the form |
| Customer | Optional | Pre-fills the customer name line |
| Mileage | Optional | Pre-fills the mileage line |
| Inspection type | Optional | `multi_point` (default), `pre_purchase`, or `seasonal` |

### Mode: `report` (completed inspection)

| Field | Required | Notes |
|-------|----------|-------|
| Customer | Yes | Name for the report header |
| Vehicle | Yes | Year, Make, Model |
| Mileage | Yes | Mileage at time of inspection |
| Results | Yes | JSON array of inspection findings — see format below |

### Results JSON Format

```json
[
  {
    "category": "Brakes",
    "item": "Front brake pads",
    "status": "needs_attention",
    "notes": "2mm remaining, replace within 3,000 miles"
  },
  {
    "category": "Brakes",
    "item": "Front rotors",
    "status": "needs_attention",
    "notes": "Light scoring visible"
  },
  {
    "category": "Tires & Wheels",
    "item": "Front left tread depth",
    "status": "good",
    "notes": "7/32\""
  },
  {
    "category": "Fluids",
    "item": "Engine oil level & condition",
    "status": "fair",
    "notes": "Dark, due for change at 67,500 miles"
  },
  {
    "category": "Battery & Electrical",
    "item": "Battery voltage",
    "status": "urgent",
    "notes": "Load test: 285 CCA, rated 550 CCA — replace"
  }
]
```

**Status values:**
- `good` → ✅ GOOD
- `fair` → ⚠️ FAIR
- `needs_attention` → 🔴 NEEDS ATTENTION
- `urgent` → 🚨 URGENT

---

## Phase 1 — Load Context

**Step 1.** Load the shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 2.** Ask the user which mode they need:
> "Are you generating a blank inspection form for your technicians, or a completed inspection report for a customer?"

**Step 3 (form mode).** Ask for vehicle/customer info (optional) and inspection type (multi-point, pre-purchase, or seasonal).

**Step 3 (report mode).** Ask for customer name, vehicle, mileage, and the completed inspection results. Accept results as plain text (you'll convert to JSON) or directly as JSON.

---

## Phase 2 — Generate Form or Report

### Form Mode

```bash
python tools/inspection/generate_forms.py \
    --mode form \
    --customer "Sarah Mitchell" \
    --vehicle "2019 Toyota Camry SE" \
    --mileage 67000 \
    --type multi_point
```

Other inspection types:
```bash
--type pre_purchase
--type seasonal
```

### Report Mode

```bash
python tools/inspection/generate_forms.py \
    --mode report \
    --customer "David Chen" \
    --vehicle "2017 Honda CR-V" \
    --mileage 84200 \
    --results '[{"category":"Brakes","item":"Front brake pads","status":"needs_attention","notes":"2mm remaining"},{"category":"Tires & Wheels","item":"Front left tread depth","status":"good","notes":"7/32 inch"},{"category":"Fluids","item":"Engine oil","status":"fair","notes":"Dark, due for change"},{"category":"Battery & Electrical","item":"Battery voltage","status":"urgent","notes":"285 CCA vs 550 rated"}]'
```

**If the user provides inspection results as plain text** (e.g., reading from a paper form), convert them to the JSON format above before running the tool. Confirm category, item, status, and notes for each entry.

---

## Phase 3 — Review & Deliver

After the tool runs, confirm the output file(s):

**Form mode:**
```
✅ Inspection Form generated.

Type: Multi-Point Vehicle Inspection
Vehicle pre-filled: 2019 Toyota Camry SE
Sections: 10 | Total inspection points: 52

Saved to: output/inspection/multi_point_form.txt
Ready to print and use.
```

**Report mode:**
```
✅ Inspection Report generated.

Customer: David Chen
Vehicle: 2017 Honda CR-V | 84,200 miles
Results summary:
  ✅ GOOD:            18 items
  ⚠️  FAIR:            2 items
  🔴 NEEDS ATTENTION:  2 items
  🚨 URGENT:           1 item

Saved to: output/inspection/inspection_report.txt
```

Offer to:
- Display the report inline
- Generate an estimate narration for the items needing attention (Module 6)
- Re-run with corrected results

---

## Workflow: Form → Report (Full Inspection Flow)

The typical shop flow:
1. **Before the vehicle arrives**: Run `--mode form` to print the checklist.
2. **Technician inspects the vehicle**: Fills in the paper or digital form.
3. **Advisor enters results**: Runs `--mode report` with the completed findings.
4. **Advisor hands report to customer**: Along with or before presenting the estimate.
5. **Optional**: Run Module 6 (Estimate Narrator) to translate any repair recommendations.

---

## Decision Rules

**If the user provides results as plain text:** Ask them to read the results by category. Convert each to a JSON entry before running. Confirm status for any items that are ambiguous.

**If status is ambiguous** (e.g., user says "the tires are okay but a little worn"): Map to `fair` and note that in the entry.

**If an inspection item was not checked:** Omit it from the results JSON or set status to `not_inspected`. The tool will handle it gracefully.

**If the tool fails:** Try once more. If it fails again, offer to generate the form manually in plain text.

**If the user wants a custom inspection category:** Add it to the results JSON under a custom category name — the tool will include it.

---

## Quality Standards

- The blank form must be clean enough to print and use — no extra whitespace or broken lines.
- The customer report must use plain language, not technician shorthand.
- Urgent items must appear at the top of the report, not buried.
- Every item with a status of `needs_attention` or `urgent` must have a notes field — if the technician left it blank, flag it to the user before generating the report.
- Status counts in the summary must match the actual detail section.
- No fabricated findings — only what the technician actually inspected.

---

## Input / Output Summary

| | Form Mode | Report Mode |
|---|-----------|-------------|
| **Input** | Vehicle, customer, mileage (all optional), type | Customer, vehicle, mileage, results JSON |
| **Tool** | `tools/inspection/generate_forms.py --mode form` | `tools/inspection/generate_forms.py --mode report` |
| **Output file** | `output/inspection/<type>_form.txt` | `output/inspection/inspection_report.txt` |
| **Contents** | Printable checklist with rating boxes & notes lines | Color-coded customer report with summary, findings, and recommendations |
