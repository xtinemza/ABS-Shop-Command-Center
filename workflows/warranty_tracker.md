# Warranty Claims Tracker & Documentation System — Workflow
## Module 12 | Shop Command Center

**Purpose:** Track parts and labor warranty claims from initiation through vendor reimbursement. Log every claim with full documentation, monitor status, follow up on aged claims, and generate recovery reports.

---

## Input / Output Summary

| Input | Source |
|-------|--------|
| Claim details (part, vendor, dates, cost, vehicle) | User provides |
| Status updates | User provides |
| Report period | User selects |

| Output | Location |
|--------|----------|
| Warranty claims database | `data/warranty_claims.json` |
| Warranty report (text) | `output/warranty/warranty_report_[period].txt` |

---

## Phase 1 — Load Context and Determine Request Type

**Step 1.1** — Load the shop profile:
```bash
python tools/shared/load_profile.py
```

**Step 1.2** — Ask the user:
> What do you need for warranty tracking today?
> - **A** — Log a new claim
> - **B** — Update an existing claim's status
> - **C** — List all open claims
> - **D** — Generate a warranty recovery report

Wait for selection before proceeding.

---

## Phase 2A — Log a New Claim

Collect the following from the user (ask for missing fields):

| Field | Required? | Notes |
|-------|-----------|-------|
| Part name | Yes | e.g., "Alternator - Reman" |
| Part number | Optional | From invoice |
| Vendor | Yes | e.g., "O'Reilly Auto Parts" |
| Installation date | Yes | YYYY-MM-DD |
| Failure date | Yes | YYYY-MM-DD |
| Warranty period (days) | Optional | Default: 365 |
| Part cost | Yes | Dollar amount |
| Vehicle | Yes | Year/Make/Model |
| Customer name | Optional | Links claim to customer |
| Failure description | Yes | What failed and how |

**Step 2A.1** — Log the claim:
```bash
python tools/warranty/track_claims.py \
    --action add \
    --part "Alternator - Remanufactured" \
    --part_number "ALT-8912" \
    --vendor "O'Reilly Auto Parts" \
    --install_date "2025-01-15" \
    --failure_date "2025-06-20" \
    --warranty_period_days 365 \
    --cost 189.99 \
    --vehicle "2018 Honda Accord" \
    --customer "Maria Gonzalez" \
    --description "Premature failure — not charging, battery light on"
```

**Step 2A.2** — Confirm claim ID to user and advise next steps:
- Contact vendor to initiate claim
- Keep original invoice and installation record
- Document failure evidence (photos recommended)

---

## Phase 2B — Update a Claim

Ask the user for the claim ID and the new status. Valid statuses:
- `New` — Just logged, not yet contacted vendor
- `Submitted` — Vendor contacted, claim filed
- `Pending Vendor` — Awaiting vendor response
- `Parts Requested` — Replacement part requested
- `Resolved` — Claim approved, reimbursed or replacement received
- `Denied` — Vendor denied the claim
- `Escalated` — Dispute in progress

```bash
python tools/warranty/track_claims.py \
    --action update \
    --claim_id "WC-001" \
    --status "Submitted" \
    --notes "Called O'Reilly, spoke with commercial rep, given RMA #44821"
```

If reimbursement was received, also pass `--reimbursement 189.99`.

---

## Phase 2C — List Open Claims

```bash
python tools/warranty/track_claims.py --action list
```

Display the output to the user. Flag any claims aged over 30 or 60 days and suggest follow-up.

---

## Phase 2D — Generate Warranty Report

Ask the user which period they want:
- `month` — Current calendar month
- `quarter` — Current quarter
- `year` — Current year
- `all` — All time

Optionally filter by status:
```bash
python tools/warranty/generate_warranty_report.py --period month
python tools/warranty/generate_warranty_report.py --period quarter --status open
python tools/warranty/generate_warranty_report.py --period all
```

---

## Phase 3 — Confirm and Summarize

After any action, confirm:
- What was logged or updated
- File path of any saved report
- Any claims flagged for follow-up (aged 30+ days)

**Always ask:** "Is there another claim to log, or would you like a report?"

---

## Edge Case Rules

**If the vendor is unknown:** Log the claim with vendor as "Unknown — To Confirm" and flag it. Don't block the workflow.

**If failure date precedes install date:** Flag the error and ask the user to verify dates before saving.

**If a claim is denied:** Update status to `Denied`, log the denial reason in notes, and advise the user whether escalation is appropriate (especially if the part failed within warranty period with documented evidence).

**If reimbursement is partial:** Record actual reimbursement amount. Report will show both claimed and recovered values.

**If no claims exist:** On report request, generate an empty report with a note that no claims have been logged. Do not error out.

---

## Quality Standards

- Every claim must have: part name, vendor, install date, failure date, cost, and a description. No incomplete claims.
- Status history must be maintained. Every update appends to the claim's history log — never overwrites.
- Reports must show: claims by vendor, resolution rate, total claimed vs. recovered, aged claims (30/60/90+ days).
- Never fabricate reimbursement amounts. Mark recovered value as $0 until confirmed.
- Aging flags: 30+ days = review needed, 60+ days = escalate, 90+ days = consider write-off review.
