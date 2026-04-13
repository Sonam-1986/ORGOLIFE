import asyncio
from app.db.database import connect_db, get_hospitals_table

async def test():
    await connect_db()
    
    fields_to_test = [
        "specializations",
        "aadhaar_path",
        "pan_path",
        "cert_path",
        "is_active",
        "total_approvals",
        "total_rejections"
    ]
    
    for field in fields_to_test:
        test_doc = {
            "name": "Test",
            "registration_number": f"REG-TEST-{field}",
            field: [] if field == "specializations" else (1 if "total" in field else ("" if "path" in field else True))
        }
        try:
            r = get_hospitals_table().insert(test_doc).execute()
            print(f'{field}: SUCCESS')
            get_hospitals_table().delete().eq('id', r.data[0]['id']).execute()
        except Exception as e:
            print(f'{field}: FAIL -> {e}')

if __name__ == '__main__':
    asyncio.run(test())
