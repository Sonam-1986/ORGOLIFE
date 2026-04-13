"""
Hospital Admin schemas — registration, donor list, verify actions.
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.donor import DonorStatus


# ── Admin Registration ────────────────────────────────────────────

class HospitalAdminSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=8, pattern=r"^\d{8}$")
    contact_number: str = Field(..., pattern=r"^[0-9]{10}$", description="10-digit mobile number")
    hospital_name: str = Field(..., min_length=3, max_length=200)
    hospital_registration_number: str = Field(..., min_length=3, max_length=50)
    hospital_state: str = Field(..., min_length=2, max_length=100)
    hospital_city: str = Field(..., min_length=2, max_length=100)
    hospital_address: str = Field(..., min_length=5, max_length=500)
    hospital_contact: str = Field(..., description="Hospital contact number")
    aadhaar_number: Optional[str] = Field(None, description="12-digit Aadhaar number")
    pan_number: Optional[str] = Field(None, description="PAN number format")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dr. Ananya Singh",
                "email": "admin@apollomumbai.com",
                "password": "AdminPass123!",
                "contact_number": "9876500000",
                "hospital_name": "Apollo Hospital Mumbai",
                "hospital_registration_number": "MH-HOSP-2024-001",
                "hospital_state": "Maharashtra",
                "hospital_city": "Mumbai",
                "hospital_address": "Plot 13, Off New Link Road, Andheri West",
                "hospital_contact": "02266920000"
            }
        }


# ── Verification Actions ──────────────────────────────────────────

class ApproveDonorRequest(BaseModel):
    donor_id: str = Field(..., description="Unique ID (UUID) of the donor")
    notes: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {"donor_id": "d09a123-ef45-6789", "notes": "All documents verified."}
        }


class RejectDonorRequest(BaseModel):
    donor_id: str = Field(..., description="Unique ID (UUID) of the donor")
    rejection_reason: str = Field(..., min_length=10, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "donor_id": "d09a123-ef45-6789",
                "rejection_reason": "Medical report is outdated (older than 6 months)."
            }
        }


# ── Admin Response schemas ────────────────────────────────────────

class DonorAdminView(BaseModel):
    """Full donor detail visible to hospital admin."""
    donor_id: str
    user_id: str
    name: str
    age: int
    father_name: str
    email: str
    contact_number: str
    state: str
    city: str
    full_address: str
    aadhaar_number: str           # unmasked for admin
    pan_number: Optional[str]
    verified: bool
    status: DonorStatus
    aadhaar_card_url: str
    pan_card_url: str
    medical_report_url: str
    organ_registrations: List[dict]
    created_at: str


class HospitalProfileResponse(BaseModel):
    hospital_id: str
    name: str
    state: str
    city: str
    registration_number: str
    total_approvals: int
    total_rejections: int
    created_at: str


class VerificationActionResponse(BaseModel):
    donor_id: str
    new_status: DonorStatus
    verified: bool
    action_by_hospital: str
    message: str
