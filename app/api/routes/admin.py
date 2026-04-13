"""
Hospital Admin routes:
  GET  /admin/hospital/profile      — own hospital info
  GET  /admin/donors                — paginated donor list
  GET  /admin/donors/{donor_id}     — full donor detail + docs
  POST /admin/donors/approve        — approve donor
  POST /admin/donors/reject         — reject donor
"""
from fastapi import APIRouter, Depends, Query, status
from app.core.dependencies import require_admin
from app.schemas.admin import ApproveDonorRequest, RejectDonorRequest
from app.schemas.common import BaseResponse
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Hospital Admin"])


@router.get(
    "/hospital/profile",
    response_model=BaseResponse,
    summary="Get Hospital Profile",
)
async def get_hospital_profile(current_user: dict = Depends(require_admin)):
    profile = await admin_service.get_hospital_profile(current_user["sub"])
    return BaseResponse(data=profile)


@router.get(
    "/insights",
    response_model=BaseResponse,
    summary="Get Platform Insights",
    description="Returns statistics for donors, receivers, hospitals, and admins."
)
async def get_platform_insights(current_user: dict = Depends(require_admin)):
    insights = await admin_service.get_platform_insights(current_user["sub"])
    return BaseResponse(data=insights)


@router.get(
    "/donors",
    response_model=BaseResponse,
    summary="List All Donors",
    description=(
        "Paginated list of all registered donors with document URLs. "
        "Filter by status: all | pending | approved | rejected."
    ),
)
async def list_donors(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: str = Query("all", pattern=r"^(all|pending|approved|rejected)$"),
    current_user: dict = Depends(require_admin),
):
    result = await admin_service.list_all_donors(
        admin_user_id=current_user["sub"],
        page=page,
        page_size=page_size,
        status_filter=status_filter,
    )
    return BaseResponse(data=result)


@router.get(
    "/donors/{donor_id}",
    response_model=BaseResponse,
    summary="Get Full Donor Detail",
    description="Returns complete donor info including unmasked Aadhaar/PAN and document URLs.",
)
async def get_donor_detail(
    donor_id: str,
    current_user: dict = Depends(require_admin),
):
    detail = await admin_service.get_donor_detail(current_user["sub"], donor_id)
    return BaseResponse(data=detail)


@router.post(
    "/donors/approve",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Donor",
    description=(
        "Sets donor.verified=true, donor.status='approved'. "
        "Hospital name is recorded as the verifying authority."
    ),
)
async def approve_donor(
    payload: ApproveDonorRequest,
    current_user: dict = Depends(require_admin),
):
    result = await admin_service.approve_donor(
        admin_user_id=current_user["sub"],
        donor_id=payload.donor_id,
        notes=payload.notes,
    )
    return BaseResponse(message=result["message"], data=result)


@router.post(
    "/donors/reject",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject Donor",
    description=(
        "Sets donor.verified=false, donor.status='rejected'. "
        "Rejection reason is stored and visible to the admin."
    ),
)
async def reject_donor(
    payload: RejectDonorRequest,
    current_user: dict = Depends(require_admin),
):
    result = await admin_service.reject_donor(
        admin_user_id=current_user["sub"],
        donor_id=payload.donor_id,
        rejection_reason=payload.rejection_reason,
    )
    return BaseResponse(message=result["message"], data=result)


@router.get(
    "/receivers",
    response_model=BaseResponse,
    summary="List All Receivers",
)
async def list_receivers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: str = Query("all", pattern=r"^(all|pending|approved|rejected)$"),
    current_user: dict = Depends(require_admin),
):
    result = await admin_service.list_all_receivers(
        admin_user_id=current_user["sub"],
        page=page,
        page_size=page_size,
        status_filter=status_filter,
    )
    return BaseResponse(data=result)


@router.get(
    "/receivers/{receiver_id}",
    response_model=BaseResponse,
    summary="Get Full Receiver Detail",
)
async def get_receiver_detail(
    receiver_id: str,
    current_user: dict = Depends(require_admin),
):
    detail = await admin_service.get_receiver_detail(current_user["sub"], receiver_id)
    return BaseResponse(data=detail)


@router.post("/donors/{donor_id}/approve", response_model=BaseResponse)
async def approve_donor_v2(donor_id: str, current_user: dict = Depends(require_admin)):
    result = await admin_service.approve_donor(current_user["sub"], donor_id)
    return BaseResponse(message="Donor approved", data=result)


@router.post("/donors/{donor_id}/reject", response_model=BaseResponse)
async def reject_donor_v2(donor_id: str, current_user: dict = Depends(require_admin)):
    result = await admin_service.reject_donor(current_user["sub"], donor_id, rejection_reason="Administrative rejection")
    return BaseResponse(message="Donor rejected", data=result)


@router.post("/receivers/{receiver_id}/approve", response_model=BaseResponse)
async def approve_receiver_route(receiver_id: str, current_user: dict = Depends(require_admin)):
    result = await admin_service.approve_receiver(current_user["sub"], receiver_id)
    return BaseResponse(message="Receiver approved", data=result)


@router.post("/receivers/{receiver_id}/reject", response_model=BaseResponse)
async def reject_receiver_route(receiver_id: str, current_user: dict = Depends(require_admin)):
    result = await admin_service.reject_receiver(current_user["sub"], receiver_id)
    return BaseResponse(message="Receiver rejected", data=result)
