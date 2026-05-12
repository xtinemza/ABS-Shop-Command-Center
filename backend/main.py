import sys
import os
import logging

# ── Structured logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("shop_command_center")

# Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

# Ensure project root is on the path so tool imports work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_ROOT = os.path.join(PROJECT_ROOT, "tools")
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, TOOLS_ROOT)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    _limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    _rate_limiting_available = True
except ImportError:
    _limiter = None
    _rate_limiting_available = False
    logger.warning("slowapi not installed — rate limiting disabled. Run: pip install slowapi")

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
    ai_modules,
    service_prices,
)

app = FastAPI(
    title="Shop Command Center API",
    version="1.0.0",
    description="AI-powered operations suite for independent auto repair shops.",
)

# Attach rate limiter if available
if _rate_limiting_available:
    app.state.limiter = _limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled: 60 requests/minute per IP")

# Global exception handler — never leak internal details to the client
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred. Please try again."})

_DEFAULT_ORIGINS = ",".join([
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "https://absshopscommandcenter.netlify.app",
    "https://abs-shop-command-center.netlify.app",
])
_allowed_origins = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", _DEFAULT_ORIGINS).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("← %s %s %s", request.method, request.url.path, response.status_code)
    return response

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
app.include_router(ai_modules.router, prefix="/api", tags=["AI Modules"])
app.include_router(service_prices.router, prefix="/api", tags=["Knowledge Base"])


@app.get("/")
def root():
    return {"message": "Shop Command Center API", "docs": "/docs"}
