"""
Role-based access control (RBAC) dependency.

Usage in a router:
    @router.post("/", dependencies=[Depends(require_role(RoleEnum.ADMIN))])
"""

from functools import wraps
from typing import List

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import Employee, RoleEnum


def require_role(*allowed_roles: RoleEnum):
    """
    Returns a FastAPI dependency that checks the current user's role
    against a whitelist.  Raises 403 if the role is not permitted.
    """
    def role_checker(current_user: Employee = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not authorized. "
                       f"Required: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker
