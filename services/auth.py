"""
Authentication helpers wrapping existing auth manager.
Provides simplified interface for user authentication and JWT token management.
"""

from typing import Dict, Any
from services.auth_privacy import get_auth_manager
from database.db_manager import get_db_manager


def create_or_login_user(user_profile: Dict[str, Any]) -> str:
    """
    Create or authenticate user and generate JWT token.
    
    Args:
        user_profile: User profile dictionary containing user_id and other details
        
    Returns:
        JWT token string for authenticated session
    """
    # Save user to database
    db = get_db_manager()
    db.save_user(user_profile)
    
    # Generate JWT token
    auth = get_auth_manager()
    token = auth.generate_jwt_token(user_profile["user_id"], user_profile)
    return token


def logout(user_id: str) -> None:
    """
    Revoke user's authentication token.
    
    Args:
        user_id: Unique user identifier
    """
    auth = get_auth_manager()
    auth.revoke_token(user_id)
