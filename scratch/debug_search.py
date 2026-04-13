import asyncio
from app.db.database import connect_db, get_donors_table, get_organ_registrations_table, get_users_table

async def run():
    await connect_db()
    
    # Check all organ registrations
    res_o = get_organ_registrations_table().select("*").execute()
    print("--- ORGAN REGISTRATIONS ---")
    for o in res_o.data:
        print(f"ID: {o['id']}, DonorID: {o['donor_id']}, Organ: {o['organ_name']}, Blood: {o['blood_group']}, State: {o['state']}, City: {o['city']}, Available: {o['is_available']}")
        
    # Check all donors
    res_d = get_donors_table().select("*").execute()
    print("\n--- DONORS ---")
    for d in res_d.data:
        print(f"ID: {d['id']}, Status: {d['status']}, Verified: {d['verified']}")

if __name__ == '__main__':
    asyncio.run(run())
