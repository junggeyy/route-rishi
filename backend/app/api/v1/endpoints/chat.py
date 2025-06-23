from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.agent.travel_agent import travel_agent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to the RouteRishi AI agent and get a response.
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
        
        # Use the async version of the agent
        response = await travel_agent.run_query_async(
            user_query=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again."
        )

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