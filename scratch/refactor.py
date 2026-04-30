import os
import re

ROUTERS_DIR = r"c:\Users\chris\Downloads\Claude Shop Command Center\backend\routers"

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "from auth import get_current_user" not in content and "profile.py" not in filepath and "service_prices.py" not in filepath:
        # Add imports
        import_stmt = "from fastapi import APIRouter, Depends\nfrom auth import get_current_user\nfrom supabase_client import supabase\n"
        content = re.sub(r"from fastapi import APIRouter", import_stmt, content)

        # Replace _load_profile definition
        load_profile_regex = r"def _load_profile\(\) -> dict:.*?return \{\}"
        new_load_profile = """def _load_profile(user_id: str) -> dict:
    try:
        res = supabase.table("profiles").select("shop_info").eq("id", user_id).execute()
        return res.data[0].get("shop_info", {}) if res.data else {}
    except Exception:
        return {}"""
        content = re.sub(load_profile_regex, new_load_profile, content, flags=re.DOTALL)

        # Replace router endpoint signatures
        content = re.sub(r"(@router\.(post|get|delete)\(.*?\)\s+def \w+\()body: \w+(.*?)\):", r"\1body: \g<3>, user=Depends(get_current_user)): ", content)
        content = re.sub(r"(@router\.(post|get|delete)\(.*?\)\s+def \w+\(\)):", r"\1user=Depends(get_current_user)):", content)

        # Fix the body type hint matching which was greedy
        # A simpler way is to just find all def ...() and inject user=Depends(get_current_user)
        # But we already did a regex. Let's do a safer pass:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("@router."):
                # the next line is def something(...)
                if i+1 < len(lines) and "def " in lines[i+1]:
                    sig_line = lines[i+1]
                    if "user=Depends(get_current_user)" not in sig_line:
                        if "(body:" in sig_line or "(key:" in sig_line or "(file:" in sig_line:
                            sig_line = sig_line.replace("):", ", user=Depends(get_current_user)):")
                        else:
                            sig_line = sig_line.replace("():", "(user=Depends(get_current_user)):")
                        lines[i+1] = sig_line

        content = '\n'.join(lines)

        # Replace _load_profile() calls
        content = content.replace("_load_profile()", "_load_profile(user.id)")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

for filename in os.listdir(ROUTERS_DIR):
    if filename.endswith(".py") and filename not in ("__init__.py", "profile.py", "service_prices.py"):
        process_file(os.path.join(ROUTERS_DIR, filename))
