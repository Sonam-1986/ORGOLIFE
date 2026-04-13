"""
Reusable FastAPI dependencies:
  - get_current_user  → any authenticated user
  - require_donor     → only Donor role
  - require_receiver  → only Receiver role
  - require_admin     → only Hospital Admin role
"""
from fastapi import Depends, HTTPException, status
from app.core.security import get_token_payload
from app.models.user import UserRole


# ── Generic authenticated user ────────────────────────────────────

def get_current_user(payload: dict = Depends(get_token_payload)) -> dict:
    """
    Returns the token payload dict:
      { sub: user_id, role: ..., name: ..., email: ... }
    Any authenticated role passes.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identity."
        )
    return payload


# ── Role-specific guards ──────────────────────────────────────────

def _require_role(required_role: UserRole):
    """Factory that returns a dependency enforcing a specific role."""
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: '{required_role}'. "
                       f"Your role: '{current_user.get('role')}'."
            )
        return current_user
    return role_checker


require_donor = _require_role(UserRole.DONOR)
require_receiver = _require_role(UserRole.RECEIVER)
require_admin = _require_role(UserRole.HOSPITAL_ADMIN)


# ── Pagination query params ───────────────────────────────────────

from fastapi import Query

def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
) -> dict:
    return {"page": page, "page_size": page_size, "skip": (page - 1) * page_size}
