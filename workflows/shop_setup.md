# Shop Setup — First-Time Onboarding Workflow

## Purpose
Collect all shop profile information from the owner during first-time setup. This workflow runs automatically when `setup_complete` is `false` in `shop_profile.json`. It must complete before any other module can run.

---

## When This Runs
- On first launch, when `load_profile.py --check` returns `NOT_SETUP`
- When the user selects option 0 (My Shop Profile) and explicitly asks to redo setup
- When the agent detects that required fields (shop_name, owner_name, phone, location) are missing

---

## Phase 1 — Welcome & Intro

Greet the shop owner warmly. Explain this is a one-time setup and will take about 2 minutes.

> ⚙️ **Welcome to Shop Command Center!**
>
> Before we get started, I need a few details about your shop. This only takes about 2 minutes and you'll never have to fill it in again — every module will use your info automatically from here on.
>
> Let's start with the basics.

---

## Phase 2 — Collect Basic Info (Step 1 of 4)

Ask for the following together in one message:

- **Shop name** — What's the name of your shop?
- **Your name** — Owner or manager name?
- **Phone number** — Main customer-facing number?
- **Address** — Full street address including city, state, and ZIP?

Wait for the user's response. Do not proceed until all four are provided. If any are missing, ask only for what's missing before continuing.

---

## Phase 3 — Collect Hours & Services (Step 2 of 4)

Ask:

- **Business hours** — What are your regular hours? (e.g., Mon–Fri 7:30am–5:30pm, Sat 8am–1pm)
- **Services offered** — List the services you offer, separated by commas. (e.g., oil changes, brakes, tires, diagnostics, AC, transmission)
- **Business type** — How would you describe your shop in a few words? (e.g., "Independent auto repair", "Family-owned European specialist", "Tire and alignment shop")

Wait for the user's response before continuing.

---

## Phase 4 — Collect Online Presence (Step 3 of 4)

Ask:

- **Website** — Do you have a website? If so, what's the URL? (Say "none" to skip)
- **Google review link** — Do you have a Google review link you send customers? (Say "none" to skip)
- **Tagline** — Do you have a tagline or slogan? (Say "none" to skip)

These are optional. If the user says "none," "no," or "skip" for any field, leave it blank and move on.

---

## Phase 5 — Tone Preference (Step 4 of 4)

Ask:

> **Last one — how would you describe the tone of your shop's communication?**
>
> - **Professional** — Formal, business-like, precise
> - **Friendly** — Warm, approachable, conversational
> - **Professional and friendly** — A balanced mix (most shops choose this)
> - **Casual** — Relaxed, informal, like texting a friend
>
> Just pick one or describe your preference in your own words.

---

## Phase 6 — Save Profile

Once all inputs are collected, run `setup_wizard.py` to save everything at once:

```bash
python tools/shared/setup_wizard.py \
    --name "<shop_name>" \
    --owner "<owner_name>" \
    --phone "<phone>" \
    --address "<address>" \
    --location "<city, state>" \
    --hours "<hours>" \
    --services "<services>" \
    --type "<business_type>" \
    --website "<website or blank>" \
    --tagline "<tagline or blank>" \
    --google-review "<google_review_link or blank>" \
    --tone "<tone>"
```

**Extract city/state from the address** to populate `--location` automatically. Do not ask the user for this separately.

After saving, run `load_profile.py` to confirm the data was saved correctly.

---

## Phase 7 — Confirm & Launch

Display a clean summary of what was saved:

> ✅ **Setup complete! Here's your shop profile:**
>
> **[Shop Name]**
> 👤 [Owner Name]
> 📍 [Address]
> 📞 [Phone]
> 🕐 [Hours]
> 🔧 Services: [Services]
> 🌐 [Website or "No website on file"]
> ⭐ [Google review link or "No review link on file"]
> 💬 Tone: [Tone]
>
> You can update any of this anytime by selecting **option 0** from the main menu.
>
> Ready to get started? Here's what I can help you with today:

Then display the full module menu and wait for the user to pick a module.

---

## Error Handling

**If the user skips required fields** (shop name, owner name, phone, address): Remind them these are needed for every module to work. Ask once more. If they still skip, save what's available and flag the missing fields clearly.

**If `setup_wizard.py` fails**: Try `save_profile.py` directly with individual `--flag` arguments. If that also fails, tell the user to check the `data/` folder and try again.

**If the user wants to skip setup entirely**: Allow it with a warning that outputs will contain placeholder text instead of their real shop info. Proceed to the main menu.

---

## Quality Standards

- Never ask for more than 4 fields at a time — keep each step manageable.
- Never repeat questions the user already answered.
- Never leave `[Shop Name]` or `[Owner Name]` as literal placeholders in any output — always substitute real values.
- After setup, the `setup_complete` flag in `shop_profile.json` must be `true`.
