import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Add parent dir to path to import app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    sys.exit(1)

try:
    supabase = create_client(url, key)
    res = supabase.table("users").select("count", count="exact").limit(1).execute()
    print(f"Connection successful! Found {res.count} users.")
except Exception as e:
    print(f"Connection failed: {e}")

