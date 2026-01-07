"""
Role-Based Access Control (RBAC) middleware for MediAI API

Provides role management and permission checking for protected endpoints.
"""

from enum import Enum
from functools import wraps
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

from .security import User, get_current_user


class Role(str, Enum):
    """User roles with hierarchical permissions"""

    ADMIN = "admin"  # Full access
    DOCTOR = "doctor"  # Can view/create predictions, view patients
    NURSE = "nurse"  # Can view predictions, limited write
    RESEARCHER = "researcher"  # Read-only access for analytics
    VIEWER = "viewer"  # Basic read-only access


class RolePermissions:
    """Maps roles to allowed permissions"""

    PERMISSIONS = {
        Role.ADMIN: ["*"],  # Wildcard = all permissions
        Role.DOCTOR: [
            "predictions:read",
            "predictions:write",
            "patients:read",
            "patients:write",
            "doctors:read",
            "chat:read",
            "chat:write",
        ],
        Role.NURSE: [
            "predictions:read",
            "patients:read",
            "doctors:read",
            "chat:read",
        ],
        Role.RESEARCHER: [
            "predictions:read",
            "analytics:read",
            "doctors:read",
        ],
        Role.VIEWER: [
            "predictions:read",
            "doctors:read",
        ],
    }

    @classmethod
    def has_permission(cls, role: Role, permission: str) -> bool:
        """Check if a role has a specific permission"""
        role_perms = cls.PERMISSIONS.get(role, [])
        if "*" in role_perms:
            return True
        return permission in role_perms


class UserWithRole(User):
    """Extended user model with role information"""

    role: Role = Role.VIEWER
    permissions: List[str] = []


# Mock user database for demo (replace with real DB in production)
DEMO_USERS = {
    "admin": UserWithRole(
        username="admin",
        email="admin@mediai.com",
        full_name="System Administrator",
        role=Role.ADMIN,
        disabled=False,
    ),
    "demo": UserWithRole(
        username="demo",
        email="demo@mediai.com",
        full_name="Demo Doctor",
        role=Role.DOCTOR,
        disabled=False,
    ),
    "nurse": UserWithRole(
        username="nurse",
        email="nurse@mediai.com",
        full_name="Demo Nurse",
        role=Role.NURSE,
        disabled=False,
    ),
    "researcher": UserWithRole(
        username="researcher",
        email="researcher@mediai.com",
        full_name="Demo Researcher",
        role=Role.RESEARCHER,
        disabled=False,
    ),
}


async def get_user_with_role(user: User = Depends(get_current_user)) -> UserWithRole:
    """
    Get current user with their role information.
    In production, this would fetch from the database.
    """
    if user.username in DEMO_USERS:
        return DEMO_USERS[user.username]

    # Default to viewer role for unknown users
    return UserWithRole(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=Role.VIEWER,
        disabled=user.disabled,
    )


def require_role(allowed_roles: List[Role]):
    """
    Dependency factory that checks if user has one of the allowed roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: UserWithRole = Depends(require_role([Role.ADMIN]))):
            return {"message": "Welcome admin!"}
    """

    async def role_checker(
        user: UserWithRole = Depends(get_user_with_role),
    ) -> UserWithRole:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return user

    return role_checker


def require_permission(permission: str):
    """
    Dependency factory that checks if user has a specific permission.

    Usage:
        @router.post("/predictions")
        async def create_prediction(
            user: UserWithRole = Depends(require_permission("predictions:write"))
        ):
            return {"message": "Prediction created"}
    """

    async def permission_checker(
        user: UserWithRole = Depends(get_user_with_role),
    ) -> UserWithRole:
        if not RolePermissions.has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {permission}",
            )
        return user

    return permission_checker


# Convenience dependencies for common role checks
require_admin = require_role([Role.ADMIN])
require_doctor = require_role([Role.ADMIN, Role.DOCTOR])
require_medical_staff = require_role([Role.ADMIN, Role.DOCTOR, Role.NURSE])
require_authenticated = require_role(
    [Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RESEARCHER, Role.VIEWER]
)
