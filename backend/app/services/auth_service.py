import logging
from datetime import datetime, timezone
from fastapi import HTTPException, status, Request
from typing import Optional, Dict, Any, Set
import urllib.parse
import secrets
import httpx

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
from app.core.config import settings

logger = logging.getLogger(__name__)

# Module-level OAuth state storage
_oauth_states: Dict[str, Dict[str, Any]] = {}

class AuthService:
    """Authentication service handling user signup, login, token management"""

    def __init__(self, firebase_service: FirebaseService, jwt_service: JWTService):
        self.firebase = firebase_service
        self.firebase_client = firebase_client_service
        self.jwt = jwt_service
        # Simple in-memory token blacklist for logout
        self._blacklisted_tokens: Set[str] = set()
        
        # Google OAuth configuration
        self.google_oauth_config = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "auth_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo"
        }
        

    
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

    async def get_google_oauth_url(self, flow_type: str, request: Request) -> str:
        """
        Generate Google OAuth URL for authentication.
        
        Args:
            flow_type: "login" or "signup"
            request: FastAPI request object
            
        Returns:
            str: Google OAuth authorization URL
        """
        try:
            # Generate secure random state
            state = secrets.token_urlsafe(32)
            
            # Store state with flow type and timestamp
            _oauth_states[state] = {
                "flow_type": flow_type,
                "timestamp": datetime.now(timezone.utc).timestamp(),
                "ip": request.client.host if request.client else "unknown"
            }
            
            # Clean up old states (older than 10 minutes)
            current_time = datetime.now(timezone.utc).timestamp()
            expired_states = [
                s for s, data in _oauth_states.items()
                if current_time - data.get("timestamp", 0) > 600
            ]
            for s in expired_states:
                del _oauth_states[s]
            
            # Build OAuth URL
            params = {
                "client_id": self.google_oauth_config["client_id"],
                "redirect_uri": self.google_oauth_config["redirect_uri"],
                "scope": self.google_oauth_config["scope"],
                "response_type": "code",
                "state": state,
                "access_type": "offline",
                "prompt": "consent"
            }
            
            auth_url = f"{self.google_oauth_config['auth_url']}?{urllib.parse.urlencode(params)}"
            
            logger.info(f"Generated Google OAuth URL for {flow_type}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating Google OAuth URL: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate Google OAuth URL"
            )
    
    async def handle_google_oauth_callback(self, code: str, state: str) -> AuthResponse:
        """
        Handle Google OAuth callback and authenticate/create user.
        
        Args:
            code: Authorization code from Google
            state: State parameter to prevent CSRF
            
        Returns:
            AuthResponse: User data with access and refresh tokens
        """
        try:
            # Verify state
            if state not in _oauth_states:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid OAuth state"
                )
            
            flow_type = _oauth_states[state]["flow_type"]
            del _oauth_states[state]  # Clean up used state
            
            # Exchange code for tokens
            google_tokens = await self._exchange_google_code_for_tokens(code)
            
            # Get user info from Google
            google_user_info = await self._get_google_user_info(google_tokens["access_token"])
            
            # Check if user exists
            existing_user = await self.firebase.get_user_by_email(google_user_info["email"])
            
            if existing_user and flow_type == "signup":
                # User exists but trying to signup
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already exists. Please login instead."
                )
            
            if not existing_user and flow_type == "login":
                # User doesn't exist but trying to login
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found. Please signup first."
                )
            
            # Create or authenticate user
            if existing_user:
                # Existing user login
                user_id = existing_user['uid']
                user_profile = await self.firebase.get_user_profile(user_id)
                
                if not user_profile:
                    # Create profile if missing
                    user_profile = await self._create_user_profile(
                        uid=user_id,
                        email=google_user_info["email"],
                        full_name=google_user_info.get("name", ""),
                        provider="google"
                    )
                
                # Update last login
                await self._update_last_login(user_id)
                
            else:
                # New user signup
                # Create user in Firebase Auth
                firebase_user = await self._create_firebase_user_from_google(google_user_info)
                user_id = firebase_user['uid']
                
                # Create user profile
                user_profile = await self._create_user_profile(
                    uid=user_id,
                    email=google_user_info["email"],
                    full_name=google_user_info.get("name", ""),
                    provider="google"
                )
                
                existing_user = firebase_user
            
            # Generate JWT tokens
            tokens = await self._generate_token_pair(user_id)
            user_response = self._create_user_response(user_profile, existing_user)
            
            logger.info(f"Google OAuth {flow_type} successful for: {google_user_info['email']}")
            
            return AuthResponse(
                user=user_response,
                token=tokens['access_token'],
                refreshToken=tokens['refresh_token']
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Google OAuth callback error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google authentication failed"
            )
    


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

    ### PRIVATE HELPER METHODS FOR GOOGLE OAUTH
    
    async def _exchange_google_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.google_oauth_config["token_url"],
                    data={
                        "client_id": self.google_oauth_config["client_id"],
                        "client_secret": self.google_oauth_config["client_secret"],
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.google_oauth_config["redirect_uri"],
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange authorization code"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token exchange failed"
            )
    
    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.google_oauth_config["userinfo_url"],
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"User info request failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to get user information"
                    )
                
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during user info request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user information"
            )
    
    async def _create_firebase_user_from_google(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create Firebase user from Google user info"""
        try:
            from firebase_admin import auth
            
            user_record = auth.create_user(
                email=google_user_info["email"],
                display_name=google_user_info.get("name", ""),
                email_verified=google_user_info.get("verified_email", False)
            )
            
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified
            }
            
        except Exception as e:
            logger.error(f"Error creating Firebase user from Google: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )