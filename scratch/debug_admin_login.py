import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

email = "akansha12@gmail.com"
hospital_code = "AIIMS-DL-01".strip()

print(f"--- Debugging login for {email} ---")

try:
    # 1. Check user
    res = supabase.table("users").select("*").eq("email", email).execute()
    if not res.data:
        print(f"User '{email}' not found.")
    else:
        user = res.data[0]
        print(f"User found: ID={user['id']}, Role={user['role']}, PasswordField={user.get('password')[:10] if user.get('password') else 'MISSING'}...")
        
        # 2. Check hospital
        h_res = supabase.table("hospitals").select("*").eq("admin_user_id", user["id"]).execute()
        if not h_res.data:
            print(f"Hospital not found for admin_user_id={user['id']}")
        else:
            hospital = h_res.data[0]
            print(f"Hospital found: ID={hospital['id']}, RegNum={hospital['registration_number']}")
            if hospital['registration_number'].strip() == hospital_code:
                print("Hospital code matches!")
            else:
                print(f"Hospital code mismatch! Expected '{hospital['registration_number']}', got '{hospital_code}'")

    # 3. Check all hospitals to see if code exists elsewhere
    h_all = supabase.table("hospitals").select("*").eq("registration_number", hospital_code).execute()
    if h_all.data:
        print(f"Hospital code '{hospital_code}' exists in DB for admin_user_id={h_all.data[0]['admin_user_id']}")
    else:
        print(f"Hospital code '{hospital_code}' not found in 'hospitals' table at all.")

except Exception as e:
    print(f"An error occurred during debugging: {e}")
    import traceback
    traceback.print_exc()
