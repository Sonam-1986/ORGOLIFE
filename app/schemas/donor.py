"""
Donor schemas — Step 1 registration, Step 2 organ registration,
donor profile response, and admin-facing donor detail.
"""
import re
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.organ import OrganName, BloodGroup
from app.models.donor import DonorStatus


# ── Step 1: Donor Signup (text fields only; files via Form) ───────

class DonorSignupStep1(BaseModel):
    """
    Sent as multipart/form-data alongside file uploads.
    All fields are strings here because HTML forms send strings.
    """
    age: int = Field(..., ge=18, le=70, description="Donor must be 18–70")
    father_name: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    full_address: str = Field(..., min_length=5, max_length=500)
    aadhaar_number: Optional[str] = Field(None, pattern=r"^\d{12}$")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")

    @classmethod
    def no_op(cls):
        pass

    class Config:
        json_schema_extra = {
            "example": {
                "age": 35,
                "father_name": "Ramesh Kumar",
                "state": "Maharashtra",
                "city": "Mumbai",
                "full_address": "123 MG Road, Andheri West",
                "aadhaar_number": "123456789012",
                "pan_number": "ABCDE1234F"
            }
        }


# ── Step 2: Organ Registration ────────────────────────────────────

class OrganRegistrationRequest(BaseModel):
    organ_name: OrganName
    blood_group: BloodGroup
    health_report: str = Field(..., min_length=10, max_length=2000)
    hospitals_selected: List[str] = Field(..., min_length=1, max_length=5)
    state: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "organ_name": "kidney",
                "blood_group": "O+",
                "health_report": "Both kidneys functioning normally. No chronic disease.",
                "hospitals_selected": ["Apollo Mumbai", "Lilavati Hospital"],
                "state": "Maharashtra",
                "city": "Mumbai"
            }
        }


# ── Response schemas ──────────────────────────────────────────────

class DonorProfileResponse(BaseModel):
    donor_id: str
    user_id: str
    name: str
    age: int
    father_name: str
    contact_number: str
    state: str
    city: str
    full_address: str
    verified: bool
    status: DonorStatus
    verified_by_hospital: Optional[str]
    created_at: str


class OrganRegistrationResponse(BaseModel):
    registration_id: str
    donor_id: str
    organ_name: OrganName
    blood_group: BloodGroup
    health_report: str
    hospitals_selected: List[str]
    state: str
    city: str
    is_available: bool
    created_at: str


class DonorSearchResultItem(BaseModel):
    """What a receiver sees in search results."""
    donor_name: str
    father_name: str
    aadhaar_number_masked: str
    blood_group: BloodGroup
    organ: OrganName
    hospital_verified_by: Optional[str]
    verification_status: str          # "legal" | "illegal" | "pending"
    contact_number: str
    state: str
    city: str
    full_address: str
