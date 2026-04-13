import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.services import auth_service
from app.schemas.admin import HospitalAdminSignup
from app.db.database import connect_db

async def debug():
    await connect_db()
    
    payload = HospitalAdminSignup(
        name="Dr. Akansha Rai",
        email="akansha12@gmail.com",
        password="12345678",
        contact_number="9876543210",
        hospital_name="AIIMS Delhi",
        hospital_registration_number="AIIMS-DL-01",
        hospital_state="Delhi",
        hospital_city="New Delhi",
        hospital_address="Ansari Nagar, New Delhi",
        hospital_contact="011-26588500",
        aadhaar_number="123456789012",
        pan_number="ABCDE1234F"
    )
    
    try:
        print("Attempting to register hospital admin...")
        result = await auth_service.register_hospital_admin(payload)
        print("Success:", result)
    except Exception as e:
        print("Registration Failed!")
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug())
