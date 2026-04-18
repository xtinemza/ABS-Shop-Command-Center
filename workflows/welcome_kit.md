# New Customer Welcome Kit Generator — Workflow

## Purpose
Generate a complete welcome package for first-time customers: a personal thank-you letter from the owner, a shop overview, a realistic mileage-based maintenance guide, a new-customer discount offer, a referral card, and a full welcome email that combines it all. Every component is ready to print, email, or insert into a folder — no editing required (beyond personalizing `{{customer_name}}` at send time).

---

## Input / Output Summary

**Inputs:**
- Shop profile (`data/shop_profile.json`) — loaded automatically
- New customer discount offer (e.g., "10% off your next visit, max $50, valid 90 days")
- Referral reward (e.g., "$25 off for you and $25 off for the friend you refer")
- Specific service performed at first visit (optional — used to personalize thank-you letter)

**Outputs:**
- 6 files saved to `output/welcome_kit/`
- One combined `welcome_email.txt` ready to send

---

## Phase 1 — Load Context

### Step 1.1 — Load Shop Profile
```bash
python tools/shared/load_profile.py
```
Check that `shop_name`, `owner_name`, `phone`, `address`, `location`, `website`, `services`, and `business_type` are populated. If critical fields are missing, prompt the user before proceeding.

### Step 1.2 — Collect Inputs
Ask the user (one question at a time):

1. "What new-customer offer would you like to include? (e.g., '10% off next visit, max $50, valid 90 days')"
2. "Do you have a referral reward? (e.g., '$25 off for both you and a friend')"
3. "What service did this customer just have done? (optional — leave blank to keep it general)"

If the user says "use defaults," use:
- Discount: "10% off your next service visit — up to $50 in savings. Valid for 90 days."
- Referral: "$25 off for you and $25 off for the friend you refer — no limit on referrals."

### Step 1.3 — Confirm
Present a brief summary and ask: "Ready to generate all 6 welcome kit components?"

---

## Phase 2 — Generate Components

Run with `--component all` to generate everything at once, or run each component individually:

```bash
# Generate all 6 components at once
python tools/welcome_kit/generate_kit.py \
    --component all \
    --discount "10% off your next service, max $50, valid 90 days" \
    --referral_offer "$25 off for you and the friend you refer" \
    --service_performed "oil change and tire rotation"

# Generate a single component
python tools/welcome_kit/generate_kit.py \
    --component thank_you_letter \
    --discount "10% off next visit" \
    --service_performed "brake pad replacement"
```

**Components:**

| Component | File | Description |
|-----------|------|-------------|
| `thank_you_letter` | `thank_you_letter.txt` | Personal letter from the owner (~200 words) |
| `shop_overview` | `shop_overview.txt` | Who we are, what we offer, what sets us apart |
| `maintenance_guide` | `maintenance_guide.txt` | Mileage-based maintenance schedule with real intervals |
| `new_customer_offer` | `new_customer_offer.txt` | The discount offer with redemption instructions and terms |
| `referral_card` | `referral_card.txt` | Referral program details and tracking instructions |
| `welcome_email` | `welcome_email.txt` | Complete email combining all components, ready to send |

---

## Phase 3 — Review & Customize

After generating, present the welcome email to the user so they can review the overall tone.

Offer to:
- Adjust the discount or referral offer terms
- Customize the thank-you letter for a specific customer
- Modify the shop overview language
- Re-run any single component

If the user wants to update the discount or referral offer and re-run:
```bash
python tools/welcome_kit/generate_kit.py \
    --component welcome_email \
    --discount "15% off next visit, max $75" \
    --referral_offer "$30 off for both"
```

---

## Phase 4 — Deliver Summary

```
✅ Welcome Kit — Generated
Shop: [shop_name]

Component               File                      Status
──────────────────────────────────────────────────────────
Thank-You Letter        thank_you_letter.txt       ✅
Shop Overview           shop_overview.txt          ✅
Maintenance Guide       maintenance_guide.txt      ✅
New Customer Offer      new_customer_offer.txt     ✅
Referral Card           referral_card.txt          ✅
Welcome Email           welcome_email.txt          ✅

Files saved to: output/welcome_kit/

Tip: The welcome_email.txt is ready to copy-paste into any email client.
     The other files can be printed and included in a physical welcome folder.
```

---

## Decision Rules

**If the user doesn't have a discount offer:**
Use: "Complimentary multi-point inspection on your next visit — a $30 value." This is always a value-add that costs little and impresses new customers.

**If services list is empty in the profile:**
Proceed with generic "full-service automotive repair" language. Remind the user they can update their services list via Option 0 (Shop Profile).

**If the user wants to personalize for a specific customer:**
Replace `{{customer_name}}` in the thank-you letter before printing/sending. The tool outputs it with the placeholder so the front desk can fill it in.

**If the user wants to run this for a fleet customer or business account:**
Swap the tone to "professional" and skip the referral card. Run each component individually with adjusted language.

**If a tool fails:**
Try once more. If it fails again, display the error and offer to copy the template content manually.

---

## Output Files

```
output/welcome_kit/
├── thank_you_letter.txt
├── shop_overview.txt
├── maintenance_guide.txt
├── new_customer_offer.txt
├── referral_card.txt
└── welcome_email.txt
```

---

## Quality Standards

- **Thank-you letter:** Must feel like it was written by a person, not a corporation. Owner's name signs it. References the specific service if provided. 150–250 words.
- **Shop overview:** 3–4 paragraphs. Speaks to what makes an independent shop better than a chain. Never uses the phrase "we pride ourselves."
- **Maintenance guide:** Real intervals (3k, 5k, 15k, 30k, 60k, 100k miles). Specific services at each interval. Seasonal tips section. Genuinely useful — not a veiled upsell.
- **New customer offer:** Clear terms. Dollar cap or percentage clearly stated. Expiration timeframe included. Redemption instructions are one sentence.
- **Referral card:** Step-by-step process. No limit on referrals. Reward for both parties stated clearly. Tracking method (mention customer name at booking) is explicit.
- **Welcome email:** Complete subject line. All components summarized. Ready to send. Signature includes name, shop name, phone, and website.
- **No `[INSERT]` placeholders** in final output — every field is filled from the profile or from user inputs at runtime.
