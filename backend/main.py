import sys
import os

# Ensure project root is on the path so tool imports work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_ROOT = os.path.join(PROJECT_ROOT, "tools")
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, TOOLS_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    profile,
    appointments,
    welcome_kit,
    wait_time,
    declined,
    service_history,
    estimates,
    inspection,
    recall,
    equipment,
    sop,
    parts,
    warranty,
    expenses,
    seasonal,
    referrals,
    tech,
    milestones,
)

app = FastAPI(
    title="Shop Command Center API",
    version="1.0.0",
    description="AI-powered operations suite for independent auto repair shops.",
)

app.add_middleware(
    CORSMiddleware,
allow_origins=["http://localhost:3000","https://absshopscommandcenter.netlify.app/",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers
app.include_router(profile.router, prefix="/api", tags=["Profile & Health"])
app.include_router(appointments.router, prefix="/api", tags=["1 - Appointments"])
app.include_router(welcome_kit.router, prefix="/api", tags=["2 - Welcome Kit"])
app.include_router(wait_time.router, prefix="/api", tags=["3 - Wait Time"])
app.include_router(declined.router, prefix="/api", tags=["4 - Declined Services"])
app.include_router(service_history.router, prefix="/api", tags=["5 - Service History"])
app.include_router(estimates.router, prefix="/api", tags=["6 - Estimates"])
app.include_router(inspection.router, prefix="/api", tags=["7 - Inspection"])
app.include_router(recall.router, prefix="/api", tags=["8 - Recall"])
app.include_router(equipment.router, prefix="/api", tags=["9 - Equipment"])
app.include_router(sop.router, prefix="/api", tags=["10 - SOP"])
app.include_router(parts.router, prefix="/api", tags=["11 - Parts"])
app.include_router(warranty.router, prefix="/api", tags=["12 - Warranty"])
app.include_router(expenses.router, prefix="/api", tags=["13 - Expenses"])
app.include_router(seasonal.router, prefix="/api", tags=["14 - Seasonal"])
app.include_router(referrals.router, prefix="/api", tags=["15 - Referrals"])
app.include_router(tech.router, prefix="/api", tags=["16 - Tech Productivity"])
app.include_router(milestones.router, prefix="/api", tags=["17 - Milestones"])


@app.get("/")
def root():
    return {"message": "Shop Command Center API", "docs": "/docs"}
