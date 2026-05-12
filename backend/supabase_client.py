import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Try to load local .env if it exists
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

if not url or not key:
    raise RuntimeError(
        "Missing required environment variables: "
        + (", ".join(v for v, val in [("SUPABASE_URL", url), ("SUPABASE_KEY", key)] if not val))
        + ". Set them in backend/.env or your deployment environment."
    )

supabase: Client = create_client(url, key)
