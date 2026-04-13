import os
import sys
import asyncio
from dotenv import load_dotenv
from supabase import create_client

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.services import auth_service
from app.schemas.auth import AdminLoginRequest
from app.db.database import connect_db

async def debug_login():
    await connect_db()
    
    payload = AdminLoginRequest(
        email="akansha12@gmail.com",
        password="password123", # Assuming this is correct for testing
        hospital_code="AIIMS-DL-01"
    )
    
    print(f"Testing login for {payload.email}...")
    try:
        # We manually call verify_password to see if it even gets past that
        # But let's just call login_admin and see it fail
        result = await auth_service.login_admin(payload)
        print("Login SUCCESS!")
        print(result)
    except Exception as e:
        print(f"Login FAILED with exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_login())
