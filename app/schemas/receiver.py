"""
Receiver schemas — registration and donor search.
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from app.models.organ import OrganName, BloodGroup


# ── Step 1: Receiver Signup ───────────────────────────────────────

class ReceiverSignupStep1(BaseModel):
    age: int = Field(..., ge=1, le=120)
    father_name: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    aadhaar_number: Optional[str] = Field(None, pattern=r"^\d{12}$")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")

    @classmethod
    def no_op(cls):
        pass

    class Config:
        json_schema_extra = {
            "example": {
                "age": 28,
                "father_name": "Suresh Sharma",
                "state": "Maharashtra",
                "city": "Pune"
            }
        }


# ── Step 2: Donor Search Filters ─────────────────────────────────

class DonorSearchRequest(BaseModel):
    organ_type: Optional[str] = "all"
    blood_group: Optional[str] = "all"
    verified_donor: str = Field("all", pattern=r"^(yes|no|all)$")
    state: Optional[str] = None
    city: Optional[str] = None
    hospital_name: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)

    class Config:
        json_schema_extra = {
            "example": {
                "organ_type": "kidney",
                "blood_group": "O+",
                "verified_donor": "yes",
                "state": "Maharashtra",
                "city": "Mumbai",
                "page": 1,
                "page_size": 10
            }
        }


# ── Response schemas ──────────────────────────────────────────────

class ReceiverProfileResponse(BaseModel):
    receiver_id: str
    user_id: str
    name: str
    age: int
    father_name: str
    contact_number: str
    state: str
    city: str
    created_at: str
