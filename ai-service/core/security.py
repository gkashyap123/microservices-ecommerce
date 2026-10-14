
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError, jwt

from core.config import settings

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> dict:
    # 1. Check that the Authorization header was provided.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Validate the JWT signature, expiry, and claims.
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require_sub": True},
        )

    except JWTError as exc:
        # Log the exception type only. Never log the token or secret.
        logger.warning(
            "JWT validation failed: %s",
            type(exc).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    # 3. Auth Service issues tokens with {"sub": str(user.id)}.
    user_id = payload.get("sub") or payload.get("user_id")

    if user_id is None or not str(user_id).strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is missing a user identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Return the authenticated identity for route authorization.
    return {
        "user_id": str(user_id),
        "claims": payload,
    }
