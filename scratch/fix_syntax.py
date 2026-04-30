import os
import re

ROUTERS_DIR = r"c:\Users\chris\Downloads\Claude Shop Command Center\backend\routers"

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We stripped the Request model names!
    # Let's read the file line by line and if we see `body: , user=`
    # We look for the class definition of a request model earlier in the file, or just parse it.
    # Actually, we can just look at the pydantic classes defined in the file.
    
    lines = content.split('\n')
    models = []
    for line in lines:
        if line.startswith("class ") and "(BaseModel):" in line:
            models.append(line.split(" ")[1].split("(")[0])
            
    # Now fix the signatures
    for i, line in enumerate(lines):
        if "def " in line and "body: , user=" in line:
            # We need to guess the model name based on the function name or just pick the best one
            # Usually there's only 1-2 models per file.
            # Let's find the model that corresponds to this function
            func_name = line.split("def ")[1].split("(")[0]
            
            # Simple heuristic:
            # Most files have 1 request model.
            best_model = models[0] if models else "dict"
            
            # Match specific ones if there are multiple
            if "SocialMediaRequest" in models and "social" in func_name: best_model = "SocialMediaRequest"
            elif "CTACopyRequest" in models and "cta" in func_name: best_model = "CTACopyRequest"
            elif "PromoRequest" in models and "promo" in func_name: best_model = "PromoRequest"
            elif "BlogRequest" in models and "blog" in func_name: best_model = "BlogRequest"
            elif "QueryRequest" in models and ("generate" in func_name or "repair" in func_name or "query" in func_name or "advisor" in func_name or "maint" in func_name): best_model = "QueryRequest"
            
            # For others, we can extract from the name of the file or just use the first model defined
            lines[i] = line.replace("body: , user=", f"body: {best_model}, user=")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Fixed {os.path.basename(filepath)}")

for filename in os.listdir(ROUTERS_DIR):
    if filename.endswith(".py"):
        fix_file(os.path.join(ROUTERS_DIR, filename))
