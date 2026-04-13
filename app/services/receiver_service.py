"""
Receiver service — profile creation and donor search engine.
"""
import logging
from typing import Optional, List
from fastapi import HTTPException, UploadFile, status
from app.db.database import (
    get_users_table, get_receivers_table,
    get_donors_table, get_organ_registrations_table
)
from app.models.receiver import receiver_document
from app.models.user import UserRole
from app.schemas.receiver import ReceiverSignupStep1, DonorSearchRequest
from app.services.file_service import save_upload
from app.utils.masking import mask_aadhaar
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


# ── Step 1: Receiver Registration ────────────────────────────────

async def register_receiver(
    user_id: str,
    data: ReceiverSignupStep1,
    aadhaar_file: UploadFile,
    pan_file: UploadFile,
    medical_file: UploadFile,
) -> dict:
    """Validate user and create receiver profile with uploaded documents."""
    users = get_users_table()
    user_res = users.select("*").eq("id", user_id).execute()
    user = user_res.data[0] if user_res.data else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    users.update({"role": UserRole.RECEIVER}).eq("id", user_id).execute()

    aadhaar_path = await save_upload(aadhaar_file, "aadhaar", user_id, "aadhaar_card")
    pan_path = await save_upload(pan_file, "pan", user_id, "pan_card")
    medical_path = await save_upload(medical_file, "medical_reports", user_id, "medical_report")

    doc = receiver_document(
        user_id=user_id,
        age=data.age,
        father_name=data.father_name,
        state=data.state,
        city=data.city,
        aadhaar_card_path=aadhaar_path,
        pan_card_path=pan_path,
        medical_report_path=medical_path,
        aadhaar_number=data.aadhaar_number,
        pan_number=data.pan_number,
    )
    receivers = get_receivers_table()
    result = receivers.insert(doc).execute()

    logger.info(f"Receiver registered: user_id={user_id}")
    return {
        "user_id": user_id,
        "receiver_id": str(result.data[0]["id"]),
        "message": "Receiver registered successfully. You can now search for donors.",
    }


# ── Step 2: Donor Search ──────────────────────────────────────────

async def search_donors(req: DonorSearchRequest) -> dict:
    """
    Search organ_registrations with filters, JOIN user + donor data,
    return masked results with pagination.
    """
    organs_table = get_organ_registrations_table()
    donors_table = get_donors_table()
    users_table = get_users_table()

    try:
        logger.info(f"🔍 Starting donor search. Filters: Organ={req.organ_type}, Blood={req.blood_group}, City={req.city}")
        # Fetch all available organ registrations
        res_all = organs_table.select("*").eq("is_available", True).execute()
        organs = res_all.data
        logger.info(f"📊 DATABASE CHECK: Found {len(organs)} available organs total.")
    except Exception as e:
        logger.error(f"❌ DATABASE ERROR in search_donors: {e}")
        return paginate_response([], 0, req.page, req.page_size)

    scored_results = []
    for organ in organs:
        donor_id = organ.get("donor_id")
        if not donor_id:
            continue

        # Fetch donor profile
        donor_q = donors_table.select("*").eq("id", donor_id)
        if req.verified_donor == "yes":
            donor_q = donor_q.eq("verified", True).ilike("status", "approved")
        elif req.verified_donor == "no":
            donor_q = donor_q.eq("verified", False)
            
        res = donor_q.execute()
        donor = res.data[0] if res.data else None
        if not donor:
            continue

        # Hospital name filter
        if req.hospital_name and req.hospital_name.lower() != "all":
            selected = [h.lower() for h in organ.get("hospitals_selected", [])]
            if not any(req.hospital_name.lower() in h for h in selected):
                continue

        # Fetch user
        user_res = users_table.select("*").eq("id", donor["user_id"]).execute()
        user = user_res.data[0] if user_res.data else None
        if not user:
            continue

        # ── Calculate Match Score for Ranking ────────────────────────
        score = 0
        if req.organ_type and req.organ_type.lower() != "all":
            if req.organ_type.lower() == organ["organ_name"].lower(): score += 100
        if req.blood_group and req.blood_group.lower() != "all":
            if req.blood_group.lower() == organ["blood_group"].lower(): score += 100
        if req.city and req.city.lower() != "all":
            if req.city.lower() == donor["city"].lower(): score += 50
        if req.state and req.state.lower() != "all":
            if req.state.lower() == donor["state"].lower(): score += 20

        # Determine verification status label
        d_status = (donor.get("status") or "pending").lower()
        verification_status = "legal" if (donor["verified"] and d_status == "approved") else "pending"
        if d_status == "rejected": verification_status = "illegal"

        scored_results.append({
            "score": score,
            "data": {
                "donor_id": str(donor_id),
                "donor_name": user["name"],
                "father_name": donor["father_name"],
                "aadhaar_number_masked": mask_aadhaar(donor.get("aadhaar_number", "")),
                "blood_group": organ["blood_group"],
                "organ": organ["organ_name"],
                "hospital_verified_by": donor.get("verified_by_hospital"),
                "verification_status": verification_status,
                "contact_number": user["contact_number"],
                "state": donor["state"],
                "city": donor["city"],
                "full_address": donor["full_address"],
            }
        })

    # Rank by score descending, then by creation date
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    
    total = len(scored_results)
    skip = (req.page - 1) * req.page_size
    final_items = [item["data"] for item in scored_results[skip : skip + req.page_size]]

    return paginate_response(final_items, total, req.page, req.page_size)


# ── Receiver profile ──────────────────────────────────────────────

async def get_receiver_profile(user_id: str) -> dict:
    receivers = get_receivers_table()
    res = receivers.select("*").eq("user_id", user_id).execute()
    receiver = res.data[0] if res.data else None
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver profile not found.")

    users = get_users_table()
    u_res = users.select("*").eq("id", user_id).execute()
    user = u_res.data[0] if u_res.data else None

    return {
        "receiver_id": str(receiver["id"]),
        "user_id": user_id,
        "name": user["name"],
        "email": user["email"],
        "age": receiver["age"],
        "father_name": receiver["father_name"],
        "contact_number": user["contact_number"],
        "state": receiver["state"],
        "city": receiver["city"],
        "created_at": receiver["created_at"],
    }


# ── Donor Profile for Receiver ────────────────────────────────────

async def get_donor_profile_for_receiver(donor_id: str) -> dict:
    """
    Return non-sensitive donor profile details for a receiver.
    Excludes Aadhaar/PAN paths but includes medical reports and identity masking.
    """
    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found.")

    users_table = get_users_table()
    user_res = users_table.select("*").eq("id", donor["user_id"]).execute()
    user = user_res.data[0] if user_res.data else None
    if not user:
        raise HTTPException(status_code=404, detail="Donor user data not found.")

    organs_table = get_organ_registrations_table()
    o_res = organs_table.select("*").eq("donor_id", donor_id).execute()
    organs = [{"name": o["organ_name"], "blood": o["blood_group"]} for o in o_res.data]
    
    from app.services.file_service import file_url
    from app.utils.masking import mask_aadhaar
    
    status = (donor.get("status") or "pending").upper()

    return {
        "donor_id": donor_id,
        "name": user["name"],
        "father_name": donor["father_name"],
        "age": donor["age"],
        "contact_number": user["contact_number"],
        "email": user["email"],
        "state": donor["state"],
        "city": donor["city"],
        "address": donor["full_address"],
        "registered_organs": ", ".join([f"{o['name'].upper()} ({o['blood']})" for o in organs]) or "None",
        "status": status,
        "verified_by_hospital": donor.get("verified_by_hospital"),
        "medical_report_url": file_url(donor.get("medical_report_path", "")),
        "aadhaar_masked": mask_aadhaar(donor.get("aadhaar_number", "")),
    }
