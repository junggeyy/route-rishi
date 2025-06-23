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

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str
    conversation_id: str

class ChatResponse(BaseModel):
    """Basic response model for chat messages"""
    response: str
    conversation_id: str

class ChatResponseWithReasoning(BaseModel):
    """Enhanced response model that includes agent reasoning steps"""
    response: str
    conversation_id: str
    tool_calls: List[ToolCall]
    total_execution_time_ms: Optional[int] = None
    reasoning_enabled: bool = True 