import requests
import json

base = "http://localhost:8000/api/v1"

# 1. Register a new admin
print("Registering new admin...")
fd = {
    "name": "Test Admin",
    "email": "testadmin@exam.com",
    "password": "12345678",
    "contact_number": "1234567890",
    "hospital_name": "AIIMS Delhi",
    "hospital_registration_number": "AIIMS-DL-TEST",
    "hospital_state": "Delhi",
    "hospital_city": "New Delhi",
    "hospital_address": "Test addr",
    "hospital_contact": "011-222222"
}
r1 = requests.post(f"{base}/auth/register/admin", data=fd)
print("Reg status:", r1.status_code, r1.text)

# 2. Login
print("\nLogging in...")
log_data = {
    "email": "testadmin@exam.com",
    "password": "12345678",
    "hospital_code": "AIIMS-DL-TEST"
}
r2 = requests.post(f"{base}/auth/login/admin", json=log_data)
print("Login status:", r2.status_code, r2.text)

if r2.status_code == 200:
    token = r2.json()["access_token"]
    
    # 3. Access dashboard
    print("\nFetching dashboard (/admin/donors)...")
    r3 = requests.get(f"{base}/admin/donors", headers={"Authorization": f"Bearer {token}"})
    print("Dash status:", r3.status_code, r3.text[:200])
