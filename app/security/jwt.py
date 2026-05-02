"""JWT token generation and verification"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import get_settings

settings = get_settings()


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token
    Args:
        subject: User ID or identifier
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional claims to include
    Returns: JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token
    Args: JWT token string
    Returns: Token claims dictionary
    Raises: JWTError if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token
    Args: JWT token string
    Returns: User ID (subject)
    Raises: JWTError if token is invalid
    """
    payload = verify_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise JWTError("Invalid token: no subject found")
    return user_id
