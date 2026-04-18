# Parts Inventory & Reorder Alert System — Workflow SOP
## Module 11 | Shop Command Center

**Purpose:** Track commonly stocked parts with quantities, reorder thresholds, vendor info, and cost. Generate instant reorder alerts when stock drops low and produce formatted Purchase Orders grouped by vendor, ready to send or call in.

---

## Inputs Required

| Field | Required | Notes |
|-------|----------|-------|
| Part number | Yes | Exact P/N from vendor catalog |
| Part name | Yes | Descriptive name (e.g., "Brake Pads - Ceramic Front") |
| Category | Optional | oil_filters, brake_pads, belts, fluids, etc. |
| Quantity on hand | Yes (add/update) | Current stock count |
| Reorder point | Yes (add) | Quantity at or below which to trigger reorder |
| Preferred vendor | Yes (add) | Vendor name |
| Unit cost | Yes (add) | Your cost per unit |

## Outputs Produced

| File | Location | Description |
|------|----------|-------------|
| `data/parts_inventory.json` | `data/` | Live inventory database |
| `inventory_report_YYYY-MM-DD.txt` | `output/parts_inventory/` | Full inventory status report |
| `inventory_report.txt` | `output/parts_inventory/` | Current copy (always up to date) |
| `PO_<Vendor>_<date>.txt` | `output/parts_inventory/` | Purchase order per vendor |

---

## Phase 1 — Load Context

### Step 1: Load shop profile
```bash
python tools/shared/load_profile.py
```

### Step 2: Determine starting point
Ask the user:
- "Do you have an existing parts list, or should we start with common auto repair shop defaults?"
- "What's your shop specialty? (General, European, domestic trucks, etc.)"

**If starting from scratch**, suggest building the initial inventory from these common categories:
- Oil filters (common fitments)
- Synthetic and conventional motor oil (5W-30, 5W-20, 0W-20, 10W-30)
- Air filters
- Cabin air filters
- Brake pads (ceramic and semi-metallic, front and rear)
- Serpentine belts (common sizes)
- Wiper blades
- Spark plugs (common fitments)
- Coolant (green, orange/HOAT, pink/OAT)
- Brake fluid (DOT 3, DOT 4)

---

## Phase 2 — Build or Update Inventory

### Add a part
```bash
python tools/parts_inventory/track_inventory.py \
    --action add \
    --part_number "MF-51394" \
    --part_name "Oil Filter - Motorcraft FL-820S" \
    --category "oil_filters" \
    --quantity 12 \
    --reorder_point 4 \
    --preferred_vendor "AutoZone Commercial" \
    --cost 6.49
```

### Update quantity (e.g., after receiving stock or using parts)
```bash
python tools/parts_inventory/track_inventory.py \
    --action update \
    --part_number "MF-51394" \
    --quantity 8
```

### Check what needs to be reordered
```bash
python tools/parts_inventory/track_inventory.py --action reorder_check
```

### List all inventory
```bash
python tools/parts_inventory/track_inventory.py --action list
```

### Generate full inventory report
```bash
python tools/parts_inventory/track_inventory.py --action report
```

---

## Phase 3 — Generate Purchase Orders

When stock is low, generate a Purchase Order for one or more vendors:

### Auto-generate POs for all low-stock parts (grouped by vendor)
```bash
python tools/parts_inventory/generate_po.py \
    --vendor "AutoZone Commercial"
```

### Manual PO with specific line items
```bash
python tools/parts_inventory/generate_po.py \
    --vendor "AutoZone Commercial" \
    --items '[{"part_number": "MF-51394", "part_name": "Oil Filter FL-820S", "quantity": 12, "unit_cost": 6.49}]' \
    --notes "Urgent — needed for fleet account jobs this week"
```

Each PO is saved as `output/parts_inventory/PO_<Vendor>_<YYYYMMDD>.txt` and includes:
- Shop header with contact info
- Auto-generated PO number (PO-YYYYMMDD-XXX)
- Vendor info section
- Line items table with quantities and costs
- Order total
- Authorization signature line

---

## Phase 4 — Review & Act

After generating the reorder check and POs:
1. Present the reorder alert to the user.
2. Ask: "Do you want me to generate a Purchase Order for these items?"
3. Confirm the vendor and quantities before generating the PO.
4. After the PO is generated, ask: "Would you like me to update the quantity for any parts you've already ordered and received?"

---

## Quality Standards

- **Never fabricate part numbers.** Only use part numbers the user provides.
- **Reorder point recommendations**: If the user doesn't know, suggest: 2× weekly usage rate. For fast-movers, 3× weekly usage.
- **PO numbers are auto-generated** in format PO-YYYYMMDD-XXX and are unique per run.
- **Every PO must include**: Shop name, PO number, date, vendor, line items (P/N, description, qty, unit cost, line total), grand total, and authorization signature line.
- **No [INSERT] placeholders in final output** — use real shop data from the profile.

---

## Decision Rules

| Situation | Action |
|-----------|--------|
| No inventory file exists | `track_inventory.py` initializes it on first add |
| Part already exists (add) | Error — use `--action update` instead |
| Part not found (update) | Error with clear message; suggest `--action list` to find correct P/N |
| Vendor in PO not in inventory | Accept vendor override — user may be ordering from a new source |
| User wants to remove a part | Use `--action update --quantity 0` or simply stop tracking — the data file is editable |
| PO for parts not at reorder point | Accept — user may want to top off proactively |
| Multiple vendors for same part | Store primary vendor in inventory; note alternate vendor in part name or use --notes on PO |
