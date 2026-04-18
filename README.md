# Shop Command Center

**AI-Powered Operations Suite for Independent Auto Repair Shops**

A single Claude Code engine with 17 modules covering customer communication, transparency, safety, operations, and financial tracking. Built on the WAT Framework.

---

## What It Does

Shop Command Center is a unified AI agent that helps auto repair shop owners automate operational tasks across 5 categories:

**Customer Communication** — Appointment reminders, welcome kits, wait time updates, declined service follow-ups, seasonal campaigns, referral tracking, customer milestone outreach

**Transparency & Trust** — Vehicle service history reports, repair estimate translation (tech-to-plain-language), digital inspection forms

**Safety & Compliance** — Vehicle recall notifications (NHTSA lookup), equipment maintenance and calibration logging

**Operations** — SOP library for every shop process, parts inventory tracking with reorder alerts, warranty claim tracking and recovery

**Financial** — Expense categorization and reporting, technician productivity summaries

---

## Folder Structure

```
shop-command-center/
├── CLAUDE.md                          ← Agent brain (auto-read by Claude Code)
├── README.md                          ← You are here
├── data/
│   └── shop_profile.json              ← Shared shop context (name, hours, services)
├── workflows/
│   ├── appointment_reminders.md       ← Module 1
│   ├── welcome_kit.md                 ← Module 2
│   ├── wait_time_comms.md             ← Module 3
│   ├── declined_services.md           ← Module 4
│   ├── service_history.md             ← Module 5
│   ├── estimate_narrator.md           ← Module 6
│   ├── inspection_forms.md            ← Module 7
│   ├── recall_notifications.md        ← Module 8
│   ├── equipment_logger.md            ← Module 9
│   ├── sop_library.md                 ← Module 10
│   ├── parts_inventory.md             ← Module 11
│   ├── warranty_tracker.md            ← Module 12
│   ├── expense_reports.md             ← Module 13
│   ├── seasonal_campaigns.md          ← Module 14
│   ├── referral_tracking.md           ← Module 15
│   ├── tech_productivity.md           ← Module 16
│   └── customer_milestones.md         ← Module 17
├── tools/
│   ├── shared/
│   │   ├── load_profile.py            ← Load shop profile
│   │   ├── save_profile.py            ← Save/update shop profile
│   │   ├── save_output.py             ← Universal file saver
│   │   └── send_template.py           ← Format for SMS/email/phone
│   ├── appointments/
│   │   └── generate_reminders.py
│   ├── welcome_kit/
│   │   └── generate_kit.py
│   ├── wait_time/
│   │   └── generate_templates.py
│   ├── declined_services/
│   │   └── generate_campaign.py
│   ├── service_history/
│   │   └── generate_report.py
│   ├── estimates/
│   │   └── narrate_estimate.py
│   ├── inspection/
│   │   └── generate_forms.py
│   ├── recall/
│   │   ├── check_recalls.py
│   │   └── generate_notifications.py
│   ├── equipment/
│   │   ├── log_equipment.py
│   │   └── generate_alerts.py
│   ├── sop/
│   │   └── generate_sop.py
│   ├── parts_inventory/
│   │   ├── track_inventory.py
│   │   └── generate_po.py
│   ├── warranty/
│   │   ├── track_claims.py
│   │   └── generate_warranty_report.py
│   ├── expenses/
│   │   ├── categorize_expenses.py
│   │   └── generate_expense_report.py
│   ├── seasonal/
│   │   └── generate_campaign.py
│   ├── referrals/
│   │   ├── track_referrals.py
│   │   └── generate_rewards.py
│   ├── tech_productivity/
│   │   └── generate_summary.py
│   └── milestones/
│       └── generate_outreach.py
└── output/                            ← All generated files land here
    ├── appointments/
    ├── welcome_kit/
    ├── wait_time/
    ├── declined_services/
    ├── service_history/
    ├── estimates/
    ├── inspection/
    ├── recall/
    ├── equipment/
    ├── sop/
    ├── parts_inventory/
    ├── warranty/
    ├── expenses/
    ├── seasonal/
    ├── referrals/
    ├── tech_productivity/
    └── milestones/
```

---

## Prerequisites

- Python 3.8+
- Claude Code (CLI)
- VS Code (recommended)
- No third-party Python packages required — standard library only

---

## How to Launch

1. Open the `shop-command-center/` folder in VS Code.
2. Open a terminal and launch Claude Code.
3. Claude reads `CLAUDE.md` automatically, greets the shop by name, and presents the module menu.
4. Pick a module number or describe what you need.

**Note for deployment:** Before delivering to a shop owner, pre-fill `data/shop_profile.json` with their business details (name, phone, hours, services, etc.). The agent uses this profile to personalize every output automatically.

---

## How to Run Tools Manually

Every tool can be run independently from the terminal for testing.

### Shared Tools

```bash
# Check if shop profile is set up
python tools/shared/load_profile.py --check

# View full profile
python tools/shared/load_profile.py

# Save/update profile
python tools/shared/save_profile.py --name "Mike's Auto" --owner "Mike" --location "Denver, CO" --phone "(303) 555-1234"

# Save any output
python tools/shared/save_output.py appointments reminder.txt "content here"

# Format for channel
python tools/shared/send_template.py sms output/appointments/reminder.txt
```

### Module Tools

```bash
# Appointment reminders
python tools/appointments/generate_reminders.py --touchpoint day_before_reminder --service_type "Oil Change"

# Welcome kit
python tools/welcome_kit/generate_kit.py --component thank_you_letter

# Wait time templates
python tools/wait_time/generate_templates.py --touchpoint checkin_confirmation

# Declined services campaign
python tools/declined_services/generate_campaign.py --service "Brake Pads" --touches 3

# Service history report
python tools/service_history/generate_report.py --vehicle "2019 Toyota Camry" --mileage 67000 --records "01/15/24, 62000mi, Oil Change, $45"

# Estimate narrator
python tools/estimates/narrate_estimate.py --item "Replace front brake pads" --cost 350 --parts_cost 120

# Inspection forms
python tools/inspection/generate_forms.py --type multi_point

# Recall check
python tools/recall/check_recalls.py --year 2019 --make Toyota --model Camry

# Equipment logger
python tools/equipment/log_equipment.py --action add --name "BendPak Lift" --type "Lift" --serial "BP-001"
python tools/equipment/generate_alerts.py

# SOP generator
python tools/sop/generate_sop.py --process customer_checkin

# Parts inventory
python tools/parts_inventory/track_inventory.py --action add --part "Brake Pads" --part_number "BP-001" --quantity 12 --min_threshold 4 --cost 35
python tools/parts_inventory/generate_po.py

# Warranty tracker
python tools/warranty/track_claims.py --action new --part "Alternator" --vendor "O'Reilly" --cost 189.99

# Expense reports
python tools/expenses/categorize_expenses.py --date "2024-11-15" --amount 450 --category parts --description "Brake pads bulk"
python tools/expenses/generate_expense_report.py --period monthly --month "2024-11"

# Seasonal campaigns
python tools/seasonal/generate_campaign.py --season winter --offer "Free battery test"

# Referral tracking
python tools/referrals/track_referrals.py --action log --referrer "John" --referee "Jane" --service "Brakes"
python tools/referrals/generate_rewards.py --referrer "John" --referee "Jane" --reward "$25 off"

# Tech productivity
python tools/tech_productivity/generate_summary.py --tech "Mike R." --jobs_completed 18 --hours_billed 42.5 --hours_actual 38 --revenue 8750

# Customer milestones
python tools/milestones/generate_outreach.py --milestone 1_year_anniversary --offer "10% off"
```

---

## Architecture: WAT Framework

- **W (Workflow)**: Each module has a `.md` workflow file defining the step-by-step SOP.
- **A (Agent)**: `CLAUDE.md` is the single brain — it routes to the right module on demand.
- **T (Tools)**: Python scripts that do the actual work. One job per tool.

The agent reads only the workflow it needs, keeping context focused and outputs specific.

---

## Data Files

The `data/` folder stores persistent state:

| File | Purpose |
|------|---------|
| `shop_profile.json` | Shop name, contact, services, branding |
| `equipment_inventory.json` | Equipment tracking data |
| `parts_inventory.json` | Parts stock levels |
| `warranty_claims.json` | Warranty claim records |
| `expenses.json` | Expense log |
| `referrals.json` | Referral tracking |
| `tech_data.json` | Technician labor data |

---

## Built for AmericasBestShops.com

This engine is designed to be deployed to ABS platform members — independent auto repair shops, tire shops, RV dealers, and specialty automotive businesses.
