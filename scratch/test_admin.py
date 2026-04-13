import asyncio
from app.db.database import connect_db
from app.services.auth_service import register_hospital_admin
from app.schemas.admin import HospitalAdminSignup

async def test():
    await connect_db()
    payload = HospitalAdminSignup(
        name='Test Admin',
        email='testadmin114@admin.com',
        password='12345678',
        contact_number='1234567890',
        hospital_name='Test Hosp',
        hospital_registration_number='REG123114',
        hospital_state='State',
        hospital_city='City',
        hospital_address='Address123',
        hospital_contact='0987654321'
    )
    res = await register_hospital_admin(payload)
    print('SUCCESS', res)

if __name__ == '__main__':
    asyncio.run(test())
