import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Try to load local .env if it exists
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(url, key) if url and key else None
