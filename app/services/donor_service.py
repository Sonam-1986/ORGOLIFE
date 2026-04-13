import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException, status, UploadFile
from app.db.database import (
    get_users_table, get_donors_table,
    get_organ_registrations_table
)
from app.models.donor import donor_document, DonorStatus
from app.models.organ import organ_registration_document
from app.models.user import UserRole
from app.schemas.donor import DonorSignupStep1, OrganRegistrationRequest
from app.schemas.auth import TokenResponse
from app.services.file_service import save_upload, file_url
from app.utils.masking import mask_aadhaar
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


# ── Step 1: Full donor onboarding (user + profile + file uploads) ─

async def register_donor(
    user_id: str,
    data: DonorSignupStep1,
    aadhaar_file: UploadFile,
    pan_file: UploadFile,
    medical_file: UploadFile,
) -> dict:
    """
    1. Verify user exists
    2. Save uploaded documents
    3. Create donor profile
    """
    users = get_users_table()
    user_res = users.select("*").eq("id", user_id).execute()
    user = user_res.data[0] if user_res.data else None
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    users.update({"role": UserRole.DONOR}).eq("id", user_id).execute()

    # Save files to disk
    aadhaar_path = await save_upload(aadhaar_file, "aadhaar", user_id, "aadhaar_card")
    pan_path = await save_upload(pan_file, "pan", user_id, "pan_card")
    medical_path = await save_upload(medical_file, "medical_reports", user_id, "medical_report")

    # Build and insert donor document
    doc = donor_document(
        user_id=user_id,
        age=data.age,
        father_name=data.father_name,
        state=data.state,
        city=data.city,
        full_address=data.full_address,
        aadhaar_card_path=aadhaar_path,
        pan_card_path=pan_path,
        medical_report_path=medical_path,
        aadhaar_number=data.aadhaar_number,
        pan_number=data.pan_number,
    )
    donors = get_donors_table()
    result = donors.insert(doc).execute()
    donor_id = str(result.data[0]["id"])

    logger.info(f"Donor profile created: donor_id={donor_id}, user_id={user_id}")
    return {
        "user_id": user_id,
        "donor_id": donor_id,
        "message": "Donor registered successfully. Please complete organ registration.",
    }


# ── Step 2: Organ Registration ────────────────────────────────────

async def register_organ(
    user_id: str,
    payload: OrganRegistrationRequest,
) -> dict:
    """Register one or more organs for an existing verified donor profile."""
    donors = get_donors_table()
    donor_res = donors.select("*").eq("user_id", user_id).execute()
    donor = donor_res.data[0] if donor_res.data else None
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor profile not found. Please complete Step 1 first."
        )

    donor_id = str(donor["id"])

    # Prevent duplicate organ registrations
    organs_table = get_organ_registrations_table()
    existing_res = organs_table.select("*").eq("donor_id", donor_id).eq("organ_name", payload.organ_name).eq("is_available", True).execute()
    if existing_res.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You have already registered '{payload.organ_name}' as an available organ."
        )

    doc = organ_registration_document(
        donor_id=donor_id,
        user_id=user_id,
        organ_name=payload.organ_name,
        blood_group=payload.blood_group,
        health_report=payload.health_report,
        hospitals_selected=payload.hospitals_selected,
        state=payload.state,
        city=payload.city,
    )
    result = organs_table.insert(doc).execute()

    logger.info(f"Organ registered: {payload.organ_name} | donor_id={donor_id}")
    return {
        "registration_id": str(result.data[0]["id"]),
        "donor_id": donor_id,
        "organ_name": payload.organ_name,
        "message": "Organ registered successfully. Awaiting hospital verification.",
    }


# ── Donor Profile ─────────────────────────────────────────────────

async def get_donor_profile(user_id: str) -> dict:
    """Return donor profile + organ registrations for the logged-in donor."""
    donors = get_donors_table()
    donor_res = donors.select("*").eq("user_id", user_id).execute()
    donor = donor_res.data[0] if donor_res.data else None
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found.")

    users = get_users_table()
    user_res = users.select("*").eq("id", user_id).execute()
    user = user_res.data[0] if user_res.data else None

    donor_id = str(donor["id"])
    organs_table = get_organ_registrations_table()
    organs_res = organs_table.select("*").eq("donor_id", donor_id).execute()
    organs = []
    for o in organs_res.data:
        organs.append({
            "registration_id": str(o["id"]),
            "organ_name": o["organ_name"],
            "blood_group": o["blood_group"],
            "state": o["state"],
            "city": o["city"],
            "is_available": o["is_available"],
            "created_at": o["created_at"],
        })

    return {
        "donor_id": donor_id,
        "user_id": user_id,
        "name": user["name"],
        "email": user["email"],
        "age": donor["age"],
        "father_name": donor["father_name"],
        "contact_number": user["contact_number"],
        "state": donor["state"],
        "city": donor["city"],
        "full_address": donor["full_address"],
        "verified": donor["verified"],
        "status": donor["status"],
        "verified_by_hospital": donor.get("verified_by_hospital"),
        "organ_registrations": organs,
        "created_at": donor["created_at"],
    }


# ── Donor document URLs (for own viewing) ─────────────────────────

async def get_donor_documents(user_id: str) -> dict:
    """Return pre-signed-like URLs for donor's own uploaded documents."""
    donors = get_donors_table()
    donor_res = donors.select("*").eq("user_id", user_id).execute()
    donor = donor_res.data[0] if donor_res.data else None
    if not donor:
        raise HTTPException(status_code=404, detail="Donor profile not found.")

    return {
        "aadhaar_card": file_url(donor.get("aadhaar_card_path", "")),
        "pan_card": file_url(donor.get("pan_card_path", "")),
        "medical_report": file_url(donor.get("medical_report_path", "")),
    }
