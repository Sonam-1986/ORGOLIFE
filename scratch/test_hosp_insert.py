import asyncio
from app.db.database import connect_db, get_hospitals_table

async def test():
    await connect_db()
    # test insert
    test_doc = {
        "name": "Test",
        "state": "State",
        "city": "City",
        "address": "Adr",
        "contact_number": "123",
        "registration_number": "REG-TEST-12345678"
    }
    try:
        r = get_hospitals_table().insert(test_doc).execute()
        print('SUCCESS CORE')
        get_hospitals_table().delete().eq('id', r.data[0]['id']).execute()
    except Exception as e:
        print('FAIL CORE', e)

if __name__ == '__main__':
    asyncio.run(test())
