# Vehicle Recall Notification Module — Workflow SOP
## Module 8 | Shop Command Center

**Purpose:** Cross-reference customer vehicles against known NHTSA recall data and generate professional, multi-channel notifications alerting customers to open recalls, safety implications, and next steps.

---

## Inputs Required

| Field | Required | Notes |
|-------|----------|-------|
| Customer name | Yes | For personalized notifications |
| Vehicle year/make/model | Yes | OR provide VIN |
| VIN | Optional | Enables more precise lookup |
| Recall data | Yes (Phase 2) | Campaign #, component, description, remedy |
| Urgency level | Optional | low / medium / high — defaults to medium |

## Outputs Produced

| File | Location | Description |
|------|----------|-------------|
| `recall_lookup_guide.txt` | `output/recall/` | Step-by-step guide to find recall data on NHTSA |
| `recall_check_results.txt` | `output/recall/` | Formatted recall info entered by user |
| `recall_notification_sms.txt` | `output/recall/` | SMS alert (under 160 chars) |
| `recall_notification_email.txt` | `output/recall/` | Full email with subject line |
| `recall_notification_phone_script.txt` | `output/recall/` | Structured phone call script |
| `recall_notification_shop_note.txt` | `output/recall/` | Internal file note for shop records |

---

## Phase 1 — Load Context

### Step 1: Load shop profile
```bash
python tools/shared/load_profile.py
```

### Step 2: Collect vehicle information
Ask the user:
- Customer name
- Vehicle: Year, Make, Model (required at minimum)
- VIN if available
- Any urgency context (e.g., "we just saw this vehicle" or "customer called about it")

---

## Phase 2 — Look Up Recalls

**IMPORTANT:** This tool does NOT make live API calls. The shop must look up recall data manually. Run `check_recalls.py` to get the exact lookup instructions and NHTSA URLs for the vehicle.

### Step 1: Generate lookup guide
```bash
# With VIN (most accurate):
python tools/recall/check_recalls.py --vin "1HGBH41JXMN109186" --customer "Sarah Mitchell"

# OR with year/make/model:
python tools/recall/check_recalls.py --year 2019 --make Toyota --model Camry --customer "Sarah Mitchell"
```

This outputs:
- Direct NHTSA URL to paste into a browser
- NHTSA API URL the user can open directly
- What information to copy back from the NHTSA results

### Step 2: User looks up recalls on NHTSA
Direct the user to open the provided URL. The NHTSA site will show:
- Campaign Number
- Component affected
- Description of defect
- Consequence if unrepaired
- Remedy (what the fix is)

### Step 3: Enter recall data
Once the user has the recall info, run with `--recall_data`:
```bash
python tools/recall/check_recalls.py \
  --year 2019 --make Toyota --model Camry \
  --customer "Sarah Mitchell" \
  --recall_campaign "19V123000" \
  --component "FUEL SYSTEM, GASOLINE:FUEL PUMP" \
  --description "The fuel pump impeller may crack and cause the engine to stall or fail to start." \
  --consequence "Engine stall increases crash risk." \
  --remedy "Toyota will replace the fuel pump free of charge."
```

**Edge Case — No Recalls Found:**
If NHTSA shows no open recalls:
- Tell the user no action is required for this vehicle
- Log it as "checked, no recalls" for documentation purposes
- Offer to check again with a VIN if they only used year/make/model

**Edge Case — Multiple Recalls Found:**
Run `generate_notifications.py` once per recall campaign, using a unique `--recall_campaign` value each time. Output files will be named with the campaign number to avoid overwriting.

---

## Phase 3 — Generate Customer Notifications

Once recall data is confirmed, generate all notification channels:

```bash
python tools/recall/generate_notifications.py \
  --customer "Sarah Mitchell" \
  --vehicle "2019 Toyota Camry" \
  --recall_campaign "19V123000" \
  --component "Fuel Pump" \
  --description "The fuel pump may crack, causing the engine to stall or fail to start." \
  --consequence "An engine stall while driving increases the risk of a crash." \
  --remedy "Toyota will replace the fuel pump at no charge to the owner." \
  --urgency high
```

**Urgency levels:**
- `low` — Informational, not immediately dangerous. Schedule when convenient.
- `medium` (default) — Should be addressed, no immediate emergency.
- `high` — Safety-critical. Customer should not drive the vehicle until repaired.

### Edge Case — Shop Cannot Perform the Recall:
Some recalls are dealer-only. If the shop cannot do the work:
- Still generate all notifications
- Include language directing the customer to their nearest dealer
- Offer to inspect the vehicle before they go to confirm the issue is present

### Edge Case — Customer Already Had It Fixed:
If the customer confirms the recall was already addressed:
- Note it in the shop file with date confirmed
- No notifications needed
- Update vehicle history if using a service history module

---

## Phase 4 — Deliver & Document

### Step 1: Present outputs to user
Tell the user what files were generated:
- SMS: ready to copy-paste into their messaging tool
- Email: ready to copy-paste into their email client
- Phone script: ready to hand to the service advisor making the call
- Shop note: ready to add to the customer's file

### Step 2: Confirm follow-up
Ask: "Do you want me to flag this for follow-up if the customer doesn't respond in 7 days?"

If yes, note the follow-up date. (Manual — the shop sets a reminder in their system.)

---

## Quality Standards

- **Never alarm customers unnecessarily.** State facts calmly. Use the manufacturer's language where possible.
- **Always mention recall repairs are typically free.** This removes cost as an objection.
- **SMS must be under 160 characters.** The tool enforces this but verify the output.
- **All four channels (SMS, email, phone, shop note) must be produced** for every recall notification.
- **Use the customer's name** in every template — not "Dear Customer."
- **Include the NHTSA campaign number** in all communications for the customer's reference.
- **High-urgency recalls** must include language recommending the customer limit or stop driving the vehicle.

---

## Decision Rules

| Situation | Action |
|-----------|--------|
| NHTSA shows no recalls | Tell user, document as checked, no notifications needed |
| Multiple open recalls | Run generate_notifications.py once per recall |
| Dealer-only recall | Generate notifications with dealer referral language |
| Customer already repaired | Note it, skip notifications |
| VIN not available | Use year/make/model, note results may include multiple trims |
| User has recall info already | Skip Phase 2, go directly to Phase 3 |
