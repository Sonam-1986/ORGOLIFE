import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env file.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def reset_database():
    print("Starting database reset...")
    
    # Order of deletion to respect foreign keys
    tables = [
        "organ_registrations",
        "receivers",
        "donors",
        "hospitals",
        "users"
    ]
    
    for table in tables:
        print(f"Clearing table: {table}")
        try:
            # Delete all rows (empty filter deletes everything)
            res = supabase.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            # Note: We use a non-existent ID filter to bypass the 'delete everything same as no filter' restriction in some settings
            # or just use .neq('id', 'some-uuid')
        except Exception as e:
            print(f"Error clearing {table}: {e}")
            
    print("\nDatabase reset complete. All user, donor, receiver, and hospital data cleared.")

if __name__ == "__main__":
    confirm = input("Are you SURE you want to delete ALL data? (yes/delete): ")
    if confirm.lower() in ["yes", "delete"]:
        reset_database()
    else:
        print("Reset aborted.")
