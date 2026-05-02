"""Utility validators"""

import re
from typing import Optional


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username
    Requirements:
    - 3-255 characters
    - Alphanumeric and underscore only
    """
    if len(username) < 3 or len(username) > 255:
        return False, "Username must be between 3 and 255 characters"
    
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain alphanumeric characters and underscore"
    
    return True, "Username is valid"
