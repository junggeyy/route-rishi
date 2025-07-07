from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.services.firestore_service import get_firestore_service
from app.middleware.auth_middleware import get_current_user_required
from app.schemas.auth_schemas import UserResponse
from app.schemas.conversation_schemas import Conversation, ConversationMetadata
from app.schemas.chat_schemas import ChatMessage
from typing import List
import logging

router = APIRouter(prefix="/conversations", tags=["conversations"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ConversationMetadata])
async def get_user_conversations(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of conversations per page"),
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Get user's conversations with pagination.
    
    Returns:
        List[ConversationMetadata]: List of user's conversations
    """
    try:
        firestore_service = get_firestore_service()
        conversations = await firestore_service.get_user_conversations(
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
        return conversations
    except Exception as e:
        logger.error(f"Error getting conversations for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )

@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Get a specific conversation with its details.
    """
    try:
        firestore_service = get_firestore_service()
        
        # Check if user owns the conversation
        if not await firestore_service.user_owns_conversation(current_user.id, conversation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        conversation = await firestore_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )

@router.get("/{conversation_id}/messages", response_model=List[ChatMessage])
async def get_conversation_messages(
    conversation_id: str,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of messages per page"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Message order: 'asc' or 'desc'"),
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Get messages from a specific conversation.
    """
    try:
        firestore_service = get_firestore_service()
        
        # Check if user owns the conversation
        if not await firestore_service.user_owns_conversation(current_user.id, conversation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        messages = await firestore_service.get_messages(
            conversation_id=conversation_id,
            page=page,
            page_size=page_size,
            order=order
        )
        
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for conversation {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user_required)
):
    """
    Delete a specific conversation and all its messages.
    """
    try:
        firestore_service = get_firestore_service()
        
        # Check if user owns the conversation
        if not await firestore_service.user_owns_conversation(current_user.id, conversation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        success = await firestore_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        ) 