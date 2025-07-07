from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GuestSession(BaseModel):
    """For tracking guest user sessions"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    conversation_ids: List[str] = []
    limit: int = 5

class SessionInfo(BaseModel):
    """Current sesson information"""
    session_id: str
    user_id: Optional[str] = None
    is_authenticated: bool = False
    conversation_id: Optional[str] = None
