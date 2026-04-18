# Appointment Reminders & Follow-Up Sequences — Workflow

## Purpose
Generate a complete set of appointment communication templates covering every touchpoint in the customer journey — from booking confirmation through 6-month maintenance reminders. Each template is produced in SMS, email, and phone script formats and is ready to copy-paste into any CRM, texting platform, or scheduling system.

---

## Input / Output Summary

**Inputs:**
- Shop profile (`data/shop_profile.json`) — loaded automatically
- Service type (e.g., "Oil Change", "Brake Service", "Transmission Flush")
- Channels to generate (sms, email, phone_script — default: all three)
- Touchpoint(s) to generate (or "all" for the complete set)

**Outputs:**
- 18 files (6 touchpoints × 3 channels) saved to `output/appointments/`
- Each file is named `{touchpoint}_{channel}.txt`

---

## Phase 1 — Load Context

### Step 1.1 — Load Shop Profile
```bash
python tools/shared/load_profile.py
```
Verify that `shop_name`, `phone`, `address`, and `owner_name` are populated. If any are missing, prompt the user and update with `save_profile.py` before continuing.

### Step 1.2 — Collect User Inputs
Ask the user:
> "Which service type should I generate reminders for? (e.g., Oil Change, Brake Service, Transmission Flush, General Repair)"

If the user says "all" or "everything," use "General Service" as the service type — the `{{service_type}}` placeholder in each template will be filled by the front desk at send time.

**Do not ask multiple questions at once.** Get the service type first, then confirm.

### Step 1.3 — Confirm Before Running
Present a one-line confirmation:
> "Generating all 6 touchpoints × 3 channels for **[service type]**. That's 18 files. Ready to proceed?"

Wait for a "yes" or "go ahead" before running the generator.

---

## Phase 2 — Generate Templates

Run the generator for each touchpoint, or use `--touchpoint all` to generate everything at once:

```bash
# Generate all 18 files at once
python tools/appointments/generate_reminders.py \
    --touchpoint all \
    --service_type "Oil Change" \
    --channels sms,email,phone_script

# Generate a single touchpoint
python tools/appointments/generate_reminders.py \
    --touchpoint booking_confirmation \
    --service_type "Brake Service" \
    --channels sms,email,phone_script
```

**Touchpoint sequence:**

| # | Touchpoint | When to Send | Key Purpose |
|---|-----------|--------------|-------------|
| 1 | `booking_confirmation` | Immediately after booking | Confirm date/time/service, set expectations |
| 2 | `day_before_reminder` | 24 hours before appointment | Reduce no-shows, allow easy reschedule |
| 3 | `day_of_notification` | Morning of appointment | "See you today" — build excitement, reduce anxiety |
| 4 | `post_service_thankyou` | 1–2 hours after vehicle pickup | Thank them, request review, hint at next service |
| 5 | `thirty_day_followup` | 30 days after service | Check in, seasonal tip, soft re-booking |
| 6 | `six_month_maintenance` | 6 months after service | Maintenance due, specific recommendations |

For each touchpoint, generate all three channels: **SMS**, **email**, and **phone_script**.

---

## Phase 3 — Review & Customize

After generating, present the user with a summary table of what was created. Offer to:
- Adjust the tone (e.g., more casual, more urgent)
- Modify a specific touchpoint
- Generate the same set for a different service type

If the user wants to tweak a template, edit the content directly and re-save using:
```bash
python tools/shared/save_output.py appointments "<filename>.txt" "updated content"
```

---

## Phase 4 — Deliver Summary

Present the output summary:

```
✅ Appointment Reminder Templates — Generated
Service Type: [service_type]

Touchpoint               SMS    Email  Phone Script
─────────────────────────────────────────────────────
booking_confirmation     ✅     ✅     ✅
day_before_reminder      ✅     ✅     ✅
day_of_notification      ✅     ✅     ✅
post_service_thankyou    ✅     ✅     ✅
thirty_day_followup      ✅     ✅     ✅
six_month_maintenance    ✅     ✅     ✅

Files saved to: output/appointments/
```

Offer to generate templates for additional service types (brakes, tires, transmission, etc.) if useful.

---

## Decision Rules

**If profile fields are missing (shop_name, phone, address):**
Tell the user which fields are empty and ask them to provide values. Update with `save_profile.py` before generating. Do not generate templates with `[Not Set]` placeholders in the shop name or phone number.

**If the user wants only one or two touchpoints:**
Generate only those. Use `--touchpoint <name>` for each requested touchpoint individually.

**If the user wants to skip the phone script:**
Run with `--channels sms,email` only. Note that phone scripts are valuable for higher-ticket services.

**If a service type is unusual or very specific (e.g., "transmission reseal on a 2018 F-150"):**
Use it as-is. The `{{service_type}}` variable will carry through naturally — templates are written to work with any service name.

**If the user rejects a template's tone:**
Ask them to describe the preferred tone (more casual, more professional, shorter). Edit the template content and re-save.

**If the tool fails:**
Try once more. If it fails again, show the error and ask the user if they want to paste the content manually.

---

## Output Files

All files save to `output/appointments/`:

```
output/appointments/
├── booking_confirmation_sms.txt
├── booking_confirmation_email.txt
├── booking_confirmation_phone_script.txt
├── day_before_reminder_sms.txt
├── day_before_reminder_email.txt
├── day_before_reminder_phone_script.txt
├── day_of_notification_sms.txt
├── day_of_notification_email.txt
├── day_of_notification_phone_script.txt
├── post_service_thankyou_sms.txt
├── post_service_thankyou_email.txt
├── post_service_thankyou_phone_script.txt
├── thirty_day_followup_sms.txt
├── thirty_day_followup_email.txt
├── thirty_day_followup_phone_script.txt
├── six_month_maintenance_sms.txt
├── six_month_maintenance_email.txt
└── six_month_maintenance_phone_script.txt
```

---

## Quality Standards

- **SMS character limit:** Every SMS template must render under 160 characters when shop name (≤30 chars) and phone are substituted. Test mentally before saving.
- **Email subject lines:** Must appear on the first line in the format `Subject: ...` — no exceptions.
- **Phone scripts:** Must include all five cues: `[GREET]`, `[PAUSE]`, `[IF YES]`, `[IF NO]`, `[CLOSE]`. Scripts that ask for approval must include `[IF NO]` with a graceful exit.
- **Shop name and phone:** Must appear in every template. No generic `[Your Shop]` placeholders in final output.
- **Review request:** The `post_service_thankyou` must include the shop's Google review link if one is set in the profile. If not set, include a reminder to add one and use a soft ask ("look us up online") as fallback.
- **Specificity:** The 30-day and 6-month messages must reference the specific service performed — not just "your vehicle." This is what separates a real follow-up from a spam message.
- **Tone consistency:** Match the tone field from the shop profile across all templates. A shop with `"tone": "casual and friendly"` should sound different from one with `"tone": "professional"`.
