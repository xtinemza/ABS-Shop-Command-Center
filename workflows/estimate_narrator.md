# Module 6 — Repair Estimate Narrator

## Purpose
Turn a technical repair estimate into a plain-English explanation customers can actually understand. Each line item gets a clear description of what it is, why it's needed, what happens if they wait, and a cost breakdown. The final document is ready to hand to the customer or email alongside the estimate.

---

## Inputs Required

| Field | Required | Notes |
|-------|----------|-------|
| Customer name | Optional | Personalizes the intro paragraph |
| Vehicle | Optional | Year, Make, Model |
| Line items (estimate) | Yes | See format below |
| Shop labor rate | Optional | Defaults to calculating from total if not provided |

### Line Item Format

Collect the estimate line items as a JSON array. Each item:

```json
[
  {
    "part": "Front Brake Pads & Rotors",
    "part_cost": 180.00,
    "labor_hours": 1.5,
    "labor_cost": 142.50,
    "urgency": "high",
    "notes": "Pads at 2mm, rotors scored"
  },
  {
    "part": "Serpentine Belt",
    "part_cost": 45.00,
    "labor_hours": 0.5,
    "labor_cost": 47.50,
    "urgency": "medium",
    "notes": "Cracking visible on underside"
  },
  {
    "part": "Cabin Air Filter",
    "part_cost": 22.00,
    "labor_hours": 0.25,
    "labor_cost": 23.75,
    "urgency": "low",
    "notes": ""
  }
]
```

**Urgency levels:**
- `safety-critical` — Do not drive. Safety is at risk.
- `high` — Repair this visit. Will cause larger, more expensive failure soon.
- `medium` — Address within 30–60 days. Manageable but don't ignore.
- `low` — Recommended maintenance. Reasonable to schedule at next visit.

**Minimum per item:** `part` name and at least a `part_cost` or `labor_cost`. Everything else improves the output but is not required.

---

## Phase 1 — Load Context

**Step 1.** Load the shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 2.** Ask the user for the estimate details:
> "What's on the estimate? Give me the line items — part name, parts cost, labor hours or labor cost, and urgency for each item. You can paste from your shop management system or list them out."

Accept any format. If the user pastes raw text (e.g., from Mitchell1 or ShopWare), help them structure it into the JSON format before running the tool.

**Step 3 (optional).** Ask for customer name and vehicle to personalize the document.

---

## Phase 2 — Generate the Narrated Estimate

Once you have all line items structured as JSON, run the tool:

```bash
python tools/estimates/narrate_estimate.py \
    --customer "David Chen" \
    --vehicle "2017 Honda CR-V" \
    --items '[{"part":"Front Brake Pads & Rotors","part_cost":180,"labor_hours":1.5,"labor_cost":142.50,"urgency":"high","notes":"Pads at 2mm, rotors scored"},{"part":"Serpentine Belt","part_cost":45,"labor_hours":0.5,"labor_cost":47.50,"urgency":"medium","notes":"Cracking visible on underside"},{"part":"Cabin Air Filter","part_cost":22,"labor_hours":0.25,"labor_cost":23.75,"urgency":"low","notes":""}]'
```

The tool produces a single, complete customer-facing document with:
- A personalized intro paragraph
- Each repair item explained in plain English with cost breakdown
- A "What happens if I wait?" section for all high/safety items
- A grand total
- A closing paragraph inviting questions

---

## Phase 3 — Review & Deliver

After the tool runs:

1. Show the user the output file path: `output/estimates/narrated_estimate.txt`
2. Offer to display the full document inline
3. Summarize what was produced:

```
✅ Estimate Narrator complete.

Customer: David Chen
Vehicle: 2017 Honda CR-V
Line items narrated: 3
  🚨 High urgency: 1 item (Front Brake Pads & Rotors)
  🟡 Medium urgency: 1 item (Serpentine Belt)
  🟢 Low urgency: 1 item (Cabin Air Filter)
Estimate total: $461.25

Saved to: output/estimates/narrated_estimate.txt
```

---

## Decision Rules

**If the user provides the estimate as raw text (not JSON):** Structure it into JSON yourself before running the tool. Ask the user to confirm any fields you're unsure about (especially urgency and cost breakdowns).

**If urgency is not specified:** Default to `medium` and note to the user that you assumed medium urgency for that item.

**If parts cost or labor cost is missing but total is given:** Calculate the missing field if possible. If you can't, pass what you have — the tool will omit the breakdown line and show only the total.

**If the tool fails:** Try once more. If it fails again, offer to generate the narration manually item by item in plain text.

**If the customer name is not provided:** The tool generates a generic intro ("Dear Valued Customer") — that's fine.

---

## Quality Standards

- Language must be at an 8th-grade reading level. No shop jargon.
- Never minimize safety-critical or high-urgency items — be honest about consequences.
- Never exaggerate low-urgency items to pressure the customer.
- Urgency framing must match the urgency level passed in:
  - `safety-critical` → "Do not drive this vehicle until repaired."
  - `high` → "We strongly recommend addressing this today."
  - `medium` → "Plan to address this within the next 30–60 days."
  - `low` → "This is routine maintenance — schedule at your next visit."
- Cost context must be honest: say "this is typical for this repair" only when that's true.
- End every document with a genuine invitation to ask questions.

---

## Input / Output Summary

| | Details |
|---|---|
| **Input** | Customer name (optional), vehicle (optional), JSON array of line items |
| **Tool** | `tools/estimates/narrate_estimate.py` |
| **Output file** | `output/estimates/narrated_estimate.txt` |
| **Contents** | Intro paragraph, per-item plain-English explanations with cost breakdowns, "what if I wait?" section, grand total, closing |
