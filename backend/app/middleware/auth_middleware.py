from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
import time

from app.services.auth_service import AuthService
from app.services.firebase_service import firebase_service
from app.services.jwt_service import JWTService
from app.schemas.auth_schemas import UserResponse

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)

# Guest session tracking
guest_sessions: Dict[str, Dict[str, Any]] = {}

class AuthMiddleware:
    """Authentication middleware for handling JWT tokens and guest limits"""
    
    def __init__(self):
        self.auth_service = AuthService(firebase_service, JWTService())
        self.GUEST_CHAT_LIMIT = 5
        self.GUEST_SESSION_DURATION = 24 * 60 * 60 
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address for guest session tracking"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _get_guest_session_key(self, request: Request) -> str:
        """Generate guest session key based on IP and user agent"""
        ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")
        return f"guest_{ip}_{hash(user_agent)}"
    
    def _cleanup_expired_guest_sessions(self):
        """Remove expired guest sessions"""
        current_time = time.time()
        expired_keys = []
        
        for key, session in guest_sessions.items():
            if current_time - session.get("created_at", 0) > self.GUEST_SESSION_DURATION:
                expired_keys.append(key)
        
        for key in expired_keys:
            del guest_sessions[key]
    
    def _get_or_create_guest_session(self, request: Request) -> Dict[str, Any]:
        """Get or create guest session for tracking chat limits"""
        self._cleanup_expired_guest_sessions()
        
        session_key = self._get_guest_session_key(request)
        
        if session_key not in guest_sessions:
            guest_sessions[session_key] = {
                "chat_count": 0,
                "created_at": time.time(),
                "last_chat_at": 0
            }
        
        return guest_sessions[session_key]
    
    def _increment_guest_chat_count(self, request: Request) -> None:
        """Increment guest chat count and update last chat time"""
        session = self._get_or_create_guest_session(request)
        session["chat_count"] += 1
        session["last_chat_at"] = time.time()
    
    async def verify_token(self, credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[UserResponse]:
        """
        Verify JWT token and return user information
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            UserResponse if token is valid, None if invalid/missing
        """
        if not credentials:
            return None
        
        try:
            token = credentials.credentials
            user = await self.auth_service.get_user_by_token(token)
            return user
        except Exception as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None

# global instance
auth_middleware = AuthMiddleware()

# Dependency functions for different protection levels

async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserResponse]:
    """
    Get current user if authenticated, None if not.
    Used for endpoints that work for both auth and guest users.
    """
    return await auth_middleware.verify_token(credentials)

async def get_current_user_required(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserResponse:
    """
    Require authentication. Raises 401 if not authenticated.
    Used for endpoints that require authentication.
    """
    user = await auth_middleware.verify_token(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

async def get_current_user_with_guest_limit(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Allow authenticated users OR guests with chat limits.
    Used for chat endpoints that support guest users with limitations.
    
    Returns:
        Dict with 'user' (UserResponse or None) and 'is_guest' (bool)
    """
    user = await auth_middleware.verify_token(credentials)
    
    if user:
        # Authenticated user - no limits
        return {"user": user, "is_guest": False}
    
    # Guest user - check limits
    guest_session = auth_middleware._get_or_create_guest_session(request)
    
    if guest_session["chat_count"] >= auth_middleware.GUEST_CHAT_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Guest chat limit reached. Please sign up for unlimited access. Limit: {auth_middleware.GUEST_CHAT_LIMIT} chats per 24 hours."
        )
    
    return {"user": None, "is_guest": True}

def increment_guest_chat(request: Request) -> None:
    """
    Increment guest chat count. Call this after successful chat completion.
    """
    auth_middleware._increment_guest_chat_count(request)

def get_guest_chat_status(request: Request) -> Dict[str, Any]:
    """
    Get guest chat status for frontend display.
    
    Returns:
        Dict with chat count and limit information
    """
    guest_session = auth_middleware._get_or_create_guest_session(request)
    
    return {
        "chat_count": guest_session["chat_count"],
        "chat_limit": auth_middleware.GUEST_CHAT_LIMIT,
        "remaining_chats": max(0, auth_middleware.GUEST_CHAT_LIMIT - guest_session["chat_count"]),
        "is_limit_reached": guest_session["chat_count"] >= auth_middleware.GUEST_CHAT_LIMIT
    }
