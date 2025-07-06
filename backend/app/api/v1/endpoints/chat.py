from fastapi import APIRouter, HTTPException, status, Depends, Request
from app.agent.travel_agent import travel_agent
from app.schemas.chat_schemas import ChatRequest, ChatResponse, ChatResponseWithReasoning
from app.middleware.auth_middleware import (
    get_current_user_with_guest_limit,
    increment_guest_chat,
    get_guest_chat_status
)
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    http_request: Request,
    auth_info: Dict[str, Any] = Depends(get_current_user_with_guest_limit)
):
    """
    Send a message to the RouteRishi AI agent and get a response.
    Supports both authenticated users (unlimited) and guest users (5 chats/24h).
    """
    try:
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        if not request.conversation_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation ID cannot be empty"
            )
        
        user = auth_info.get("user")
        is_guest = auth_info.get("is_guest", False)
        
        response = await travel_agent.run_query_async(
            user_query=request.message,
            conversation_id=request.conversation_id
        )
        
        # Increment guest chat count after successful response
        if is_guest:
            increment_guest_chat(http_request)
        
        # Add user context to response
        chat_response = ChatResponse(
            response=response,
            conversation_id=request.conversation_id
        )
        
        return chat_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again."
        )

@router.post("/chat/message-with-reasoning", response_model=ChatResponseWithReasoning)
async def send_message_with_reasoning(
    request: ChatRequest,
    http_request: Request,
    auth_info: Dict[str, Any] = Depends(get_current_user_with_guest_limit)
):
    """
    Send a message to the RouteRishi AI agent and get a response with reasoning steps.
    Supports both authenticated users (unlimited) and guest users (5 chats/24h).
    """
    try:
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        if not request.conversation_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation ID cannot be empty"
            )
        
        user = auth_info.get("user")
        is_guest = auth_info.get("is_guest", False)
        
        # Use the new reasoning method
        response_data = await travel_agent.run_query_with_reasoning(
            user_query=request.message,
            conversation_id=request.conversation_id
        )
        
        # Increment guest chat count after successful response
        if is_guest:
            increment_guest_chat(http_request)
        
        return ChatResponseWithReasoning(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat reasoning endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message with reasoning. Please try again."
        )

@router.get("/chat/guest-status")
async def get_guest_status(http_request: Request):
    """
    Get guest chat status for frontend display.
    Returns chat count, limit, and remaining chats for guest users.
    """
    try:
        status_info = get_guest_chat_status(http_request)
        return {
            "status": "success",
            **status_info
        }
    except Exception as e:
        logger.error(f"Guest status check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "chat_count": 0,
            "chat_limit": 5,
            "remaining_chats": 5,
            "is_limit_reached": False
        }

@router.get("/chat/health")
def chat_health():
    """
    Health check for the chat/agent functionality.
    """
    try:
        health_status = travel_agent.health_check()
        return {
            "status": "healthy",
            "agent_status": health_status,
            "message": "Chat service is operational"
        }
    except Exception as e:
        logger.error(f"Chat health check failed: {str(e)}")
        return {
            "status": "unhealthy", 
            "error": str(e),
            "message": "Chat service is experiencing issues"
        } 