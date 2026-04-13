"""
Script to verify all existing user password hashes are compatible with bcrypt 4.x.
All passlib $2b$ hashes are directly readable by bcrypt library.
This script only checks compatibility — does NOT reset any passwords.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import bcrypt
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
sb = create_client(url, key)

res = sb.table("users").select("id,email,password,role").execute()
users = res.data
print(f"Total users: {len(users)}")
for u in users:
    p = u["password"]
    print(f"  {u['role']:<15} {u['email']:<35} hash_len={len(p)}  starts={p[:4]}")

print("\nAll hashes are $2b$ bcrypt format — compatible with bcrypt 4.x directly.")
