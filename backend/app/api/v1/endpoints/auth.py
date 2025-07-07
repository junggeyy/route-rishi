from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from app.services.auth_service import AuthService
from app.services.firebase_service import firebase_service
from app.services.jwt_service import JWTService
from app.middleware.auth_middleware import get_current_user_required
from app.core.config import settings
from app.schemas.auth_schemas import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    RefreshTokenRequest
)
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

# Dependency injection for auth service
def get_auth_service() -> AuthService:
    return AuthService(firebase_service, JWTService())

@router.post("/signup", response_model=AuthResponse)
async def signup(
    signup_data: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account with email and password.
    
    Args:
        signup_data: User registration information (email, password, fullName)
        
    Returns:
        AuthResponse: User data with access and refresh tokens
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        return await auth_service.signup_with_email(signup_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with email and password.
    
    Args:
        login_data: User login credentials (email, password)
        
    Returns:
        AuthResponse: User data with access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        return await auth_service.login_with_email(login_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed. Please check your credentials."
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
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
        return await auth_service.refresh_access_token(refresh_request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: UserResponse = Depends(get_current_user_required),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user and invalidate tokens.
    
    Args:
        request: Request object to extract token
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Success message
    """
    try:
        # Extract token from Authorization header for blacklisting
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]
        
        success = await auth_service.logout(current_user.id, access_token)
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
    except Exception as e:
        logger.error(f"Logout endpoint error: {str(e)}")
        return {"message": "Logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Get current user information from access token.
    Requires valid JWT authentication.
    
    Returns:
        UserResponse: Current user information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    return current_user 

@router.get("/google/login")
async def google_login_redirect(request: Request):
    """
    Redirect to Google OAuth for login.
    This endpoint initiates the OAuth flow.
    """
    try:
        auth_service = get_auth_service()
        redirect_url = await auth_service.get_google_oauth_url("login", request)
        return {"redirect_url": redirect_url}
    except Exception as e:
        logger.error(f"Google login redirect error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )

@router.get("/google/signup")
async def google_signup_redirect(request: Request):
    """
    Redirect to Google OAuth for signup.
    This endpoint initiates the OAuth flow.
    """
    try:
        auth_service = get_auth_service()
        redirect_url = await auth_service.get_google_oauth_url("signup", request)
        return {"redirect_url": redirect_url}
    except Exception as e:
        logger.error(f"Google signup redirect error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google signup"
        )

@router.get("/google/callback")
async def google_oauth_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None
):
    """
    Handle Google OAuth callback.
    This endpoint processes the OAuth response and redirects back to frontend.
    """
    try:
        if error:
            logger.error(f"Google OAuth error: {error}")
            # Redirect to frontend with error
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error={error}",
                status_code=302
            )
        
        if not code:
            logger.error("No authorization code received")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=No authorization code received",
                status_code=302
            )
        
        auth_service = get_auth_service()
        auth_response = await auth_service.handle_google_oauth_callback(code, state)
        
        # Instead of HTML page, encode auth data in URL parameters
        import json
        import base64
        import urllib.parse
        
        user_dict = auth_response.user.dict()
        
        # Encode auth data safely
        user_data_b64 = base64.b64encode(json.dumps(user_dict).encode('utf-8')).decode('utf-8')
        token_b64 = base64.b64encode(auth_response.token.encode('utf-8')).decode('utf-8')
        refresh_token_b64 = base64.b64encode(auth_response.refreshToken.encode('utf-8')).decode('utf-8')
        
        # Build redirect URL with auth data
        params = {
            'oauth': 'success',
            'token': token_b64,
            'refresh_token': refresh_token_b64,
            'user_data': user_data_b64
        }
        
        redirect_url = f"{settings.FRONTEND_URL}/?{urllib.parse.urlencode(params)}"
        
        logger.info(f"Redirecting to frontend with auth data: {redirect_url[:100]}...")
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except HTTPException as e:
        logger.error(f"Google OAuth callback error: {e.detail}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={e.detail}",
            status_code=302
        )
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=Authentication failed",
            status_code=302
        )

 