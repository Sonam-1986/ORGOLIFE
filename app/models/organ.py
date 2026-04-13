"""
Organ registration model — stored in 'organ_registrations' table.
One donor can register multiple organs.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List


class OrganName(str, Enum):
    KIDNEY = "kidney"
    LIVER = "liver"
    HEART = "heart"
    LUNG = "lung"
    PANCREAS = "pancreas"
    CORNEA = "cornea"
    SKIN = "skin"
    BONE_MARROW = "bone_marrow"
    INTESTINE = "intestine"


class BloodGroup(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


def organ_registration_document(
    donor_id: str,
    user_id: str,
    organ_name: OrganName,
    blood_group: BloodGroup,
    health_report: str,
    hospitals_selected: List[str],
    state: str,
    city: str,
) -> dict:
    """Factory for organ_registrations table."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "donor_id": donor_id,
        "user_id": user_id,
        "organ_name": organ_name,
        "blood_group": blood_group,
        "health_report": health_report,
        "hospitals_selected": hospitals_selected,
        "state": state,
        "city": city,
        "is_available": True,
        "matched_receiver_id": None,
        "created_at": now,
        "updated_at": now,
    }
