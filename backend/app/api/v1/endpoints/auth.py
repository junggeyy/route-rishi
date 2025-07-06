from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.services.auth_service import AuthService
from app.services.firebase_service import firebase_service
from app.services.jwt_service import JWTService
from app.middleware.auth_middleware import get_current_user_required
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