import asyncio
from app.db.database import connect_db, get_donors_table, get_organ_registrations_table
from app.services import receiver_service
from app.schemas.receiver import DonorSearchRequest

async def run():
    await connect_db()
    
    # 1. Test search with state only
    req_state = DonorSearchRequest(
        organ_type="liver",
        blood_group="B+",
        state="Haryana",
        page=1,
        page_size=10
    )
    res_state = await receiver_service.search_donors(req_state)
    print(f"SEARCH (State only): Found {len(res_state['items'])} items")
    
    # 2. Test search with state and city
    req_city = DonorSearchRequest(
        organ_type="liver",
        blood_group="B+",
        state="Haryana",
        city="Gurgaon",
        page=1,
        page_size=10
    )
    res_city = await receiver_service.search_donors(req_city)
    print(f"SEARCH (State & City): Found {len(res_city['items'])} items")

if __name__ == '__main__':
    asyncio.run(run())
