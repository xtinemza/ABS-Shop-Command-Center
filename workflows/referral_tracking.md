# Referral Tracking & Reward System — Workflow
## Module 15 | Shop Command Center

**Purpose:** Track who referred whom, generate personalized thank-you messages for referrers and welcome messages for new customers, manage reward status, and report on referral program performance.

---

## Input / Output Summary

| Input | Source |
|-------|--------|
| Referrer name and phone | User provides |
| Referee (new customer) name and phone | User provides |
| Service date and type | User provides |
| Reward type and value | User provides |
| Reward issued status | User tracks |

| Output | Location |
|--------|----------|
| Referral database | `data/referrals.json` |
| Thank-you SMS and email (referrer) | `output/referrals/reward_referrer_[name]_sms.txt`, `_email.txt` |
| Welcome SMS and email (referee) | `output/referrals/reward_referee_[name]_sms.txt`, `_email.txt` |
| Internal referral note | `output/referrals/internal_note_[name].txt` |
| Referral program report | `output/referrals/referral_report.txt` |

---

## Phase 1 — Load Context and Determine Request

**Step 1.1** — Load shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 1.2** — Ask the user:
> What do you need for referral tracking today?
> - **A** — Log a new referral
> - **B** — Generate thank-you and reward messages
> - **C** — List referrals and check who's owed a reward
> - **D** — Generate referral program report

**Step 1.3** — If the user is new to this module, ask about the reward program:
> What reward do you offer referrers? (e.g., "$25 off next service," "free oil change," "10% off")
> Do new customers (referees) get anything? (e.g., "$20 off first visit," "free inspection")

---

## Phase 2A — Log a New Referral

Collect from the user:

| Field | Required? |
|-------|-----------|
| Referrer name | Yes |
| Referrer phone | Recommended |
| Referee name (new customer) | Yes |
| Referee phone | Recommended |
| Service date | Yes |
| Service performed | Yes |
| Reward issued? | No (default: not yet) |
| Notes | Optional |

```bash
python tools/referrals/track_referrals.py \
    --action add \
    --referrer_name "John Smith" \
    --referrer_phone "(303) 555-4412" \
    --referred_name "Jane Doe" \
    --referred_phone "(303) 555-7821" \
    --service_date "2025-04-10" \
    --service "Brake Repair — front pads and rotors" \
    --notes "Jane mentioned John sent her"
```

After logging, ask: "Do you want to generate thank-you messages for this referral now?"

---

## Phase 2B — Generate Reward Messages

After logging a referral, or when the user wants to send a reward:

```bash
python tools/referrals/generate_rewards.py \
    --referrer_name "John Smith" \
    --referrer_phone "(303) 555-4412" \
    --referred_name "Jane Doe" \
    --reward_type discount \
    --reward_value "$25 off your next service" \
    --referee_reward "$20 off your first visit"
```

This generates four files:
1. Thank-you SMS to referrer
2. Thank-you email to referrer
3. Welcome SMS to new customer (referee)
4. Welcome email to new customer (referee)
5. Internal note for the customer file

Display each file's content and path to the user.

---

## Phase 2C — List Referrals and Check Rewards Owed

```bash
python tools/referrals/track_referrals.py --action list
```

To see only referrals where the reward hasn't been issued:
```bash
python tools/referrals/track_referrals.py --action list --filter pending_rewards
```

For each pending reward, suggest running `generate_rewards.py` to create the outreach messages.

After a reward is issued, mark it:
```bash
python tools/referrals/track_referrals.py \
    --action update \
    --referral_id R-001 \
    --reward_issued yes \
    --notes "Gave John $25 credit on 4/15 oil change"
```

---

## Phase 2D — Generate Referral Program Report

```bash
python tools/referrals/track_referrals.py --action report
```

Report includes:
- Total referrals logged
- Conversion rate (referrals that completed a service)
- Rewards issued vs. pending
- Top referrers by count
- Estimated revenue from referred customers

---

## Phase 3 — Confirm and Deliver

After any action:
- Confirm what was logged or generated
- State file paths for all generated messages
- Remind the user to mark rewards as issued once delivered

---

## Edge Case Rules

**If phone numbers are missing:** Log the referral without them. Note that reward messages cannot be sent without contact info. Flag these for follow-up.

**If the same person refers multiple customers:** Each referral gets its own entry. The report will show total referrals per person.

**If a referee becomes a referrer later:** Log them as a referrer on that new entry. The system tracks individuals by name and phone.

**If the reward program terms change:** Existing logged referrals retain their original reward noted in their entry. New entries use the new terms.

**If a referral is a duplicate** (same referrer + same referee): Warn the user before adding. Ask if they want to update the existing entry instead.

---

## Quality Standards

- Thank-you messages must be warm and personal. This person just brought you business — treat them accordingly.
- Reward notifications must state the reward clearly: what it is, how to redeem it, and whether it expires.
- Reports must show: total referrals, top referrers, and rewards owed.
- Never send reward messages to referrers until the referred customer has actually completed a service (not just booked).
- All messages use the shop's real name, phone, and owner name from `shop_profile.json`.
