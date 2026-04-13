
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

async def test_supabase_connection():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("[FAIL] SUPABASE_URL or SUPABASE_KEY not found in .env")
        return

    print(f"Connecting to: {url}")
    try:
        supabase: Client = create_client(url, key)
        # Try a simple query
        response = supabase.table("users").select("*", count="exact").limit(1).execute()
        print(f"[SUCCESS] Supabase connection successful!")
        print(f"Found {response.count} users in the database.")
    except Exception as e:
        print(f"[FAIL] Supabase connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_supabase_connection())
