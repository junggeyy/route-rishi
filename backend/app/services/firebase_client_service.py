import requests
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class FirebaseClientService:
    """Firebase Client Authentication Service using REST API"""
    
    def __init__(self):
        self.api_key = settings.FIREBASE_WEB_API_KEY
        self.base_url = "https://identitytoolkit.googleapis.com/v1/accounts"
    
    async def sign_in_with_email_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password using Firebase REST API
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dict containing user data and tokens if successful, None if failed
        """
        try:
            url = f"{self.base_url}:signInWithPassword"
            params = {"key": self.api_key}
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, params=params, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "uid": data.get("localId"),
                    "email": data.get("email"),
                    "id_token": data.get("idToken"),
                    "refresh_token": data.get("refreshToken"),
                    "expires_in": data.get("expiresIn"),
                    "display_name": data.get("displayName", "")
                }
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Authentication failed")
                logger.warning(f"Firebase sign-in failed for {email}: {error_message}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error during Firebase sign-in: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Firebase sign-in: {str(e)}")
            return None
    
    async def create_user_with_email_password(self, email: str, password: str, display_name: str = "") -> Optional[Dict[str, Any]]:
        """
        Create a new user with email and password using Firebase REST API
        
        Args:
            email: User's email address
            password: User's password
            display_name: User's display name
            
        Returns:
            Dict containing user data if successful, None if failed
        """
        try:
            url = f"{self.base_url}:signUp"
            params = {"key": self.api_key}
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, params=params, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                user_data = {
                    "success": True,
                    "uid": data.get("localId"),
                    "email": data.get("email"),
                    "id_token": data.get("idToken"),
                    "refresh_token": data.get("refreshToken"),
                    "expires_in": data.get("expiresIn")
                }
                
                if display_name:
                    await self._update_profile(data.get("idToken"), display_name)
                    user_data["display_name"] = display_name
                
                return user_data
            else:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "User creation failed")
                logger.warning(f"Firebase user creation failed for {email}: {error_message}")
                
                # Handle specific error cases
                if "EMAIL_EXISTS" in error_message:
                    return {"success": False, "error": "EMAIL_EXISTS", "message": "User with this email already exists"}
                elif "WEAK_PASSWORD" in error_message:
                    return {"success": False, "error": "WEAK_PASSWORD", "message": "Password is too weak"}
                else:
                    return {"success": False, "error": "UNKNOWN", "message": error_message}
                
        except requests.RequestException as e:
            logger.error(f"Network error during Firebase user creation: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during Firebase user creation: {str(e)}")
            return None
    
    async def _update_profile(self, id_token: str, display_name: str) -> bool:
        """
        Update user profile with display name
        
        Args:
            id_token: Firebase ID token
            display_name: User's display name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}:update"
            params = {"key": self.api_key}
            
            payload = {
                "idToken": id_token,
                "displayName": display_name,
                "returnSecureToken": False
            }
            
            response = requests.post(url, params=params, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and get user info
        
        Args:
            id_token: Firebase ID token to verify
            
        Returns:
            Dict containing user data if valid, None if invalid
        """
        try:
            url = f"{self.base_url}:lookup"
            params = {"key": self.api_key}
            
            payload = {
                "idToken": id_token
            }
            
            response = requests.post(url, params=params, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                if users:
                    user = users[0]
                    return {
                        "uid": user.get("localId"),
                        "email": user.get("email"),
                        "display_name": user.get("displayName", ""),
                        "email_verified": user.get("emailVerified", False)
                    }
            return None
            
        except Exception as e:
            logger.error(f"Error verifying ID token: {str(e)}")
            return None

firebase_client_service = FirebaseClientService() 