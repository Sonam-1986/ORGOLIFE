"""
Hospital Admin service — donor listing, document access, verification actions.
"""
import logging
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.db.database import (
    get_users_table, get_donors_table, get_receivers_table,
    get_hospitals_table, get_organ_registrations_table
)
from app.models.donor import DonorStatus
from app.services.file_service import file_url
from app.utils.pagination import paginate_response

logger = logging.getLogger(__name__)


async def _get_hospital_for_admin(admin_user_id: str) -> dict:
    """Fetch the hospital linked to this admin. Raises 404 if missing."""
    hospitals = get_hospitals_table()
    res = hospitals.select("*").eq("admin_user_id", admin_user_id).execute()
    hospital = res.data[0] if res.data else None
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found for this admin account."
        )
    return hospital


# ── Donor Listing ─────────────────────────────────────────────────

async def list_all_donors(
    admin_user_id: str,
    page: int = 1,
    page_size: int = 10,
    status_filter: str = "all",
) -> dict:
    """
    Paginated donor list visible to hospital admins.
    Optionally filtered by verification status.
    """
    await _get_hospital_for_admin(admin_user_id)  # auth check

    donors_table = get_donors_table()
    users_table = get_users_table()

    query = donors_table.select("*")
    if status_filter != "all":
        query = query.eq("status", status_filter)

    skip = (page - 1) * page_size
    # Realistically we'd do a count query, but for now we follow the simple migration pattern.
    total_res = query.execute()
    total = len(total_res.data)

    response = query.order("created_at", desc=True).range(skip, skip + page_size - 1).execute()
    donors = response.data

    items = []
    for donor in donors:
        u_res = users_table.select("*").eq("id", donor["user_id"]).execute()
        user = u_res.data[0] if u_res.data else None
        if not user:
            continue

        items.append({
            "donor_id": str(donor["id"]),
            "user_id": donor["user_id"],
            "name": user["name"],
            "email": user["email"],
            "age": donor["age"],
            "contact_number": user["contact_number"],
            "state": donor["state"],
            "city": donor["city"],
            "verified": donor["verified"],
            "status": donor["status"],
            "aadhaar_card_url": file_url(donor.get("aadhaar_card_path")),
            "pan_card_url": file_url(donor.get("pan_card_path")),
            "medical_report_url": file_url(donor.get("medical_report_path")),
            "created_at": donor["created_at"],
        })

    return paginate_response(items, total, page, page_size)


# ── Full Donor Detail ─────────────────────────────────────────────

async def get_donor_detail(admin_user_id: str, donor_id: str) -> dict:
    """Return complete donor info (including unmasked docs) for admin review."""
    await _get_hospital_for_admin(admin_user_id)

    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None

    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found."
        )

    users_table = get_users_table()
    u_res = users_table.select("*").eq("id", donor["user_id"]).execute()
    user = u_res.data[0] if u_res.data else None

    organs_table = get_organ_registrations_table()
    o_res = organs_table.select("*").eq("donor_id", donor_id).execute()
    organs = []
    for o in o_res.data:
        organs.append({
            "registration_id": str(o["id"]),
            "organ_name": o["organ_name"],
            "blood_group": o["blood_group"],
            "health_report": o["health_report"],
            "hospitals_selected": o["hospitals_selected"],
            "state": o["state"],
            "city": o["city"],
            "is_available": o["is_available"],
        })

    docs = donor.get("documents", {})
    registered_organs_str = ", ".join([o["organ_name"] for o in organs])
    
    return {
        "donor_id": donor_id,
        "user_id": donor["user_id"],
        "name": user["name"],
        "email": user["email"],
        "age": donor["age"],
        "father_name": donor["father_name"],
        "contact_number": user["contact_number"],
        "state": donor["state"],
        "city": donor["city"],
        "full_address": donor["full_address"],
        "aadhaar_number": donor.get("aadhaar_number", "N/A"),
        "pan_number": donor.get("pan_number", "N/A"),
        "verified": donor["verified"],
        "status": donor["status"],
        "rejection_reason": donor.get("rejection_reason"),
        "verified_by_hospital": donor.get("verified_by_hospital"),
        "aadhaar_card_url": file_url(donor.get("aadhaar_card_path", "")),
        "pan_card_url": file_url(donor.get("pan_card_path", "")),
        "medical_report_url": file_url(donor.get("medical_report_path", "")),
        "organ_registrations": organs,
        "registered_organs": registered_organs_str,
        "created_at": donor["created_at"],
    }


# ── Approve Donor ─────────────────────────────────────────────────

async def approve_donor(admin_user_id: str, donor_id: str, notes: str = None) -> dict:
    """
    Set donor.verified=True, donor.status='approved'.
    Tag with hospital name for audit trail.
    """
    hospital = await _get_hospital_for_admin(admin_user_id)
    hospital_name = hospital["name"]

    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found."
        )

    if donor["status"] == DonorStatus.APPROVED:
        raise HTTPException(status_code=409, detail="Donor is already approved.")

    now = datetime.now(timezone.utc).isoformat()
    donors_table.update({
        "verified": True,
        "status": DonorStatus.APPROVED,
        "verified_by_hospital": hospital_name,
        "verified_by_admin_id": admin_user_id,
        "rejection_reason": None,
        "updated_at": now,
    }).eq("id", donor_id).execute()

    # Increment hospital approval counter
    hospitals_table = get_hospitals_table()
    hospitals_table.update({
        "total_approvals": (hospital.get("total_approvals") or 0) + 1,
        "updated_at": now
    }).eq("id", hospital["id"]).execute()

    logger.info(f"Donor APPROVED: donor_id={donor_id} | by hospital={hospital_name}")
    return {
        "donor_id": donor_id,
        "new_status": DonorStatus.APPROVED,
        "verified": True,
        "action_by_hospital": hospital_name,
        "message": "Donor has been approved and is now visible in search results.",
    }


# ── Reject Donor ──────────────────────────────────────────────────

async def reject_donor(admin_user_id: str, donor_id: str, rejection_reason: str) -> dict:
    """
    Set donor.verified=False, donor.status='rejected'.
    Store the rejection reason.
    """
    hospital = await _get_hospital_for_admin(admin_user_id)
    hospital_name = hospital["name"]

    donors_table = get_donors_table()
    res = donors_table.select("*").eq("id", donor_id).execute()
    donor = res.data[0] if res.data else None
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found."
        )

    if donor["status"] == DonorStatus.REJECTED:
        raise HTTPException(status_code=409, detail="Donor is already rejected.")

    now = datetime.now(timezone.utc).isoformat()
    donors_table.update({
        "verified": False,
        "status": DonorStatus.REJECTED,
        "rejection_reason": rejection_reason,
        "verified_by_hospital": hospital_name,
        "verified_by_admin_id": admin_user_id,
        "updated_at": now,
    }).eq("id", donor_id).execute()

    hospitals_table = get_hospitals_table()
    hospitals_table.update({
        "total_rejections": (hospital.get("total_rejections") or 0) + 1,
        "updated_at": now
    }).eq("id", hospital["id"]).execute()

    logger.info(f"Donor REJECTED: donor_id={donor_id} | hospital={hospital_name}")
    return {
        "donor_id": donor_id,
        "new_status": DonorStatus.REJECTED,
        "verified": False,
        "action_by_hospital": hospital_name,
        "message": "Donor registration has been rejected.",
    }


# ── Receiver Listing ──────────────────────────────────────────────

async def list_all_receivers(
    admin_user_id: str,
    page: int = 1,
    page_size: int = 10,
    status_filter: str = "all",
) -> dict:
    """Paginated receiver list for admin review."""
    await _get_hospital_for_admin(admin_user_id)

    receivers_table = get_receivers_table()
    users_table = get_users_table()

    query = receivers_table.select("*")
    if status_filter != "all":
        query = query.eq("status", status_filter)

    skip = (page - 1) * page_size
    total_res = query.execute()
    total = len(total_res.data)

    response = query.order("created_at", desc=True).range(skip, skip + page_size - 1).execute()
    receivers = response.data

    items = []
    for recv in receivers:
        u_res = users_table.select("*").eq("id", recv["user_id"]).execute()
        user = u_res.data[0] if u_res.data else None
        if not user:
            continue

        items.append({
            "receiver_id": str(recv["id"]),
            "user_id": recv["user_id"],
            "name": user["name"],
            "email": user["email"],
            "age": recv["age"],
            "state": recv["state"],
            "city": recv["city"],
            "status": recv.get("status", "pending"),
            "aadhaar_card_url": file_url(recv.get("aadhaar_card_path")),
            "pan_card_url": file_url(recv.get("pan_card_path")),
            "medical_report_url": file_url(recv.get("medical_report_path")),
            "created_at": recv.get("created_at"),
        })

    return paginate_response(items, total, page, page_size)


# ── Full Receiver Detail ──────────────────────────────────────────

async def get_receiver_detail(admin_user_id: str, receiver_id: str) -> dict:
    """Return complete receiver info for admin review."""
    await _get_hospital_for_admin(admin_user_id)

    receivers_table = get_receivers_table()
    res = receivers_table.select("*").eq("id", receiver_id).execute()
    recv = res.data[0] if res.data else None

    if not recv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found."
        )

    users_table = get_users_table()
    u_res = users_table.select("*").eq("id", recv["user_id"]).execute()
    user = u_res.data[0] if u_res.data else None

    return {
        "receiver_id": receiver_id,
        "user_id": recv["user_id"],
        "name": user["name"],
        "email": user["email"],
        "age": recv["age"],
        "father_name": recv["father_name"],
        "contact_number": user["contact_number"],
        "state": recv["state"],
        "city": recv["city"],
        "full_address": recv.get("full_address", f"{recv['city']}, {recv['state']}"),
        "aadhaar_number": recv.get("aadhaar_number", "N/A"),
        "pan_number": recv.get("pan_number", "N/A"),
        "status": recv.get("status", "pending"),
        "verified_by_hospital": recv.get("verified_by_hospital"),
        "aadhaar_card_url": file_url(recv.get("aadhaar_card_path", "")),
        "pan_card_url": file_url(recv.get("pan_card_path", "")),
        "medical_report_url": file_url(recv.get("medical_report_path", "")),
        "created_at": recv.get("created_at"),
    }


# ── Receiver Verification ────────────────────────────────────────

async def approve_receiver(admin_user_id: str, receiver_id: str) -> dict:
    hospital = await _get_hospital_for_admin(admin_user_id)
    receivers_table = get_receivers_table()
    
    receivers_table.update({
        "status": "approved",
        "verified_by_hospital": hospital["name"],
        "verified_by_admin_id": admin_user_id,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", receiver_id).execute()
    
    logger.info(f"Receiver APPROVED: {receiver_id} by {hospital['name']}")
    return {"message": "Receiver approved successfully.", "status": "approved"}


async def reject_receiver(admin_user_id: str, receiver_id: str) -> dict:
    hospital = await _get_hospital_for_admin(admin_user_id)
    receivers_table = get_receivers_table()
    
    receivers_table.update({
        "status": "rejected",
        "verified_by_hospital": hospital["name"],
        "verified_by_admin_id": admin_user_id,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", receiver_id).execute()
    
    logger.info(f"Receiver REJECTED: {receiver_id} by {hospital['name']}")
    return {"message": "Receiver rejected.", "status": "rejected"}


# ── Admin's Hospital Profile ──────────────────────────────────────

async def get_hospital_profile(admin_user_id: str) -> dict:
    """Return the hospital profile for the logged-in admin."""
    hospital = await _get_hospital_for_admin(admin_user_id)
    return {
        "hospital_id": str(hospital["id"]),
        "name": hospital["name"],
        "state": hospital["state"],
        "city": hospital["city"],
        "registration_number": hospital["registration_number"],
        "total_approvals": hospital.get("total_approvals", 0),
        "total_rejections": hospital.get("total_rejections", 0),
        "created_at": hospital["created_at"],
    }


# ── Platform Insights ─────────────────────────────────────────────

async def get_platform_insights(admin_user_id: str) -> dict:
    """Return platform-wide statistics for the admin dashboard."""
    await _get_hospital_for_admin(admin_user_id)  # Auth check

    users_table = get_users_table()
    donors_table = get_donors_table()
    receivers_table = get_receivers_table()
    hospitals_table = get_hospitals_table()

    # Get counts
    donors_count = len(donors_table.select("id").execute().data)
    receivers_count = len(receivers_table.select("id").execute().data)
    hospitals_count = len(hospitals_table.select("id").execute().data)
    
    # Admins count (users where role is hospital_admin)
    admins_res = users_table.select("id").eq("role", "hospital_admin").execute()
    admins_count = len(admins_res.data)

    return {
        "total_donors": donors_count,
        "total_receivers": receivers_count,
        "total_hospitals": hospitals_count,
        "total_admins": admins_count,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
