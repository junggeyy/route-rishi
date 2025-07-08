from google.cloud.firestore_v1 import FieldFilter
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone, date
import uuid
import logging
import firebase_admin
from firebase_admin import firestore

from app.schemas.chat_schemas import ChatMessage
from app.schemas.conversation_schemas import Conversation, ConversationMetadata
from app.schemas.user_schemas import UserProfile, SavedItineraryDocument

logger = logging.getLogger(__name__)

class FirestoreService:
    def __init__(self):
        """Initialize Firestore client using existing Firebase app"""
        try:
            # Ensure Firebase is initialized 
            if not firebase_admin._apps:
                logger.info("Firebase not initialized, initializing via FirebaseService...")
                from app.services.firebase_service import FirebaseService
                FirebaseService() 
            
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully using Firebase Admin SDK!")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise

    ### Conversation methods

    async def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation"""
        try:
            doc_ref = self.db.collection('conversations').document(conversation.id)
            doc_ref.set(conversation.model_dump())
            logger.info(f"Created conversation: {conversation.id}")
            return conversation.id
        except Exception as e:
            logger.error(f"Failed to create conversation {conversation.id}: {e}")
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        try:
            doc_ref = self.db.collection('conversations').document(conversation_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                return Conversation(**data)
            return None
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            raise

    async def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update conversation metadata"""
        try:
            doc_ref = self.db.collection('conversations').document(conversation_id)
            updates['updated_at'] = datetime.now(timezone.utc)
            doc_ref.update(updates)
            logger.info(f"Updated conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update conversation {conversation_id}: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        try:
            batch = self.db.batch()

            # delete all messages in the conversation
            messages_ref = (self.db.collection('conversations')
                            .document(conversation_id)
                            .collection('messages'))
            messages = messages_ref.stream()
            for message in messages:
                batch.delete(message.reference)
            
            # delete the conversation document
            conv_ref = self.db.collection('conversations').document(conversation_id)
            batch.delete(conv_ref)

            batch.commit()
            logger.info(f"Deleted conversation {conversation_id} and all messages")
            return True
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False
        
    async def get_user_conversations(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    )-> List[ConversationMetadata]:
        """get user's conversations with pagination"""
        try:
            query = (self.db.collection('conversations')
                     .where(filter=FieldFilter('user_id', '==', user_id)))
            
            docs = query.stream()
            conversations = []

            for doc in docs:
                data = doc.to_dict()
                # Ensure we have all required fields with defaults
                created_at = data.get('created_at', datetime.now(timezone.utc))
                updated_at = data.get('updated_at', datetime.now(timezone.utc))
                
                if isinstance(created_at, datetime):
                    created_at = created_at.isoformat()
                if isinstance(updated_at, datetime):
                    updated_at = updated_at.isoformat()
                
                conversation_data = {
                    'id': doc.id,
                    'title': data.get('title', 'New Conversation'),
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'user_id': data.get('user_id', user_id),
                    'message_count': data.get('message_count', 0),
                    'is_guest': data.get('is_guest', False),
                }
                conversations.append(ConversationMetadata(**conversation_data))

            # Sort by updated_at(newest first)
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_conversations = conversations[start_idx:end_idx]

            logger.info(f"Retrieved {len(paginated_conversations)} conversations for user {user_id} (page {page})")
            return paginated_conversations
        except Exception as e:
            logger.error(f"Failed to get conversations for user {user_id}: {e}")
            raise
    
    ### Message methods

    async def add_message(self, message: ChatMessage) -> str:
        """Add a message to a conversation"""
        try:
            # using batch to ensure atomicity
            batch = self.db.batch()

            # add message to subcollection
            message_ref = (self.db.collection('conversations')
                           .document(message.conversation_id)
                           .collection('messages')
                           .document(message.id))
            batch.set(message_ref, message.model_dump())

            # update conversation metadata
            conv_ref = self.db.collection('conversations').document(message.conversation_id)
            batch.update(conv_ref, {
                'message_count': firestore.Increment(1),
                'last_message_at': message.timestamp,
                'updated_at': message.timestamp
            })

            batch.commit()
            logger.info(f"Added message {message.id} to conversation {message.conversation_id}")
            return message.id
        except Exception as e:
            logger.error(f"Failed to add message {message.id}: {e}")
            raise

    async def get_messages(
        self,
        conversation_id: str,
        page: int = 1,
        page_size: int = 50,
        order: str = 'asc'
    ) -> List[ChatMessage]:
        """Get messages from a conversation"""
        try:
            direction = firestore.Query.ASCENDING if order == 'asc' else firestore.Query.DESCENDING

            query = (self.db.collection('conversations')
                     .document(conversation_id)
                     .collection('messages')
                     .order_by('timestamp', direction=direction)
                     .limit(page_size)
                     .offset((page - 1) * page_size))
            
            docs = query.stream()
            messages = []

            for doc in docs:
                data = doc.to_dict()
                messages.append(ChatMessage(**data))


            logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages
        except Exception as e:
            logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
            raise
    
    async def get_conversation_history(
        self, 
        conversation_id: str, 
        limit: int = 20
    ) -> List[ChatMessage]:
        """Get recent conversation history for AI context"""
        try:
            query = (self.db.collection('conversations')
                    .document(conversation_id)
                    .collection('messages')
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            docs = query.stream()
            messages = []
            
            for doc in docs:
                data = doc.to_dict()
                messages.append(ChatMessage(**data))
            
            # Return in chronological order (oldest first)
            messages.reverse()
            return messages
        except Exception as e:
            logger.error(f"Failed to get history for conversation {conversation_id}: {e}")
            raise
    
    async def update_message(self, message_id: str, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update a specific message"""
        try:
            message_ref = (self.db.collection('conversations')
                          .document(conversation_id)
                          .collection('messages')
                          .document(message_id))
            message_ref.update(updates)
            logger.info(f"Updated message {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update message {message_id}: {e}")
            return False
    
    ### User methods

    async def create_user_profile(self, user_profile: UserProfile) -> str:
        """Create a new user profile"""
        try:
            doc_ref = self.db.collection('users').document(user_profile.uid)
            doc_ref.set(user_profile.model_dump())
            logger.info(f"Created user profile: {user_profile.uid}")
            return user_profile.uid
        except Exception as e:
            logger.error(f"Failed to create user profile {user_profile.uid}: {e}")
            raise

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return UserProfile(**data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile {user_id}: {e}")
            raise

    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            updates['updated_at'] = datetime.now(timezone.utc)
            doc_ref.update(updates)
            logger.info(f"Updated user profile {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user profile {user_id}: {e}")
            return False

    ### Itinerary methods

    async def save_user_itinerary(self, user_id: str, itinerary_doc: SavedItineraryDocument) -> bool:
        """Add a saved itinerary to user's profile"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            
            # Convert the model to dict and handle date serialization
            itinerary_dict = itinerary_doc.model_dump()
            
            # Convert date objects to datetime for Firestore compatibility
            if isinstance(itinerary_dict.get('start_date'), date) and not isinstance(itinerary_dict['start_date'], datetime):
                itinerary_dict['start_date'] = datetime.combine(itinerary_dict['start_date'], datetime.min.time()).replace(tzinfo=timezone.utc)
            if isinstance(itinerary_dict.get('end_date'), date) and not isinstance(itinerary_dict['end_date'], datetime):
                itinerary_dict['end_date'] = datetime.combine(itinerary_dict['end_date'], datetime.min.time()).replace(tzinfo=timezone.utc)
            
            # Use set with merge to ensure the document exists, then update with array union
            # First ensure the document exists with empty itineraries array if needed
            doc_ref.set({
                'saved_itineraries': [],
                'updated_at': datetime.now(timezone.utc)
            }, merge=True)
            
            # Then add the new itinerary
            doc_ref.update({
                'saved_itineraries': firestore.ArrayUnion([itinerary_dict]),
                'updated_at': datetime.now(timezone.utc)
            })
            
            logger.info(f"Saved itinerary {itinerary_doc.id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save itinerary for user {user_id}: {e}")
            return False

    async def get_user_itineraries(self, user_id: str) -> List[SavedItineraryDocument]:
        """Get all saved itineraries for a user"""
        try:
            user_profile = await self.get_user_profile(user_id)
            if user_profile and user_profile.saved_itineraries:
                return user_profile.saved_itineraries
            return []
        except Exception as e:
            logger.error(f"Failed to get itineraries for user {user_id}: {e}")
            return []

    async def delete_user_itinerary(self, user_id: str, itinerary_id: str) -> bool:
        """Remove a saved itinerary from user's profile"""
        try:
            user_profile = await self.get_user_profile(user_id)
            if not user_profile:
                return False
            
            # Find and remove the itinerary
            updated_itineraries = [
                itin for itin in user_profile.saved_itineraries 
                if itin.id != itinerary_id
            ]
            
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update({
                'saved_itineraries': [itin.model_dump() for itin in updated_itineraries],
                'updated_at': datetime.now(timezone.utc)
            })
            
            logger.info(f"Deleted itinerary {itinerary_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete itinerary {itinerary_id} for user {user_id}: {e}")
            return False
        
    ### Utility methods
    async def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        try:
            doc_ref = self.db.collection('conversations').document(conversation_id)
            doc = doc_ref.get()
            return doc.exists
        except Exception as e:
            logger.error(f"Failed to check conversation existence {conversation_id}: {e}")
            return False

    async def user_owns_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Check if user owns a conversation"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return False

            if conversation.is_guest:
                return True
            
            # Check ownership
            return conversation.user_id == user_id
        except Exception as e:
            logger.error(f"Failed to check conversation ownership: {e}")
            return False
        
    def generate_id(self, prefix: str = "") -> str:
        """Generate a unique ID with optional prefix"""
        unique_id = str(uuid.uuid4())
        return f"{prefix}{unique_id}" if prefix else unique_id

    async def cleanup_guest_conversations(self, days_old: int = 30) -> int:
        """Clean up old guest conversations"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            query = (self.db.collection('conversations')
                    .where(filter=FieldFilter('is_guest', '==', True))
                    .where(filter=FieldFilter('created_at', '<', cutoff_date)))
            
            docs = query.stream()
            deleted_count = 0
            
            for doc in docs:
                await self.delete_conversation(doc.id)
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} anonymous conversations")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup anonymous conversations: {e}")
            return 0
        
### Dependency injection

# Singleton instance
_firestore_service = None

def get_firestore_service() -> FirestoreService:
    """Dependency injection for FirestoreService"""
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    return _firestore_service  