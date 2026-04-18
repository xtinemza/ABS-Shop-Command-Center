# Customer Milestone Outreach — Workflow
## Module 17 | Shop Command Center

**Purpose:** Generate personalized, celebratory messages for customer anniversaries (1-year, 2-year, 5-year), visit milestones (5th visit, 10th visit, 25th visit), and vehicle mileage milestones (50k, 100k miles). Builds loyalty without feeling like a marketing campaign.

---

## Input / Output Summary

| Input | Source |
|-------|--------|
| Milestone type | User selects |
| Customer name and phone | User provides |
| Vehicle details | User provides |
| Milestone value | User provides |
| Last service date | User provides |
| Offer/perk (optional) | User provides |

| Output | Location |
|--------|----------|
| Personalized SMS | `output/milestones/[type]_[customer]_sms.txt` |
| Personalized email | `output/milestones/[type]_[customer]_email.txt` |
| Phone script (major milestones) | `output/milestones/[type]_[customer]_phone_script.txt` |

---

## Milestone Types

| Type | `--milestone_type` | Phone Script? |
|------|--------------------|--------------|
| 1-year anniversary | `anniversary` with `--milestone_value "1 year"` | Yes |
| 2-year anniversary | `anniversary` with `--milestone_value "2 years"` | No |
| 5-year anniversary | `anniversary` with `--milestone_value "5 years"` | Yes (VIP) |
| 5th visit | `visit_count` with `--milestone_value "5th visit"` | No |
| 10th visit | `visit_count` with `--milestone_value "10th visit"` | Yes |
| 25th visit | `visit_count` with `--milestone_value "25th visit"` | Yes (VIP) |
| 50,000 miles | `mileage` with `--milestone_value "50,000 miles"` | No |
| 100,000 miles | `mileage` with `--milestone_value "100,000 miles"` | Yes |

---

## Phase 1 — Load Context

**Step 1.1** — Load shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 1.2** — Ask the user:
> Which milestone outreach do you need?
> - **Anniversary** — customer's 1-year, 2-year, or 5-year anniversary
> - **Visit count** — 5th, 10th, or 25th visit milestone
> - **Mileage** — 50k or 100k miles on the vehicle

**Step 1.3** — Collect customer details:
- Customer name
- Customer phone (for SMS)
- Vehicle (Year/Make/Model) — for mileage or vehicle-specific messages
- Last service date — to reference in messages
- Milestone value (e.g., "1 year," "10th visit," "100,000 miles")

**Step 1.4** — Ask about an offer:
> Would you like to include a reward or offer? (e.g., "10% off next service," "free oil change")
> This is optional — milestone messages work great without one too.

---

## Phase 2 — Generate Outreach

```bash
python tools/milestones/generate_outreach.py \
    --milestone_type anniversary \
    --customer_name "Maria Gonzalez" \
    --customer_phone "(303) 555-7821" \
    --milestone_value "1 year" \
    --vehicle "2019 Toyota Camry" \
    --last_service "2025-03-15" \
    --offer "10% off your next service"
```

More examples:

**5th visit:**
```bash
python tools/milestones/generate_outreach.py \
    --milestone_type visit_count \
    --customer_name "Tom Bradley" \
    --customer_phone "(303) 555-3344" \
    --milestone_value "5th visit" \
    --vehicle "2017 Ford F-150" \
    --last_service "2025-04-10"
```

**100k miles:**
```bash
python tools/milestones/generate_outreach.py \
    --milestone_type mileage \
    --customer_name "Kevin Park" \
    --customer_phone "(303) 555-1188" \
    --milestone_value "100,000 miles" \
    --vehicle "2015 Subaru Outback" \
    --last_service "2025-04-02" \
    --offer "Free full inspection with next oil change"
```

---

## Phase 3 — Review and Deliver

Display all generated files to the user. For major milestones (1-year, 10th visit, 100k miles), also show the phone script.

Ask:
> Are these messages ready to send? Would you like to adjust the tone or offer?

Confirm all file paths when done.

---

## Edge Case Rules

**If no offer is provided:** Generate the message without an offer. The message should feel complete and genuine — a warm acknowledgment, not a marketing push.

**If the vehicle is unknown:** Generate messages without vehicle-specific references. Do not insert "[VEHICLE]" placeholders.

**If the last service date is missing:** Generate messages without referencing the last visit. Do not mention a specific date.

**If a 5-year or 25th visit milestone is reached:** Treat these as VIP-level milestones. The tone should be noticeably more heartfelt and the phone script should be included even if not requested.

**If multiple milestones coincide** (e.g., 1-year AND 10th visit on same customer): Generate them as separate outreach pieces. Present both to the user.

---

## Quality Standards

- Messages must feel personal, not templated. Use the customer's first name throughout.
- Celebratory tone — warm, genuine, not salesy. If an offer is included, it should feel like a gift, not a hook.
- **SMS must be under 160 characters.** The tool enforces this.
- **Email should be warm but brief** — 150 to 300 words. Not a newsletter.
- Phone scripts include: opening line, what to say, how to mention the offer, how to close.
- All shop details (name, phone, owner, review links) come from `shop_profile.json`. No placeholders.
- Save files with descriptive names: `anniversary_maria_gonzalez_sms.txt`, not `output1.txt`.
