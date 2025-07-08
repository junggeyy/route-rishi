from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse
from app.agent.travel_agent import travel_agent
from app.schemas.chat_schemas import ChatRequest, ChatResponse, ChatResponseWithReasoning, ChatMessage
from app.schemas.conversation_schemas import Conversation
from app.services.firestore_service import get_firestore_service
from app.middleware.auth_middleware import (
    get_current_user_with_guest_limit,
    increment_guest_chat,
    get_guest_chat_status
)
from typing import Dict, Any
from datetime import datetime, timezone
import logging
import asyncio
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory store for SSE connections
sse_connections = {}

def generate_message_id(conversation_id: str, role: str) -> str:
    """Generate a unique message ID"""
    timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    import random
    return f"msg_{timestamp_ms}_{random.randint(1000, 9999)}_{role}"

@router.get("/chat/stream/{conversation_id}")
async def stream_chat_updates(conversation_id: str, request: Request):
    """Server-Sent Events stream for real-time chat updates"""
    
    async def event_stream():
        # Register this connection
        client_id = f"{conversation_id}_{id(request)}"
        sse_connections[client_id] = {
            'conversation_id': conversation_id,
            'queue': asyncio.Queue()
        }
        
        try:
            yield f"data: {json.dumps({'type': 'connected', 'conversation_id': conversation_id})}\n\n"
            
            while True:
                # Check if client is still connected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for new message with timeout
                    message = await asyncio.wait_for(
                        sse_connections[client_id]['queue'].get(), 
                        timeout=30
                    )
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
        finally:
            # Clean up connection
            if client_id in sse_connections:
                del sse_connections[client_id]
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

def broadcast_to_conversation(conversation_id: str, message_data: dict):
    """Send message to all clients listening to this conversation"""
    for client_id, connection in sse_connections.items():
        if connection['conversation_id'] == conversation_id:
            try:
                connection['queue'].put_nowait(message_data)
            except:
                # Queue full or connection dead, ignore
                pass

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
        
        # Get Firestore service for conversation management
        firestore_service = get_firestore_service()
        
        # Ensure conversation exists in Firestore
        conversation = await firestore_service.get_conversation(request.conversation_id)
        if not conversation:
            # Create new conversation - ensure we have a valid user
            if not user and not is_guest:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User must be authenticated to create conversations"
                )
            
            now = datetime.now(timezone.utc)
            new_conversation = Conversation(
                id=request.conversation_id,
                title="New Conversation",
                created_at=now,
                updated_at=now,
                user_id=user.id if user else "guest",
                is_guest=is_guest,
                message_count=0,
                last_message_at=None
            )
            await firestore_service.create_conversation(new_conversation)
        
        # Create and save user message
        user_message = ChatMessage(
            id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{request.conversation_id}_user",
            role="user",
            content=request.message.strip(),
            timestamp=datetime.now(timezone.utc),
            conversation_id=request.conversation_id
        )
        await firestore_service.add_message(user_message)
        
        # Broadcast user message via SSE
        broadcast_to_conversation(request.conversation_id, {
            'type': 'new_message',
            'message': {
                'id': user_message.id,
                'role': user_message.role,
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat(),
                'conversation_id': user_message.conversation_id
            }
        })
        
        # Get AI response
        user_context = {"user_id": user.id} if user else None
        response = await travel_agent.run_query_async(
            user_query=request.message,
            conversation_id=request.conversation_id,
            user_context=user_context
        )
        
        # Create and save AI message
        ai_message = ChatMessage(
            id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{request.conversation_id}_ai",
            role="assistant",
            content=response,
            timestamp=datetime.now(timezone.utc),
            conversation_id=request.conversation_id
        )
        await firestore_service.add_message(ai_message)
        
        # Broadcast AI message via SSE
        broadcast_to_conversation(request.conversation_id, {
            'type': 'new_message',
            'message': {
                'id': ai_message.id,
                'role': ai_message.role,
                'content': ai_message.content,
                'timestamp': ai_message.timestamp.isoformat(),
                'conversation_id': ai_message.conversation_id
            }
        })
        
        # Update conversation title if it's the first user message
        if not conversation or conversation.message_count == 0:
            title = request.message.strip()[:50] + ("..." if len(request.message.strip()) > 50 else "")
            await firestore_service.update_conversation(request.conversation_id, {"title": title})
        
        # Increment guest chat count after successful response
        if is_guest:
            increment_guest_chat(http_request)
        
        # Add user context to response
        chat_response = ChatResponse(
            response=response,
            conversation_id=request.conversation_id,
            user_id=user.id if user else None,
            message_id=ai_message.id
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
        
        # Get Firestore service for conversation management
        firestore_service = get_firestore_service()
        
        # Ensure conversation exists in Firestore
        conversation = await firestore_service.get_conversation(request.conversation_id)
        if not conversation:
            # Create new conversation - ensure we have a valid user
            if not user and not is_guest:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User must be authenticated to create conversations"
                )
            
            now = datetime.now(timezone.utc)
            new_conversation = Conversation(
                id=request.conversation_id,
                title="New Conversation",
                created_at=now,
                updated_at=now,
                user_id=user.id if user else "guest",
                is_guest=is_guest,
                message_count=0,
                last_message_at=None
            )
            await firestore_service.create_conversation(new_conversation)
        
        # Create and save user message
        user_message = ChatMessage(
            id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{request.conversation_id}_user",
            role="user",
            content=request.message.strip(),
            timestamp=datetime.now(timezone.utc),
            conversation_id=request.conversation_id
        )
        await firestore_service.add_message(user_message)
        
        # Broadcast user message via SSE
        broadcast_to_conversation(request.conversation_id, {
            'type': 'new_message',
            'message': {
                'id': user_message.id,
                'role': user_message.role,
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat(),
                'conversation_id': user_message.conversation_id
            }
        })
        
        # Using the reasoning method
        user_context = {"user_id": user.id} if user else None
        response_data = await travel_agent.run_query_with_reasoning(
            user_query=request.message,
            conversation_id=request.conversation_id,
            user_context=user_context
        )
        
        # Create and save AI message with tool calls
        ai_message = ChatMessage(
            id=f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{request.conversation_id}_ai",
            role="assistant",
            content=response_data["response"],
            timestamp=datetime.now(timezone.utc),
            conversation_id=request.conversation_id,
            tool_calls=response_data.get("tool_calls"),
            execution_time_ms=response_data.get("total_execution_time_ms")
        )
        await firestore_service.add_message(ai_message)
        
        # Broadcast AI message via SSE
        broadcast_to_conversation(request.conversation_id, {
            'type': 'new_message',
            'message': {
                'id': ai_message.id,
                'role': ai_message.role,
                'content': ai_message.content,
                'timestamp': ai_message.timestamp.isoformat(),
                'conversation_id': ai_message.conversation_id,
                'tool_calls': [tc.dict() for tc in ai_message.tool_calls] if ai_message.tool_calls else None,
                'execution_time_ms': ai_message.execution_time_ms
            }
        })
        
        # Update conversation title if it's the first user message
        if not conversation or conversation.message_count == 0:
            title = request.message.strip()[:50] + ("..." if len(request.message.strip()) > 50 else "")
            await firestore_service.update_conversation(request.conversation_id, {"title": title})
        
        # Increment guest chat count after successful response
        if is_guest:
            increment_guest_chat(http_request)
        
        # Add user and message context to response
        response_data["user_id"] = user.id if user else None
        response_data["message_id"] = ai_message.id
        
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
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": datetime.now(timezone.utc).isoformat()
    } 