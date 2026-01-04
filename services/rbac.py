"""
Role-Based Access Control (RBAC) System.
Manages user roles and permissions for secure access control.
"""

import logging
from enum import Enum
from typing import List, Optional, Callable
from functools import wraps
import streamlit as st

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User role definitions."""
    ADMIN = "admin"  # Full access to all features
    USER = "user"  # Standard user access
    GUEST = "guest"  # Limited read-only access
    MODERATOR = "moderator"  # Can manage content but not users


class Permission(Enum):
    """Permission definitions."""
    # User management
    CREATE_USER = "create_user"
    VIEW_USER = "view_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Food analysis
    ANALYZE_FOOD = "analyze_food"
    VIEW_ANALYSIS = "view_analysis"
    DELETE_ANALYSIS = "delete_analysis"
    EXPORT_ANALYSIS = "export_analysis"
    
    # Medical vault
    UPLOAD_MEDICAL_FILE = "upload_medical_file"
    VIEW_MEDICAL_FILE = "view_medical_file"
    DELETE_MEDICAL_FILE = "delete_medical_file"
    
    # System management
    VIEW_SYSTEM_LOGS = "view_system_logs"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_ANALYTICS = "view_analytics"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        # All permissions
        Permission.CREATE_USER,
        Permission.VIEW_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.ANALYZE_FOOD,
        Permission.VIEW_ANALYSIS,
        Permission.DELETE_ANALYSIS,
        Permission.EXPORT_ANALYSIS,
        Permission.UPLOAD_MEDICAL_FILE,
        Permission.VIEW_MEDICAL_FILE,
        Permission.DELETE_MEDICAL_FILE,
        Permission.VIEW_SYSTEM_LOGS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_ANALYTICS,
    ],
    
    UserRole.MODERATOR: [
        Permission.VIEW_USER,
        Permission.ANALYZE_FOOD,
        Permission.VIEW_ANALYSIS,
        Permission.DELETE_ANALYSIS,
        Permission.EXPORT_ANALYSIS,
        Permission.UPLOAD_MEDICAL_FILE,
        Permission.VIEW_MEDICAL_FILE,
        Permission.DELETE_MEDICAL_FILE,
        Permission.VIEW_ANALYTICS,
    ],
    
    UserRole.USER: [
        Permission.ANALYZE_FOOD,
        Permission.VIEW_ANALYSIS,
        Permission.EXPORT_ANALYSIS,
        Permission.UPLOAD_MEDICAL_FILE,
        Permission.VIEW_MEDICAL_FILE,
        Permission.DELETE_MEDICAL_FILE,
    ],
    
    UserRole.GUEST: [
        Permission.VIEW_ANALYSIS,  # Read-only
    ]
}


class RBACService:
    """Role-Based Access Control service."""
    
    def __init__(self):
        """Initialize RBAC service."""
        self.logger = logging.getLogger(__name__)
    
    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: User role
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        permissions = ROLE_PERMISSIONS.get(role, [])
        return permission in permissions
    
    def check_permission(
        self,
        username: str,
        permission: Permission,
        raise_error: bool = True
    ) -> bool:
        """
        Check if user has permission.
        
        Args:
            username: Username to check
            permission: Required permission
            raise_error: Whether to raise error if permission denied
            
        Returns:
            True if user has permission
            
        Raises:
            PermissionError: If user doesn't have permission and raise_error=True
        """
        # Get user role from session or database
        role = self.get_user_role(username)
        
        has_perm = self.has_permission(role, permission)
        
        if not has_perm and raise_error:
            self.logger.warning(f"Permission denied: {username} attempted {permission.value}")
            raise PermissionError(
                f"User '{username}' does not have permission: {permission.value}"
            )
        
        return has_perm
    
    def get_user_role(self, username: str) -> UserRole:
        """
        Get user's role from session or database.
        
        Args:
            username: Username
            
        Returns:
            User's role
        """
        # Check session state first
        if 'user_role' in st.session_state:
            role_str = st.session_state.user_role
            try:
                return UserRole(role_str)
            except ValueError:
                self.logger.error(f"Invalid role in session: {role_str}")
        
        # Default to USER role if not found
        return UserRole.USER
    
    def set_user_role(self, username: str, role: UserRole):
        """
        Set user's role in session.
        
        Args:
            username: Username
            role: Role to set
        """
        st.session_state.user_role = role.value
        self.logger.info(f"Set role for {username}: {role.value}")
    
    def get_available_features(self, role: UserRole) -> List[str]:
        """
        Get list of available features for a role.
        
        Args:
            role: User role
            
        Returns:
            List of feature names
        """
        permissions = ROLE_PERMISSIONS.get(role, [])
        
        features = []
        if Permission.ANALYZE_FOOD in permissions:
            features.append("Food Analysis")
        if Permission.VIEW_ANALYSIS in permissions:
            features.append("Analysis History")
        if Permission.UPLOAD_MEDICAL_FILE in permissions:
            features.append("Medical Vault")
        if Permission.VIEW_ANALYTICS in permissions:
            features.append("Health Dashboard")
        if Permission.MANAGE_SETTINGS in permissions:
            features.append("System Settings")
        
        return features


# Global instance
_rbac_service = None


def get_rbac_service() -> RBACService:
    """Get or create global RBAC service instance."""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


def require_permission(permission: Permission):
    """
    Decorator to require permission for a function.
    
    Args:
        permission: Required permission
        
    Usage:
        @require_permission(Permission.ANALYZE_FOOD)
        def analyze_food_view():
            # Function code
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get current user
            username = st.session_state.get('username')
            
            if not username:
                st.error("⛔ Authentication required")
                st.stop()
            
            # Check permission
            rbac = get_rbac_service()
            try:
                rbac.check_permission(username, permission, raise_error=True)
            except PermissionError as e:
                st.error(f"⛔ {str(e)}")
                st.stop()
            
            # Execute function if permission granted
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(required_role: UserRole):
    """
    Decorator to require specific role for a function.
    
    Args:
        required_role: Required user role
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = st.session_state.get('username')
            
            if not username:
                st.error("⛔ Authentication required")
                st.stop()
            
            rbac = get_rbac_service()
            user_role = rbac.get_user_role(username)
            
            if user_role != required_role and user_role != UserRole.ADMIN:
                st.error(f"⛔ This feature requires {required_role.value} role")
                st.stop()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def show_role_badge(role: UserRole):
    """
    Display role badge in Streamlit UI.
    
    Args:
        role: User role to display
    """
    badge_colors = {
        UserRole.ADMIN: "🔴",
        UserRole.MODERATOR: "🟡",
        UserRole.USER: "🟢",
        UserRole.GUEST: "⚪"
    }
    
    badge = badge_colors.get(role, "⚫")
    st.sidebar.markdown(f"{badge} **Role:** {role.value.capitalize()}")
