"""Password hashing and verification using bcrypt"""

from passlib.context import CryptContext
from typing import Tuple

# Create bcrypt context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    Args: plain text password
    Returns: hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    Args:
        plain_password: plain text password
        hashed_password: bcrypt hashed password
    Returns: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
