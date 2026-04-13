"""
Auth routes:
  POST /auth/register/admin   — register hospital admin
  POST /auth/login            — donor / receiver login
  POST /auth/login/admin      — hospital admin login
  POST /auth/refresh          — refresh access token
  GET  /auth/me               — current user profile
"""
from fastapi import APIRouter, Depends, status, Form, File, UploadFile
from typing import Optional
from app.schemas.auth import LoginRequest, AdminLoginRequest, RefreshTokenRequest, TokenResponse, UserSignup
from app.schemas.admin import HospitalAdminSignup
from app.schemas.common import BaseResponse
from app.services import auth_service
from app.core.dependencies import get_current_user
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/admin",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Hospital Admin",
)
async def register_admin(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    contact_number: str = Form(...),
    hospital_name: str = Form(...),
    hospital_registration_number: str = Form(...),
    hospital_state: str = Form(...),
    hospital_city: str = Form(...),
    hospital_address: str = Form(...),
    hospital_contact: str = Form(...),
    aadhaar_number: Optional[str] = Form(None),
    pan_number: Optional[str] = Form(None),
):
    payload = HospitalAdminSignup(
        name=name, email=email, password=password,
        contact_number=contact_number,
        hospital_name=hospital_name, hospital_registration_number=hospital_registration_number,
        hospital_state=hospital_state, hospital_city=hospital_city,
        hospital_address=hospital_address, hospital_contact=hospital_contact,
        aadhaar_number=aadhaar_number, pan_number=pan_number
    )
    result = await auth_service.register_hospital_admin(payload)
    return BaseResponse(
        message="Hospital admin registered successfully.",
        data=result,
    )


@router.post(
    "/register",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Base User",
)
async def register(payload: UserSignup):
    result = await auth_service.register_base_user(payload)
    return BaseResponse(
        message="User registered successfully.",
        data=result,
    )


@router.post(
    "/register/donor",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Full Donor Signup (Step 1)",
)
async def register_donor(
    name: str = Form(...), email: str = Form(...), password: str = Form(...), 
    contact_number: str = Form(...), age: int = Form(...), 
    father_name: str = Form(...), state: str = Form(...), 
    city: str = Form(...), full_address: str = Form(...),
    aadhaar_file: UploadFile = File(...), pan_file: UploadFile = File(...), 
    medical_file: UploadFile = File(...),
    aadhaar_number: Optional[str] = Form(None), pan_number: Optional[str] = Form(None)
):
    result = await auth_service.register_full_donor(
        name, email, password, contact_number, age, father_name, 
        state, city, full_address, aadhaar_file, pan_file, medical_file,
        aadhaar_number, pan_number
    )
    return BaseResponse(message="Donor registered successfully.", data=result)


@router.post(
    "/register/receiver",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Full Receiver Signup (Step 1)",
)
async def register_receiver(
    name: str = Form(...), email: str = Form(...), password: str = Form(...), 
    contact_number: str = Form(...), age: int = Form(...), 
    father_name: str = Form(...), state: str = Form(...), city: str = Form(...),
    aadhaar_file: UploadFile = File(...), pan_file: UploadFile = File(...), 
    medical_file: UploadFile = File(...),
    aadhaar_number: Optional[str] = Form(None), pan_number: Optional[str] = Form(None)
):
    result = await auth_service.register_full_receiver(
        name, email, password, contact_number, age, father_name, 
        state, city, aadhaar_file, pan_file, medical_file,
        aadhaar_number, pan_number
    )
    return BaseResponse(message="Receiver registered successfully.", data=result)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Universal User Login",
)
async def login(payload: LoginRequest):
    """Universal login for users, donors, receivers."""
    return await auth_service.login_user(payload, None)


@router.post(
    "/login/admin",
    response_model=TokenResponse,
    summary="Hospital Admin Login",
)
async def login_admin(payload: AdminLoginRequest):
    return await auth_service.login_admin(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Access Token",
)
async def refresh_token(payload: RefreshTokenRequest):
    return await auth_service.refresh_access_token(payload.refresh_token)


@router.get(
    "/me",
    response_model=BaseResponse,
    summary="Current User Info",
)
async def get_me(current_user: dict = Depends(get_current_user)):
    user_id = current_user["sub"]
    profile = await auth_service.get_user_profile(user_id)
    return BaseResponse(data=profile)
