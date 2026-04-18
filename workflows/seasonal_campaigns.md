# Seasonal Campaign Builder — Workflow
## Module 14 | Shop Command Center

**Purpose:** Generate ready-to-send marketing campaigns tied to the season and automotive calendar. Each campaign produces an SMS blast, email campaign, social media post, and an internal staff briefing — all using the shop's real name, phone, and contact details.

---

## Input / Output Summary

| Input | Source |
|-------|--------|
| Season or campaign type | User selects |
| Special offer / discount | User provides (optional) |
| Offer expiration date | User provides (optional) |
| Channels to generate | User selects (default: all) |

| Output | Location |
|--------|----------|
| SMS blast | `output/seasonal/[season]_sms.txt` |
| Email (subject + body) | `output/seasonal/[season]_email.txt` |
| Social media caption | `output/seasonal/[season]_social.txt` |
| Staff briefing | `output/seasonal/[season]_staff_briefing.txt` |

---

## Campaign Calendar

| Period | Campaign | Key Services |
|--------|----------|-------------|
| Oct–Nov | Winterization | Battery, coolant, heater, tires, wipers |
| Mar–Apr | Spring Checkup | AC test, alignment, brakes, fluid check |
| May–Jun | Summer Road Trip Ready | AC service, tires, coolant, belts |
| Aug–Sep | Back to School / Fall Safety | Inspection, brakes, tires, lights |
| Nov–Dec | Holiday Travel Safety | Full inspection, oil change, tire pressure |
| Year-round | Tire Rotation | Rotation reminder every 5–7K miles |

**Available seasons/campaign types:** `winter`, `spring`, `summer`, `fall`, `holiday`

---

## Phase 1 — Load Context

**Step 1.1** — Load shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 1.2** — Determine the campaign. Ask:
> Which campaign do you want to build? (winter / spring / summer / fall / holiday)
> Or I can suggest one based on today's date.

**Step 1.3** — Ask for offer details:
> Do you have a special offer to include? For example:
> - "Free battery test with any service"
> - "$20 off your next oil change"
> - "10% off AC service in June"
> If no offer, leave blank and the campaign will omit the offer line.

**Step 1.4** — Ask for expiration (optional):
> Does this offer expire? If so, what date? (e.g., "June 30" or "end of month")

---

## Phase 2 — Generate the Campaign

Run the tool with all available inputs. Always generate all four channels:

```bash
python tools/seasonal/generate_campaign.py \
    --season winter \
    --campaign_type "Winter Ready — Battery & Coolant Special" \
    --discount "Free battery test with any service" \
    --expiry "November 30"
```

**Examples by season:**

Winter:
```bash
python tools/seasonal/generate_campaign.py \
    --season winter \
    --discount "Free battery test with any service" \
    --expiry "November 30"
```

Spring:
```bash
python tools/seasonal/generate_campaign.py \
    --season spring \
    --discount "10% off AC service — spring only" \
    --expiry "April 30"
```

Summer:
```bash
python tools/seasonal/generate_campaign.py \
    --season summer \
    --discount "$30 off full summer inspection" \
    --expiry "June 30"
```

Fall:
```bash
python tools/seasonal/generate_campaign.py \
    --season fall \
    --discount "Free safety inspection with tire rotation" \
    --expiry "September 30"
```

Holiday:
```bash
python tools/seasonal/generate_campaign.py \
    --season holiday \
    --discount "Free full-point inspection with oil change" \
    --expiry "December 20"
```

---

## Phase 3 — Review and Deliver

Display all four generated pieces to the user:
1. **SMS** — read it aloud. Confirm it's under 160 characters.
2. **Email** — show subject line and body. Check tone.
3. **Social** — confirm it fits platform style.
4. **Staff Briefing** — internal only, never sent to customers.

Ask:
> Are these ready to use, or would you like to adjust the offer wording, tone, or any detail?

If adjustments are needed, update and re-run the tool with corrected inputs.

Confirm file paths when done.

---

## Edge Case Rules

**If the user doesn't know the season:** Suggest based on current month. If April → spring. If July → summer. If October → winter. If November/December → holiday.

**If no offer is provided:** Generate the campaign without an offer line. Do not insert a placeholder like "[INSERT OFFER]" — just omit that sentence.

**If the expiration date is in the past:** Warn the user and ask them to confirm or update the date before proceeding.

**If the user wants a custom campaign type:** Accept free-text for `--campaign_type` and adapt the tone and services accordingly.

**If the shop profile is missing phone or website:** Generate the campaign with whatever is on file. Flag the missing fields and suggest updating the profile.

---

## Quality Standards

- **SMS must be under 160 characters.** The tool enforces this — if it's over, it trims automatically and notes the character count.
- **Tone is care-based, not fear-based.** "Let's get your car ready for winter" not "Don't get stranded in the cold."
- **No fabricated statistics.** No "9 out of 10 cars fail in winter" unless the user provides it.
- **All shop details (name, phone, website) must come from `shop_profile.json`.** No generic placeholders in final output.
- **Social posts must end with a call to action** — phone number or booking link.
- **Staff briefing must include**: campaign dates, services to upsell, talking points, and the offer terms.
