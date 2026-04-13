import asyncio
import bcrypt
from app.db.database import get_users_table, connect_db, close_db

async def migrate_passwords():
    await connect_db()
    # Hash the new 8 digit password
    new_password = "12345678"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")
    
    users_table = get_users_table()
    
    # Let's get all users
    res = users_table.select("*").execute()
    users = res.data
    
    for u in users:
        print(f"Updating password for user: {u['email']}")
        users_table.update({"password": hashed_password}).eq("id", u["id"]).execute()
        
    print("All passwords successfully migrated to exactly 8 digits: 12345678")
    await close_db()

try:
    asyncio.run(migrate_passwords())
except Exception as e:
    print(e)
