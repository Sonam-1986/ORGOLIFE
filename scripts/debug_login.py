"""
Direct test of the admin login flow to surface the exact 500 error.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import asyncio
from app.db.database import connect_db, get_users_table, get_hospitals_table
from app.utils.password import verify_password

async def test_admin_login():
    await connect_db()
    
    email = "akansha12@gmail.com"
    password = "Akansha@1"
    hospital_code = "AIIMS-DL-01"
    
    print("Step 1: Fetch user by email...")
    users = get_users_table()
    response = users.select("*").eq("email", email.lower().strip()).execute()
    user = response.data[0] if response.data else None
    print(f"  User found: {user is not None}")
    if not user:
        print("  ERROR: User not found!")
        return
    
    print("Step 2: Verify password...")
    try:
        result = verify_password(password, user["password"])
        print(f"  Password match: {result}")
    except Exception as e:
        print(f"  ERROR in verify_password: {e}")
        traceback.print_exc()
        return
    
    if not result:
        print("  ERROR: Password doesn't match!")
        return
    
    print(f"  Role: {user['role']}")
    
    print("Step 3: Fetch hospital by admin_user_id + registration_number...")
    hospitals = get_hospitals_table()
    hosp_res = hospitals.select("*").eq("admin_user_id", str(user["id"])).eq("registration_number", hospital_code).execute()
    hospital = hosp_res.data[0] if hosp_res.data else None
    print(f"  Hospital found: {hospital is not None}")
    if not hospital:
        print("  ERROR: Hospital not found!")
        return
    
    print("Step 4: Build token response...")
    from app.utils.jwt_handler import create_access_token, create_refresh_token
    from app.core.config import settings
    from app.schemas.auth import TokenResponse
    user_id = str(user["id"])
    token_data = {
        "sub": user_id,
        "role": user["role"],
        "email": user["email"],
        "name": user["name"],
    }
    try:
        tr = TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            role=user["role"],
            user_id=user_id,
            name=user["name"],
        )
        print(f"  Token built OK: role={tr.role}")
    except Exception as e:
        print(f"  ERROR building token: {e}")
        traceback.print_exc()
        return
    
    print("\nAll steps PASSED - admin login should work!")

asyncio.run(test_admin_login())
