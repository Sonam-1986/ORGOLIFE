import asyncio
from app.db.database import connect_db, get_donors_table
from app.services import receiver_service

async def run():
    await connect_db()
    # Get a donor ID
    donors = get_donors_table().select("id").limit(1).execute()
    if not donors.data:
        print("No donors found in DB")
        return
    
    donor_id = str(donors.data[0]["id"])
    print(f"Testing for donor_id: {donor_id}")
    
    # Test search response
    from app.schemas.receiver import DonorSearchRequest
    from app.models.organ import OrganName, BloodGroup
    
    # We need a matched organ to test search, let's just test the detail function
    profile = await receiver_service.get_donor_profile_for_receiver(donor_id)
    print("DETAIL RESPONSE:", profile)
    
    # Assertions
    expected = ["name", "father_name", "age", "contact_number", "status", "medical_report_url"]
    for field in expected:
        if field not in profile:
            print(f"MISSING FIELD: {field}")
        else:
            print(f"FOUND FIELD: {field} = {profile[field]}")

if __name__ == '__main__':
    asyncio.run(run())
