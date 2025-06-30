from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.firebase_service import firebase_service
from fastapi import HTTPException, status
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthMiddleWare:
    """Authentication middleware for Firebase ID tokens"""

    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Verify Firebase ID token and return user info"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )
        if not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing"
            )
        
        decoded_token = await firebase_service.verify_id_token(credentials.credentials)

        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return decoded_token
    
    @staticmethod
    async def get_current_user(credentails: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Get current user info"""
        decoded_token = await AuthMiddleWare.verify_token(credentails)
        uid = decoded_token.get('uid')

        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing uid"
            )
        
        # user information from Firebase auth
        user_info = await firebase_service.get_user_by_uid(uid)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # user profile from Firestore
        user_profile = await firebase_service.get_user_profile(uid)

        # create a profile if doesn't exist
        if not user_profile:
            await firebase_service.create_user_profile(uid, user_info)
            user_profile = await firebase_service.get_user_profile(uid)

        return {
            **user_info,
            'profile': user_profile,
            'firebase_claims': decoded_token
        }

auth_middleware = AuthMiddleWare()
