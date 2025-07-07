from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ToolCall(BaseModel):
    """Represents a single tool call made by the agent"""
    tool_name: str
    input_params: Dict[str, Any]
    output: str
    status: str  # "running", "completed", "error"
    execution_time_ms: Optional[int] = None

class ChatMessage(BaseModel):
    """Individual message in a conversation"""
    id: str # unique message ID
    role: str   # user or assistant
    content: str
    timestamp: datetime
    conversation_id: str    # reference to parent conversation
    tool_calls: Optional[List[ToolCall]] = None
    execution_time_ms: Optional[int] = None

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str
    conversation_id: str
    user_id: Optional[str] = None # optional for guest users

class ChatResponse(BaseModel):
    """Basic response model for chat messages"""
    response: str
    conversation_id: str
    user_id: Optional[str] = None
    message_id: Optional[str] = None # ID of the agent's message

class ChatResponseWithReasoning(BaseModel):
    """Enhanced response model that includes agent reasoning steps"""
    response: str
    conversation_id: str
    user_id: Optional[str] = None
    message_id: Optional[str] = None 
    tool_calls: List[ToolCall]
    total_execution_time_ms: Optional[int] = None
    reasoning_enabled: bool = True 