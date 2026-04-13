import asyncio
from app.db.database import connect_db
from app.services.auth_service import register_full_receiver
from fastapi import UploadFile
import io

async def test():
    await connect_db()
    # Mock UploadFile
    fake_file1 = UploadFile(filename="aadhaar.jpg", file=io.BytesIO(b"\xff\xd8\xff\xe0fakecontent"))
    fake_file2 = UploadFile(filename="pan.jpg", file=io.BytesIO(b"\xff\xd8\xff\xe0fakecontent2"))
    fake_file3 = UploadFile(filename="medical.jpg", file=io.BytesIO(b"\xff\xd8\xff\xe0fakecontent3"))
    
    try:
        res = await register_full_receiver(
            name='Test Recv',
            email='testrecv222@recv.com',
            password='12345678',
            contact_number='1234567890',
            age=30,
            father_name='Test Father',
            state='State',
            city='City',
            aadhaar_file=fake_file1,
            pan_file=fake_file2,
            medical_file=fake_file3,
            aadhaar_number='123412341234',
            pan_number='ABCDE1234F'
        )
        print('SUCCESS RECV!', res)
    except Exception as e:
        print('FAIL RECV!', type(e), str(e))

if __name__ == '__main__':
    asyncio.run(test())
