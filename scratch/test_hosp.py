import asyncio
from app.db.database import connect_db, get_hospitals_table
async def test():
    await connect_db()
    r = get_hospitals_table().select('*').limit(1).execute()
    print('COLUMNS:', r.data[0].keys() if r.data else 'empty')

if __name__ == '__main__':
    asyncio.run(test())
