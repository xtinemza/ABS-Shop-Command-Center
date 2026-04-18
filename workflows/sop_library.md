# Standard Operating Procedure (SOP) Library Builder — Workflow SOP
## Module 10 | Shop Command Center

**Purpose:** Generate comprehensive, ready-to-print SOPs for every major auto repair shop process. Each SOP is formatted with Purpose, Scope, Responsibilities, Step-by-Step Procedure (with "Why" notes), Quality Checks, and Notes/Exceptions — detailed enough for a new employee to follow on day one.

---

## Inputs Required

| Field | Required | Notes |
|-------|----------|-------|
| Procedure name | Yes | From the built-in list, or use --custom |
| Custom rules | Optional | Shop-specific additions appended to the SOP |
| Custom description | Optional | Use --custom to generate a free-form SOP |

## Outputs Produced

| File | Location | Description |
|------|----------|-------------|
| `sop_<procedure>.txt` | `output/sop/` | Complete SOP document, print-ready |

---

## Phase 1 — Load Context

### Step 1: Load shop profile
```bash
python tools/shared/load_profile.py
```

### Step 2: Ask what SOPs they need
Present the full list and ask:
- "Which procedures do you need SOPs for? Pick specific ones or say 'all'."
- "Are there any shop-specific rules I should add? (e.g., 'We always take photos at intake.')"

If the user says "all," run the tool once per procedure using a loop — do not skip any.

---

## Phase 2 — Generate SOPs

### Built-in Procedures by Category

**Vehicle Operations**
```bash
python tools/sop/generate_sop.py --procedure vehicle_intake
python tools/sop/generate_sop.py --procedure oil_change
python tools/sop/generate_sop.py --procedure tire_rotation
python tools/sop/generate_sop.py --procedure vehicle_inspection
python tools/sop/generate_sop.py --procedure test_drive
python tools/sop/generate_sop.py --procedure quality_control
python tools/sop/generate_sop.py --procedure vehicle_delivery
```

**Customer Service**
```bash
python tools/sop/generate_sop.py --procedure phone_greeting
python tools/sop/generate_sop.py --procedure customer_checkin
python tools/sop/generate_sop.py --procedure estimate_approval
python tools/sop/generate_sop.py --procedure customer_complaints
```

**Operations**
```bash
python tools/sop/generate_sop.py --procedure parts_ordering
python tools/sop/generate_sop.py --procedure warranty_claims
python tools/sop/generate_sop.py --procedure cash_handling
python tools/sop/generate_sop.py --procedure hazmat_disposal
python tools/sop/generate_sop.py --procedure end_of_day
```

**With shop-specific custom rules:**
```bash
python tools/sop/generate_sop.py --procedure vehicle_intake \
    --custom_rules "Always photograph all four corners of the vehicle at check-in."
```

**Custom/free-form SOP (not in built-in list):**
```bash
python tools/sop/generate_sop.py \
    --custom "How to handle after-hours key drop-off for early morning appointments" \
    --title "After-Hours Key Drop Procedure"
```

### Listing available procedures
```bash
python tools/sop/generate_sop.py --list
```

### Generating all SOPs at once
```bash
python tools/sop/generate_sop.py --all
```

---

## Phase 3 — Save & Summarize

Each SOP is saved automatically to `output/sop/sop_<procedure>.txt`.

After generation, tell the user:
- File location for each SOP
- Recommended review: confirm the `[CUSTOMIZE]` flags match their shop's specific rules
- Suggested next step: print and laminate for each work area, or add to a shared drive

---

## Quality Standards

- **Every SOP must have**: Purpose, Scope, Who Is Responsible, Materials/Tools Needed, Step-by-Step Procedure, Quality Checks, Notes/Exceptions.
- **Steps must be numbered** and specific enough for a new employee on day one.
- **Each step includes a "Why" note** so employees understand the reasoning, not just the instruction.
- **No placeholder [INSERT] in final output** — use real shop name from profile.
- **[CUSTOMIZE] flags** mark steps that vary by shop (e.g., specific software, local regulations).
- **Procedure-specific tools/materials** must be listed — not generic.

---

## Decision Rules

| Situation | Action |
|-----------|--------|
| User asks for "all" SOPs | Run --all flag or loop through every procedure |
| User wants a custom SOP | Use --custom with a description, --title for the SOP name |
| User has shop-specific rules | Append with --custom_rules; they appear as a dedicated section |
| SOP needs legal/regulatory content | Add note: "Verify with local regulations — rules vary by state/municipality" |
| User wants to update an existing SOP | Regenerate with updated --custom_rules; output overwrites previous file |
| User wants to print the SOP | File is plain text — open in any text editor or word processor to format and print |
