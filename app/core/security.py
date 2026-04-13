"""
Security helpers — OAuth2 bearer scheme, current-user extraction.

Note: OrgoLife uses JSON-body logins (not form-based OAuth2 flow).
The tokenUrl here is for Swagger UI "Authorize" button only.
Actual token extraction only needs the Authorization: Bearer header.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt_handler import verify_access_token

# Use HTTPBearer instead of OAuth2PasswordBearer since our login endpoints
# accept JSON bodies, not application/x-www-form-urlencoded.
# This also prevents Swagger from sending wrong content-type on /authorize.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency — extracts and validates the Bearer token.
    Raises 401 if token is missing, expired, or tampered with.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
