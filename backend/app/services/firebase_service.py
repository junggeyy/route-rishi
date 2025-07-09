import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from typing import Optional, Dict, Any
from app.core.config import settings
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            service_account_key = settings.FIREBASE_SERVICE_ACCOUNT_KEY
            if not service_account_key:
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY not found in environment variables")
            
            service_account_info = json.loads(service_account_key)
            cred = credentials.Certificate(service_account_info)

            # initializing the app if not initialized
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                })
            else:
                self._app = firebase_admin.get_app()

            # initializing the Firestore db
            self._db = firestore.client()

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Firebase credentials JSON: {e}")
            raise ValueError("Invalid JSON format in FIREBASE_SERVICE_ACCOUNT_KEY")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return decoded token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.InvalidIdTokenError:
            logger.warning("Invalid ID token provided")
            return None
        except auth.ExpiredIdTokenError:
            logger.warning("Expired ID token provided")
            return None
        except Exception as e:
            logger.error(f"Error verifying ID token: {str(e)}")
            return None
        
    async def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user information from Firebase Auth"""
        try:
            user_record = auth.get_user(uid)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'created_at': user_record.user_metadata.creation_timestamp,
                'last_sign_in': user_record.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            logger.warning(f"User not found: {uid}")
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user information from Firebase Auth by email"""
        try:
            user_record = auth.get_user_by_email(email)
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'created_at': user_record.user_metadata.creation_timestamp,
                'last_sign_in': user_record.user_metadata.last_sign_in_timestamp
            }
        except auth.UserNotFoundError:
            logger.warning(f"User not found with email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
        
    async def create_user_profile(self, uid: str, user_data: Dict[str, Any]) -> bool:
        """Create user profile in Firestore"""
        try:
            user_ref = self._db.collection('users').document(uid)
            
            profile_data = {
                'uid': uid,
                'email': user_data.get('email'),
                'display_name': user_data.get('display_name'),
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }

            user_ref.set(profile_data, merge=True)
            logger.info(f"user profile created for uid: {uid}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return False
        
    async def get_user_profile(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user profile from Firestore"""
        try:
            user_ref = self._db.collection('users').document(uid)
            doc = user_ref.get()

            if doc.exists:
                return doc.to_dict()
            return None
        
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    async def update_user_profile(self, uid: str, update_data: Dict[str, Any]) -> bool:
        """Update user profile in Firestore"""
        try:
            user_ref = self._db.collection('users').document(uid)
            
            update_data['updated_at'] = datetime.now(timezone.utc)
            
            user_ref.update(update_data)
            logger.info(f"User profile updated for uid: {uid}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False

    async def save_conversation(
        self, 
        uid: str, 
        conversation_id: str, 
        conversation_data: Dict[str, Any]
    ) -> bool:
        """Save conversation to Firestore"""
        try:
            conversation_ref = (
                self._db.collection('users')
                .document(uid)
                .collection('conversations')
                .document(conversation_id)
            )

            conversation_data.update({
                'updated_at': datetime.now(timezone.utc),
                'user_id': uid
            })

            conversation_ref.set(conversation_data, merge=True)
            return True
    
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return False
    
    async def get_user_conversations(self, uid: str, limit: int = 50) -> list:
        """Get user's conversations from Firestore"""
        try:
            conversations_ref = (
                self._db.collection('users')
                .document(uid)
                .collection('conversations')
                .order_by('updated_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
            )

            docs = conversations_ref.stream()
            conversations = []

            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                conversations.append(data)

            return conversations
    
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            return []
        
    async def get_conversation(self, uid: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get specific conversation"""
        try:
            conversation_ref = (
                self._db.collection('users')
                .document(uid)
                .collection('conversations')
                .document(conversation_id)
            )
            
            doc = conversation_ref.get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return None
        
    async def delete_conversation(self, uid: str, conversation_id: str) -> bool:
        """Delete a conversation"""
        try:
            conversation_ref = (
                self._db.collection('users')
                .document(uid)
                .collection('conversations')
                .document(conversation_id)
            )
            
            conversation_ref.delete()
            logger.info(f"Conversation deleted: {conversation_id} for user: {uid}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False
        

firebase_service = FirebaseService()