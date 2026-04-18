# Wait Time Communication Templates — Workflow

## Purpose
Generate professional, ready-to-send templates for every customer communication point during a service visit — from the moment a vehicle is checked in through pickup. Templates are produced in SMS, email, and phone script formats so your front desk has the right message for every situation, every time.

---

## Input / Output Summary

**Inputs:**
- Shop profile (`data/shop_profile.json`) — loaded automatically
- Status type (which update to generate — or "all" for the complete set)
- Service type (e.g., "Oil Change", "Brake Repair") — used to personalize templates
- Optional: estimated time, tech name, delay reason, additional findings

**Outputs:**
- Up to 15 files (5 status types × 3 channels) saved to `output/wait_time/`
- Each file named `{status}_{channel}.txt`

---

## Phase 1 — Load Context

### Step 1.1 — Load Shop Profile
```bash
python tools/shared/load_profile.py
```
Confirm that `shop_name`, `phone`, `address`, and `hours` are set. These appear in nearly every template.

### Step 1.2 — Collect Inputs
Ask the user:
> "Which status update templates do you need? You can generate all five at once, or pick specific ones:
>   1. drop_off_confirmation — Vehicle received, service started
>   2. inspection_update — Findings ready, waiting on customer approval
>   3. repair_in_progress — Work is underway, ETA provided
>   4. ready_for_pickup — Vehicle complete
>   5. delayed_notification — More time needed, new ETA"

If the user says "all," generate all five across all three channels.

Also ask (one question at a time):
- "What service type should the templates reference? (e.g., Oil Change, Brake Service, General Repair)"

### Step 1.3 — Confirm
> "Generating [status types] × 3 channels for [service type]. Proceed?"

---

## Phase 2 — Generate Templates

```bash
# Generate all 5 status types at once (15 files)
python tools/wait_time/generate_templates.py \
    --status all \
    --service_type "Brake Service"

# Generate a single status update
python tools/wait_time/generate_templates.py \
    --status drop_off_confirmation \
    --service_type "Oil Change"

# Generate with specific channels only
python tools/wait_time/generate_templates.py \
    --status ready_for_pickup \
    --service_type "Transmission Service" \
    --channels sms,email
```

**Status update sequence:**

| # | Status | When to Send | Customer Need |
|---|--------|--------------|---------------|
| 1 | `drop_off_confirmation` | At vehicle check-in | Reassurance: "we have your car, here's the plan" |
| 2 | `inspection_update` | When inspection is complete | Transparency: "here's what we found, do you approve?" |
| 3 | `repair_in_progress` | When work begins | Confidence: "we're working on it, here's your ETA" |
| 4 | `ready_for_pickup` | When vehicle is ready | Action: "come get your car, here's the total and summary" |
| 5 | `delayed_notification` | If more time is needed | Trust: "we need more time — here's why and the new ETA" |

---

## Phase 3 — Review & Customize

After generating, display the SMS and email versions for the most commonly used status (usually `drop_off_confirmation` and `ready_for_pickup`).

Offer to:
- Generate for a different service type
- Adjust ETA placeholder language
- Modify the tone (more formal, more casual)
- Add a specific tech name or manager name to scripts

---

## Phase 4 — Deliver Summary

```
✅ Wait Time Communication Templates — Generated
Service Type: [service_type]

Status                  SMS    Email  Phone Script
──────────────────────────────────────────────────
drop_off_confirmation    ✅     ✅     ✅
inspection_update        ✅     ✅     ✅
repair_in_progress       ✅     ✅     ✅
ready_for_pickup         ✅     ✅     ✅
delayed_notification     ✅     ✅     ✅

Files saved to: output/wait_time/

Usage tip: Load these into your CRM or texting platform and fill in the
{{double-brace}} placeholders at send time using the customer's actual data.
```

---

## Decision Rules

**If the user only needs SMS templates:**
Run with `--channels sms`. Email and phone script are optional add-ons.

**If the user wants the "additional work found" flow:**
The `inspection_update` template covers this — it includes language that separates the finding from the cost and explicitly requests approval before proceeding. No additional template is needed.

**If a parts delay extends the ETA:**
Use the `delayed_notification` template. It includes a clear explanation, a new ETA, and an option for the customer to pick up and return later.

**If the user doesn't know their service type yet:**
Use "your vehicle" as the service placeholder. It will still read naturally in every template.

**If profile fields are missing (hours, address):**
Note what's missing, ask for the values, update with `save_profile.py`, then re-run. Don't generate templates with empty shop information.

**If a tool fails:**
Try once more. If it fails again, show the error and offer to paste the template text manually.

---

## Output Files

```
output/wait_time/
├── drop_off_confirmation_sms.txt
├── drop_off_confirmation_email.txt
├── drop_off_confirmation_phone_script.txt
├── inspection_update_sms.txt
├── inspection_update_email.txt
├── inspection_update_phone_script.txt
├── repair_in_progress_sms.txt
├── repair_in_progress_email.txt
├── repair_in_progress_phone_script.txt
├── ready_for_pickup_sms.txt
├── ready_for_pickup_email.txt
├── ready_for_pickup_phone_script.txt
├── delayed_notification_sms.txt
├── delayed_notification_email.txt
└── delayed_notification_phone_script.txt
```

---

## Quality Standards

- **SMS:** Under 160 characters when placeholders are substituted with typical values. If over, tighten — do not truncate mid-sentence.
- **Email:** Subject line on the first line, format `Subject: ...`. Body includes all key information: what's happening, when it will be done, what the customer needs to do (if anything).
- **Phone scripts:** Include `[GREET]`, `[PURPOSE]`, `[PAUSE]`, `[IF YES/APPROVED]`, `[IF NO/DECLINED]`, `[CLOSE]` cues as appropriate. Approval requests must include a clear `[IF DECLINED]` path.
- **Approval requirement:** The `inspection_update` template must never assume approval. It must always ask before starting additional work. This protects the shop legally and builds trust.
- **Tone:** Proactive and informative — not apologetic. The customer should feel informed, not managed.
- **Specificity:** Every template references the service type and vehicle placeholder. "Your brake service" reads better than "your vehicle's service."
- **Pickup template:** Must include hours, address, accepted payment methods, and total cost placeholder. The customer should have everything they need to plan their pickup in one message.
