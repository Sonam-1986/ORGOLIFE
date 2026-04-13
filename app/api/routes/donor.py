"""
Donor routes:
  POST /donors/register          — Step 1: full donor onboarding (multipart)
  POST /donors/organs            — Step 2: organ registration
  GET  /donors/profile           — own profile
  GET  /donors/documents         — own document URLs
"""
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from typing import Optional

from app.core.dependencies import require_donor, get_current_user
from app.schemas.donor import DonorSignupStep1, OrganRegistrationRequest
from app.schemas.common import BaseResponse
from app.services import donor_service
from app.models.organ import OrganName, BloodGroup

router = APIRouter(prefix="/donors", tags=["Donors"])


@router.post(
    "/register",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Donor (Step 1 — Profile + Documents)",
)
async def register_donor(
    current_user: dict = Depends(get_current_user),
    age: int = Form(...),
    father_name: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    full_address: str = Form(...),
    aadhaar_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
    aadhaar_file: UploadFile = File(..., description="Aadhaar card PDF/image"),
    pan_file: UploadFile = File(..., description="PAN card PDF/image"),
    medical_file: UploadFile = File(..., description="Medical report PDF/image"),
):
    data = DonorSignupStep1(
        age=age, father_name=father_name,
        state=state, city=city, full_address=full_address,
        aadhaar_number=aadhaar_number, pan_number=pan_number,
    )
    result = await donor_service.register_donor(current_user["sub"], data, aadhaar_file, pan_file, medical_file)
    return BaseResponse(message=result["message"], data=result)


@router.post(
    "/organs",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Organ (Step 2)",
)
async def register_organ(
    payload: OrganRegistrationRequest,
    current_user: dict = Depends(require_donor),
):
    result = await donor_service.register_organ(current_user["sub"], payload)
    return BaseResponse(message=result["message"], data=result)


@router.get(
    "/profile",
    response_model=BaseResponse,
    summary="Get Donor Profile",
)
async def get_profile(current_user: dict = Depends(require_donor)):
    profile = await donor_service.get_donor_profile(current_user["sub"])
    return BaseResponse(data=profile)


@router.get(
    "/documents",
    response_model=BaseResponse,
    summary="Get Donor Document URLs",
)
async def get_documents(current_user: dict = Depends(require_donor)):
    docs = await donor_service.get_donor_documents(current_user["sub"])
    return BaseResponse(data=docs)
