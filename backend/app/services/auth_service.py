import logging
from datetime import datetime, timezone
from fastapi import HTTPException, status
from typing import Optional, Dict, Any, Set

from app.services.firebase_service import FirebaseService
from app.services.firebase_client_service import firebase_client_service
from app.services.jwt_service import JWTService
from app.schemas.auth_schemas import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    RefreshTokenRequest
)
logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service handling user signup, login, token management"""

    def __init__(self, firebase_service: FirebaseService, jwt_service: JWTService):
        self.firebase = firebase_service
        self.firebase_client = firebase_client_service
        self.jwt = jwt_service
        # Simple in-memory token blacklist for logout
        self._blacklisted_tokens: Set[str] = set()
    
    async def signup_with_email(self, signup_data: SignupRequest)-> AuthResponse:
        """
        Create a new user account with email and password.
        
        Args:
            signup_data: User registration information
            
        Returns:
            AuthResponse: User data with access and refresh tokens
            
        Raises:
            HTTPException: If user already exists or validation fails
        """
        try:
            if not signup_data.fullName.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Full name is required"
                )

            # creating the user in Firebase Auth
            firebase_user = await self._create_firebase_user(
                email=signup_data.email,
                password=signup_data.password,
                display_name=signup_data.fullName
            )

            # user profile for Firestore
            user_profile = await self._create_user_profile(
                uid=firebase_user['uid'],
                email=signup_data.email,
                full_name=signup_data.fullName,
                provider='email'
            )

            # generate JWT tokens and user response
            tokens = await self._generate_token_pair(firebase_user['uid'])
            user_response = self._create_user_response(user_profile, firebase_user)

            logger.info(f"User successfully created for: {signup_data.email}")
            return AuthResponse(
                user=user_response,
                token=tokens['access_token'],
                refreshToken=tokens['refresh_token']
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Signup failed for {signup_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account creation failed. Please try again."
            )
    
    async def login_with_email(self, login_data: LoginRequest) -> AuthResponse:
        """
        Authenticate user with email and password.
        
        Args:
            login_data: User login credentials
            
        Returns:
            AuthResponse: User data with access and refresh tokens
            
        Raises:
            HTTPException: If credentials are invalid
        """
        try:
            # Basic validation - Pydantic handles email format
            if not login_data.email.strip() or not login_data.password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email and password are required"
                )

            firebase_user = await self._authenticate_firebase_user(
                login_data.email,
                login_data.password
            )

            if not firebase_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            user_profile = await self.firebase.get_user_profile(firebase_user['uid'])

            if not user_profile:
                # creating profile if it doesn't exist
                user_profile = await self._create_user_profile(
                    uid=firebase_user['uid'],
                    email=firebase_user['email'],
                    full_name=firebase_user.get('display_name', ''),
                    provider='email'
                )
            #update last login
            await self._update_last_login(firebase_user['uid'])

            tokens = await self._generate_token_pair(firebase_user['uid'])
            user_response = self._create_user_response(user_profile, firebase_user)
            
            logger.info(f"User successfully logged in: {login_data.email}")
            
            return AuthResponse(
                user=user_response,
                token=tokens['access_token'],
                refreshToken=tokens['refresh_token']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed for {login_data.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login failed. Please check your credentials."
            )
        
    async def refresh_access_token(self, refresh_request: RefreshTokenRequest)-> AuthResponse:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_request: Contains the refresh token
            
        Returns:
            AuthResponse: New access token and user data
            
        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        try:
            token_data = self.jwt.verify_refresh_token(refresh_request.refreshToken)

            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )

            user_id = token_data.get('sub')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token data"
                )
            
            firebase_user = await self.firebase.get_user_by_uid(user_id)
            user_profile = await self.firebase.get_user_profile(user_id)

            if not firebase_user or not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            tokens = await self._generate_token_pair(user_id)
            user_response = self._create_user_response(user_profile, firebase_user)

            logger.info(f"Token refreshed for user: {user_id}")
            
            return AuthResponse(
                user=user_response,
                token=tokens['access_token'],
                refreshToken=tokens['refresh_token']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )

    async def logout(self, user_id: str, access_token: str = None) -> bool:
        """
        Logout user and invalidate tokens.
        
        Args:
            user_id: User's unique identifier
            access_token: Optional access token to blacklist
            
        Returns:
            bool: Success status
        """
        try:
            # Add token to blacklist if provided
            if access_token:
                self._blacklisted_tokens.add(access_token)
                logger.info(f"Token blacklisted for user: {user_id}")
            
            logger.info(f"User logged out: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Logout failed for user {user_id}: {str(e)}")
            return False
        
    async def get_user_by_token(self, access_token: str) -> Optional[UserResponse]:
        """
        Get user information from access token.
        
        Args:
            access_token: JWT access token
            
        Returns:
            UserResponse: User information or None if invalid
        """
        try:
            # Periodically clean up expired tokens (every ~100 calls)
            if len(self._blacklisted_tokens) > 0 and len(self._blacklisted_tokens) % 100 == 0:
                self._cleanup_expired_tokens()
            
            # Check if token is blacklisted (logged out)
            if access_token in self._blacklisted_tokens:
                logger.info("Token is blacklisted (user logged out)")
                return None
            
            token_data = self.jwt.verify_access_token(access_token)
            
            if not token_data:
                return None
            
            user_id = token_data.get('sub')
            if not user_id:
                return None

            firebase_user = await self.firebase.get_user_by_uid(user_id)
            user_profile = await self.firebase.get_user_profile(user_id)
            
            if not firebase_user or not user_profile:
                return None
            
            return self._create_user_response(user_profile, firebase_user)
            
        except Exception as e:
            logger.error(f"Get user by token failed: {str(e)}")
            return None

    ### PRIVATE HELPER METHODS

    async def _create_firebase_user(self, email: str, password: str, display_name: str) -> Dict[str, Any]:
        """Create user in Firebase Auth"""
        try:
            client_result = await self.firebase_client.create_user_with_email_password(
                email=email, 
                password=password, 
                display_name=display_name
            )
            
            if client_result:
                if client_result.get("success"):
                    return {
                        'uid': client_result['uid'],
                        'email': client_result['email'],
                        'display_name': display_name,
                        'id_token': client_result.get('id_token'),
                        'firebase_refresh_token': client_result.get('refresh_token')
                    }
                elif client_result.get("error") == "EMAIL_EXISTS":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User with this email already exists"
                    )
                elif client_result.get("error") == "WEAK_PASSWORD":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password is too weak. Please choose a stronger password."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=client_result.get("message", "User creation failed")
                    )
            
            # Fallback to Firebase Admin SDK if client service fails
            from firebase_admin import auth
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
                email_verified=False
            )
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Firebase user creation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed. Please try again."
            )

    async def _create_user_profile(self, uid: str, email: str, full_name: str, provider: str) -> Dict[str, Any]:
        """Create user profile in Firestore - delegates to firebase_service"""
        user_data = {
            'email': email,
            'display_name': full_name,
            'provider': provider,
            'full_name': full_name
        }
        
        success = await self.firebase.create_user_profile(uid, user_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create user profile")
        
        return await self.firebase.get_user_profile(uid)

    async def _authenticate_firebase_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Firebase Auth using proper password verification"""
        try:
            auth_result = await self.firebase_client.sign_in_with_email_password(email, password)
            
            if auth_result and auth_result.get("success"):
                return {
                    'uid': auth_result['uid'],
                    'email': auth_result['email'],
                    'display_name': auth_result.get('display_name', ''),
                    'id_token': auth_result.get('id_token'),
                    'firebase_refresh_token': auth_result.get('refresh_token')
                }
            return None
        except Exception as e:
            logger.error(f"Firebase authentication error: {str(e)}")
            return None

    async def _generate_token_pair(self, user_id: str) -> Dict[str, str]:
        """Generate access and refresh token pair"""
        token_data = {"sub": user_id}
        
        access_token = self.jwt.create_access_token(token_data)
        refresh_token = self.jwt.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def _create_user_response(self, user_profile: Dict[str, Any], firebase_user: Dict[str, Any]) -> UserResponse:
        """Create UserResponse from profile and Firebase user data"""
        return UserResponse(
            id=firebase_user['uid'],
            email=firebase_user['email'],
            fullName=user_profile.get('full_name', user_profile.get('display_name', '')),
            provider=user_profile.get('provider', 'email')
        )

    async def _update_last_login(self, uid: str) -> None:
        """Update user's last login timestamp"""
        await self.firebase.update_user_profile(uid, {
            'last_login': datetime.now(timezone.utc)
        })
    
    def _cleanup_expired_tokens(self) -> None:
        """
        Clean up expired tokens from blacklist.
        simple cleanup for now.
        """
        expired_tokens = []
        current_time = datetime.now(timezone.utc).timestamp()
        
        for token in self._blacklisted_tokens:
            try:
                # Try to decode token to check expiration
                payload = self.jwt.verify_token(token)
                if not payload or payload.get('exp', 0) < current_time:
                    expired_tokens.append(token)
            except Exception:
                # If token can't be decoded, it's probably expired/invalid
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self._blacklisted_tokens.discard(token)
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens from blacklist")