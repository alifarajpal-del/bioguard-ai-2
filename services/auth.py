"""Authentication helpers wrapping existing auth manager."""

from typing import Dict, Any
from services.auth_privacy import get_auth_manager


def create_or_login_user(user_profile: Dict[str, Any]) -> str:
    """Create a token for the given user profile."""
    auth = get_auth_manager()
    token = auth.generate_jwt_token(user_profile["user_id"], user_profile)
    return token


def logout(user_id: str) -> None:
    auth = get_auth_manager()
    auth.revoke_token(user_id)
