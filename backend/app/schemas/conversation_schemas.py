from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .chat_schemas import ChatMessage

class ConversationMetadata(BaseModel):
    """Metadata of a conversation"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    message_count: int = 0
    is_guest: bool = False

class Conversation(BaseModel):
    """Full conversation"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    is_guest: bool = False
    message_count: int = 0
    last_message_at: Optional[datetime] = None

class ConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    title: Optional[str] = None  # auto-generates if not provided
    user_id: Optional[str] = None 

class ConversationCreateResponse(BaseModel):
    """Response when creating a new conversation"""
    conversation_id: str
    title: str
    created_at: datetime
    user_id: Optional[str] = None

class ConversationUpdate(BaseModel):
    """Schema for updating conversation metadata"""
    title: Optional[str] = None

class ConversationList(BaseModel):
    """Schema for listing user conversations"""
    conversations: List[ConversationMetadata]
    total_count: int
    page: int
    page_size: int

class MessageListRequest(BaseModel):
    """Request for fetching messages from a conversation"""
    conversation_id: str
    page: int = 1
    page_size: int = 50
    user_id: Optional[str] = None

class MessageListResponse(BaseModel):
    """Response containing messages with pagination"""
    messages: List[ChatMessage]
    conversation_id: str
    total_count: int
    page: int
    page_size: int
    has_more: bool