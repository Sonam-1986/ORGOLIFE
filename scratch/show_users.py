import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

try:
    print("Fetching users from Supabase...")
    res = supabase.table("users").select("id, name, email, role, status, created_at").execute()
    
    if not res.data:
        print("No users found.")
    else:
        print(f"Found {len(res.data)} registered users:")
        # Format the output into a readable table
        # Find max widths for columns
        max_name = max(len(str(u.get('name', ''))) for u in res.data)
        max_name = max(max_name, 4)
        
        max_email = max(len(str(u.get('email', ''))) for u in res.data)
        max_email = max(max_email, 5)
        
        print("-" * (max_name + max_email + 45))
        print(f"{'NAME':<{max_name}} | {'EMAIL':<{max_email}} | {'ROLE':<15} | {'STATUS':<10}")
        print("-" * (max_name + max_email + 45))
        
        for user in res.data:
            print(f"{str(user.get('name')):<{max_name}} | {str(user.get('email')):<{max_email}} | {str(user.get('role')):<15} | {str(user.get('status')):<10}")
            
except Exception as e:
    print(f"Error fetching users: {e}")
