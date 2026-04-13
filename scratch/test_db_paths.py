import asyncio
from app.db.database import connect_db, get_donors_table
async def run():
    await connect_db()
    r = get_donors_table().select('*').execute()
    if r.data:
        for d in r.data[:3]:
            print(d.get('aadhaar_card_path'))

if __name__ == '__main__':
    asyncio.run(run())
