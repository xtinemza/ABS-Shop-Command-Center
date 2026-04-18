# Shop Command Center — Backend API

FastAPI backend wrapping all 17 Shop Command Center operational modules.

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Start the server

**Windows:**
```bat
start.bat
```

**macOS / Linux:**
```bash
bash start.sh
```

**Or directly:**
```bash
python -m uvicorn main:app --reload --port 8000
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Profile & Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/profile` | Load shop profile |
| POST | `/api/profile/save` | Update profile fields |
| POST | `/api/setup` | First-time setup |
| GET | `/api/health` | Health check + setup status |

### Module Endpoints
| # | Module | Method | Path |
|---|--------|--------|------|
| 1 | Appointment Reminders | POST | `/api/appointments/generate` |
| 2 | Welcome Kit | POST | `/api/welcome-kit/generate` |
| 3 | Wait Time Comms | POST | `/api/wait-time/generate` |
| 4 | Declined Services | POST | `/api/declined/generate` |
| 5 | Service History | POST | `/api/service-history/generate` |
| 6 | Estimate Narrator | POST | `/api/estimates/generate` |
| 7 | Inspection Forms | POST | `/api/inspection/generate` |
| 8 | Recall Check | POST | `/api/recall/check` |
| 8 | Recall Notify | POST | `/api/recall/notify` |
| 9 | Equipment Logger | POST | `/api/equipment/action` |
| 10 | SOP Library | POST | `/api/sop/generate` |
| 11 | Parts Inventory | POST | `/api/parts/inventory` |
| 11 | Purchase Orders | POST | `/api/parts/po` |
| 12 | Warranty Claims | POST | `/api/warranty/claims` |
| 12 | Warranty Report | POST | `/api/warranty/report` |
| 13 | Expense Log | POST | `/api/expenses/log` |
| 13 | Expense Report | POST | `/api/expenses/report` |
| 14 | Seasonal Campaigns | POST | `/api/seasonal/generate` |
| 15 | Referral Tracking | POST | `/api/referrals/track` |
| 15 | Referral Rewards | POST | `/api/referrals/rewards` |
| 16 | Tech Productivity | POST | `/api/tech/summary` |
| 17 | Customer Milestones | POST | `/api/milestones/generate` |

## Response Format

All module endpoints return:
```json
{
  "success": true,
  "output": "Captured stdout from the tool...",
  "files": ["/absolute/path/to/file.txt"],
  "content": {
    "filename.txt": "full file content here"
  },
  "error": null
}
```

Errors are returned as 200 responses with `success: false` and the error message in the `error` field.

## Notes

- All generated files are saved to `output/<module>/` in the project root.
- The `content` dict in each response contains the full text of every file generated, so the frontend can display results without a second request.
- The shop profile (`data/shop_profile.json`) must exist before running modules. Use `POST /api/setup` or `POST /api/profile/save` to create it.
