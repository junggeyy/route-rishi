from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.middleware.auth_middleware import auth_middleware
from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional

security = HTTPBearer()

# dependency for getting the current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    return await auth_middleware.get_current_user(credentials)

# optional dependency for routes that work with or without auth
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials= Depends(HTTPBearer(auto_error=False))  
) -> Optional[Dict[str, Any]]:
    """FastAPI dependency to get currrent user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await auth_middleware.get_current_user(credentials)
    except HTTPException:
        return None
