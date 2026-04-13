import asyncio
from app.db.database import connect_db, get_donors_table, get_organ_registrations_table

async def run():
    await connect_db()
    
    # 1. Check organs
    res_o = get_organ_registrations_table().select("*").execute()
    print(f"DEBUG: Found {len(res_o.data)} organ registrations.")
    for o in res_o.data:
        print(f"  - Organ: {o['organ_name']}, Blood: {o['blood_group']}, State: {o['state']}, City: {o['city']}, ID: {o['id']}, DonorID: {o['donor_id']}")
        
    # 2. Check donors
    res_d = get_donors_table().select("*").execute()
    print(f"\nDEBUG: Found {len(res_d.data)} donors.")
    for d in res_d.data:
        print(f"  - DonorID: {d['id']}, Status: {d['status']}, Verified: {d['verified']}")

if __name__ == '__main__':
    asyncio.run(run())
