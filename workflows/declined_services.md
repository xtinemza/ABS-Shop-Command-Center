# Declined Services Follow-Up Campaign — Workflow

## Purpose
Generate a 4-touch follow-up campaign for customers who declined a recommended service. The sequence is designed to educate, create honest urgency, and offer an incentive — in that order — without being pushy or manipulative. Urgency and tone scale automatically based on the service's safety classification.

---

## Input / Output Summary

**Inputs:**
- Shop profile (`data/shop_profile.json`) — loaded automatically
- Service name (what was declined — e.g., "Brake Pad Replacement", "Transmission Flush")
- Urgency level: `low` | `medium` | `high` | `safety-critical`
- Discount offer for Touch 3 (e.g., "15% off, max $75")

**Outputs:**
- 12 files (4 touches × 3 channels) saved to `output/declined_services/`
- Files named `{service_slug}_touch{N}_{channel}.txt`

---

## Phase 1 — Load Context

### Step 1.1 — Load Shop Profile
```bash
python tools/shared/load_profile.py
```

### Step 1.2 — Collect Inputs
Ask the user (one at a time):

1. "Which declined service do you want to follow up on? (e.g., Brake Pad Replacement, Timing Belt, Transmission Flush)"
2. "How urgent is this service?
   - `low` — cosmetic or minor convenience (e.g., cabin air filter)
   - `medium` — performance/longevity impact (e.g., transmission flush)
   - `high` — reliability risk if deferred (e.g., worn tires, battery)
   - `safety-critical` — immediate safety concern (e.g., metal-on-metal brakes, failed ball joint)"
3. "What offer do you want to include in Touch 3? (e.g., '15% off the service, max $75, this week only')"

If the user isn't sure about urgency, suggest based on the service:
- Brakes, steering, tires, ball joints → `safety-critical`
- Battery, belts, suspension → `high`
- Fluids, filters → `medium`
- Wiper blades, cosmetic issues → `low`

### Step 1.3 — Confirm
> "Generating a 4-touch campaign for **[service]** (urgency: [level]).
> Touch 3 offer: [offer]. Proceed?"

---

## Phase 2 — Generate Campaign

```bash
# Generate the complete 4-touch campaign
python tools/declined_services/generate_campaign.py \
    --service "Brake Pad Replacement" \
    --urgency safety-critical \
    --offer "15% off brake service this week, max $75"

# Generate with default urgency (medium)
python tools/declined_services/generate_campaign.py \
    --service "Transmission Flush" \
    --offer "10% off, max $50"

# Generate only specific touches
python tools/declined_services/generate_campaign.py \
    --service "Battery Replacement" \
    --urgency high \
    --offer "$20 off" \
    --touches 1,2
```

**4-touch sequence:**

| Touch | Timing | Approach | Tone |
|-------|--------|----------|------|
| Touch 1 | Same day (at end of visit) | Educational — no selling | Informative, friendly |
| Touch 2 | 3 days after visit | Safety/consequence context | Honest, direct |
| Touch 3 | 2 weeks after visit | Incentive offer | Warm, feels like a favor |
| Touch 4 | 30 days after visit | Final check-in with easy CTA | Caring, no pressure |

Each touch generates SMS, email, and phone script.

**Urgency affects tone:**
- `low`: Matter-of-fact. "When you're ready" energy. No alarm.
- `medium`: Practical. References longevity and cost-of-delay. Calm urgency.
- `high`: Direct. Reliability risk stated plainly. Recommends scheduling soon.
- `safety-critical`: Clear and serious. States the safety risk honestly. Not alarmist — just factual.

---

## Phase 3 — Review

After generating, display Touch 1 (email) and Touch 4 (SMS) for the user to review.

If the urgency level feels wrong, re-run with a different `--urgency` flag.

Offer to:
- Adjust the discount in Touch 3
- Generate a campaign for a second declined service
- Modify Touch 4's final CTA (e.g., add a specific phone extension or booking link)

---

## Phase 4 — Deliver Summary

```
✅ Declined Services Campaign — Generated
Service: [service]  |  Urgency: [level]
Touch 3 Offer: [offer]

Touch         SMS    Email  Phone Script  Timing
────────────────────────────────────────────────────────
Touch 1        ✅     ✅     ✅           Same day (end of visit)
Touch 2        ✅     ✅     ✅           3 days after
Touch 3        ✅     ✅     ✅           2 weeks after
Touch 4        ✅     ✅     ✅           30 days after

Files saved to: output/declined_services/
Naming: [service]_touch1_sms.txt, [service]_touch2_email.txt, etc.
```

---

## Decision Rules

**If the service is safety-critical:**
Flag this to the user: "This service was classified as safety-critical. The Touch 1 message will include plain-language safety language — no exaggeration, just facts. Review it before sending." Require the user to confirm they've reviewed Touch 1 before proceeding.

**If the customer already rebooked:**
Don't run this campaign. Ask the user to confirm the customer hasn't already scheduled the service.

**If the user wants more than 4 touches:**
Advise against it — 4 touches over 30 days is the industry standard ceiling for non-pushy follow-up. Offer to adjust timing instead.

**If the user doesn't have a discount offer for Touch 3:**
Use: "Complimentary multi-point inspection with your [service] when you book this month." This is high-perceived-value at low cost to the shop.

**If the shop's review link is set in the profile:**
Include it in Touch 4 only — don't mix a review ask into safety follow-ups.

**If a tool fails:**
Try once more. Show the error if it fails again and offer to present the template text manually.

---

## Output Files

```
output/declined_services/
├── {service}_touch1_sms.txt
├── {service}_touch1_email.txt
├── {service}_touch1_phone_script.txt
├── {service}_touch2_sms.txt
├── {service}_touch2_email.txt
├── {service}_touch2_phone_script.txt
├── {service}_touch3_sms.txt
├── {service}_touch3_email.txt
├── {service}_touch3_phone_script.txt
├── {service}_touch4_sms.txt
├── {service}_touch4_email.txt
└── {service}_touch4_phone_script.txt
```

---

## Quality Standards

- **Touch 1 is education only.** No offer, no discount, no urgency push. Just useful information that builds trust. If the customer feels sold to on Touch 1, the rest of the campaign fails.
- **Touch 2 uses real consequences.** What actually happens if this service is skipped too long. No exaggeration — the facts are compelling enough.
- **Touch 3 offer must feel like a favor.** The customer should feel like the shop is being generous, not desperate. Frame it as "making it easy" not "begging them to come back."
- **Touch 4 is the graceful close.** No pressure. Just: "We're here when you're ready." If urgency is safety-critical, Touch 4 restates the safety concern plainly and offers an easy booking path.
- **Safety-critical services:** Never minimize risks. Never exaggerate them. State the specific failure mode (e.g., "metal-on-metal contact can damage the rotor") and what it means for the driver's safety.
- **SMS under 160 chars** for all touchpoints.
- **Every email has a subject line** in `Subject: ...` format on line 1.
- **Phone scripts** include `[GREET]`, `[PURPOSE]`, `[PAUSE]`, `[IF YES]`, `[IF NO]`, `[CLOSE]`.
