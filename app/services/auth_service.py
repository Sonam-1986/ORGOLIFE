"""
Auth service — register users, login, refresh tokens.
Orchestrates DB access, password hashing, and JWT generation.
"""
import logging
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status, UploadFile
from app.db.database import get_users_table, get_hospitals_table, get_donors_table, get_receivers_table
from app.models.user import UserRole, UserStatus, user_document
from app.models.donor import donor_document
from app.models.hospital import hospital_document
from app.schemas.auth import LoginRequest, TokenResponse, AdminLoginRequest
from app.schemas.admin import HospitalAdminSignup
from app.utils.password import hash_password, verify_password
from app.services.file_service import save_upload
from app.utils.jwt_handler import (
    create_access_token, create_refresh_token,
    verify_refresh_token
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_token_response(user: dict) -> TokenResponse:
    """Build a TokenResponse from a DB user document."""
    user_id = str(user["id"])
    token_data = {
        "sub": user_id,
        "role": user["role"],
        "email": user["email"],
        "name": user["name"],
    }
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user["role"],
        user_id=user_id,
        name=user["name"],
    )


# ── User Registration ────────────────────────────────

async def register_base_user(payload) -> dict:
    users = get_users_table()
    response = users.select("*").eq("email", payload.email.lower().strip()).execute()
    existing = response.data[0] if response.data else None
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    doc = user_document(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.USER,
        contact_number=payload.contact_number,
    )
    response = users.insert(doc).execute()
    logger.info(f"New base user registered: {payload.email}")
    return {"user_id": str(response.data[0]["id"]), "role": doc["role"]}

# ── Full Donor/Receiver Atomic Registration ──────────────────────

async def register_full_donor(
    name: str, email: str, password: str, contact_number: str,
    age: int, father_name: str, state: str, city: str, full_address: str,
    aadhaar_file: UploadFile, pan_file: UploadFile, medical_file: UploadFile,
    aadhaar_number: str = None, pan_number: str = None
) -> dict:
    """Atomic: Create User -> Create Donor Profile -> Save 3 Files."""
    users = get_users_table()
    donors_table = get_donors_table()

    # 1. User check/insert
    existing = users.select("*").eq("email", email.lower().strip()).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email already exists.")

    user_doc = user_document(
        name=name, email=email, hashed_password=hash_password(password),
        role=UserRole.DONOR, contact_number=contact_number,
    )
    user_res = users.insert(user_doc).execute()
    user_id = str(user_res.data[0]["id"])

    # 2. Save Files
    aadhaar_path = await save_upload(aadhaar_file, "aadhaar", user_id, "aadhaar_card")
    pan_path = await save_upload(pan_file, "pan", user_id, "pan_card")
    medical_path = await save_upload(medical_file, "medical_reports", user_id, "medical_report")

    # 3. Donor Profile
    donor_doc = donor_document(
        user_id=user_id, age=age, father_name=father_name,
        state=state, city=city, full_address=full_address,
        aadhaar_card_path=aadhaar_path, pan_card_path=pan_path,
        medical_report_path=medical_path,
        aadhaar_number=aadhaar_number, pan_number=pan_number
    )
    donors_table.insert(donor_doc).execute()
    
    logger.info(f"Full Donor Registered: {email}")
    return {"user_id": user_id, "role": UserRole.DONOR}


async def register_full_receiver(
    name: str, email: str, password: str, contact_number: str,
    age: int, father_name: str, state: str, city: str,
    aadhaar_file: UploadFile, pan_file: UploadFile, medical_file: UploadFile,
    aadhaar_number: str = None, pan_number: str = None
) -> dict:
    """Atomic: Create User -> Create Receiver Profile -> Save 3 Files."""
    users = get_users_table()
    receivers_table = get_receivers_table()

    existing = users.select("*").eq("email", email.lower().strip()).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email already exists.")

    user_doc = user_document(
        name=name, email=email, hashed_password=hash_password(password),
        role=UserRole.RECEIVER, contact_number=contact_number,
    )
    user_res = users.insert(user_doc).execute()
    user_id = str(user_res.data[0]["id"])

    aadhaar_path = await save_upload(aadhaar_file, "aadhaar", user_id, "aadhaar_card")
    pan_path = await save_upload(pan_file, "pan", user_id, "pan_card")
    medical_path = await save_upload(medical_file, "medical_reports", user_id, "medical_report")

    from app.models.receiver import receiver_document
    recv_doc = receiver_document(
        user_id=user_id, age=age, father_name=father_name,
        state=state, city=city,
        aadhaar_card_path=aadhaar_path, pan_card_path=pan_path,
        medical_report_path=medical_path,
        aadhaar_number=aadhaar_number, pan_number=pan_number
    )
    receivers_table.insert(recv_doc).execute()
    
    logger.info(f"Full Receiver Registered: {email}")
    return {"user_id": user_id, "role": UserRole.RECEIVER}


# ── Hospital Admin Registration ───────────────────────────────────

async def register_hospital_admin(
    payload: HospitalAdminSignup,
) -> dict:
    """Register a hospital admin + create the hospital record atomically."""
    users = get_users_table()
    hospitals = get_hospitals_table()

    # Email uniqueness
    user_res = users.select("*").eq("email", payload.email.lower().strip()).execute()
    if user_res.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An admin account with this email already exists."
        )

    # Hospital registration number uniqueness
    hosp_res = hospitals.select("*").eq("registration_number", payload.hospital_registration_number).execute()
    if hosp_res.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this registration number already exists."
        )

    # Insert user first to get ID
    user_doc = user_document(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.HOSPITAL_ADMIN,
        contact_number=payload.contact_number,
    )
    user_insert_res = users.insert(user_doc).execute()
    admin_user_id = str(user_insert_res.data[0]["id"])

    # Create hospital record
    hosp_doc = hospital_document(
        name=payload.hospital_name,
        admin_user_id=admin_user_id,
        state=payload.hospital_state,
        city=payload.hospital_city,
        address=payload.hospital_address,
        contact_number=payload.hospital_contact,
        registration_number=payload.hospital_registration_number,
    )
    
    hosp_insert_res = hospitals.insert(hosp_doc).execute()
    hospital_id = str(hosp_insert_res.data[0]["id"])

    # CRITICAL: Link hospital_id back to the user document
    users.update({"hospital_id": hospital_id}).eq("id", admin_user_id).execute()

    logger.info(f"Hospital admin registered: {payload.email} | hospital: {payload.hospital_name}")
    return {
        "user_id": admin_user_id,
        "hospital_id": hospital_id,
    }


# ── Login ─────────────────────────────────────────────────────────

async def login_user(payload: LoginRequest, expected_role: Optional[UserRole] = None) -> TokenResponse:
    """Authenticate a user and return JWT tokens."""
    users = get_users_table()
    response = users.select("*").eq("email", payload.email.lower().strip()).execute()
    user = response.data[0] if response.data else None

    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if expected_role and user["role"] != expected_role:
        # Check if the user is trying to login as something they are not, but allow base users
        if expected_role not in [UserRole.DONOR, UserRole.RECEIVER] or user["role"] not in [UserRole.DONOR, UserRole.RECEIVER, UserRole.USER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This login endpoint is for '{expected_role}' accounts only."
            )

    if user.get("status") not in ("active", UserStatus.ACTIVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended. Contact support.",
        )

    logger.info(f"Login successful: {payload.email}")
    return _build_token_response(user)


async def login_admin(payload: AdminLoginRequest) -> TokenResponse:
    """Admin login — also validates hospital code (registration number)."""
    users = get_users_table()
    hospitals = get_hospitals_table()

    response = users.select("*").eq("email", payload.email.lower().strip()).execute()
    user = response.data[0] if response.data else None
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user["role"] != UserRole.HOSPITAL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for Hospital Admins only."
        )

    if user.get("status") not in ("active", UserStatus.ACTIVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended. Contact support.",
        )

    # Validate hospital_code
    hosp_res = hospitals.select("*").eq("admin_user_id", str(user["id"])).eq("registration_number", payload.hospital_code).execute()
    hospital = hosp_res.data[0] if hosp_res.data else None
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid hospital code. Access denied."
        )

    logger.info(f"Admin login: {payload.email}")
    return _build_token_response(user)


# ── Token Refresh ─────────────────────────────────────────────────

async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Issue a new access token using a valid refresh token."""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    users = get_users_table()
    response = users.select("*").eq("id", payload["sub"]).execute()
    user = response.data[0] if response.data else None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return _build_token_response(user)

async def get_user_profile(user_id: str) -> dict:
    """Fetch full user profile, joining donor/receiver details if applicable."""
    users = get_users_table()
    res = users.select("*").eq("id", user_id).execute()
    user = res.data[0] if res.data else None
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    profile = {
        "id": str(user["id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "contact_number": user["contact_number"],
        "created_at": user["created_at"],
        "status": user.get("status", "active"),
    }
    
    # Enrich based on role
    if user["role"] == UserRole.DONOR:
        donors = get_donors_table()
        d_res = donors.select("*").eq("user_id", user_id).execute()
        if d_res.data:
            d = d_res.data[0]
            profile.update({
                "age": d["age"],
                "father_name": d["father_name"],
                "state": d["state"],
                "city": d["city"],
                "full_address": d["full_address"],
            })
            # Also get organs
            from app.db.database import get_organ_registrations_table
            organs_table = get_organ_registrations_table()
            o_res = organs_table.select("organ_name").eq("donor_id", str(d["id"])).execute()
            profile["registered_organs"] = ", ".join([o["organ_name"] for o in o_res.data])
            
    elif user["role"] == UserRole.RECEIVER:
        receivers = get_receivers_table()
        r_res = receivers.select("*").eq("user_id", user_id).execute()
        if r_res.data:
            r = r_res.data[0]
            profile.update({
                "age": r["age"],
                "father_name": r["father_name"],
                "state": r["state"],
                "city": r["city"],
            })
            
    elif user["role"] == UserRole.HOSPITAL_ADMIN:
        hospitals = get_hospitals_table()
        h_res = hospitals.select("*").eq("admin_user_id", user_id).execute()
        if h_res.data:
            h = h_res.data[0]
            profile.update({
                "hospital_name": h["name"],
                "hospital_city": h["city"],
                "hospital_reg": h["registration_number"],
            })
            
    return profile
