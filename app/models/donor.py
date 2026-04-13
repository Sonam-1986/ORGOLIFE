"""
Donor model — profile record stored in 'donors' table.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class DonorStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def donor_document(
    user_id: str,
    age: int,
    father_name: str,
    state: str,
    city: str,
    full_address: str,
    aadhaar_card_path: str,
    pan_card_path: str,
    medical_report_path: str,
    aadhaar_number: Optional[str] = None,
    pan_number: Optional[str] = None,
) -> dict:
    """Factory for donors table."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "user_id": user_id,
        "age": age,
        "father_name": father_name,
        "state": state,
        "city": city,
        "full_address": full_address,
        "aadhaar_card_path": aadhaar_card_path,
        "pan_card_path": pan_card_path,
        "medical_report_path": medical_report_path,
        "aadhaar_number": aadhaar_number,
        "pan_number": pan_number,
        "verified": False,
        "status": DonorStatus.PENDING,
        "verified_by_hospital": None,
        "verified_by_admin_id": None,
        "rejection_reason": None,
        "created_at": now,
        "updated_at": now,
    }
