from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime

class UserProfile(BaseModel):
    uid: str
    email: EmailStr
    display_name: str
    created_at: datetime
    updated_at: datetime
    
class UserProfile(BaseModel):
    display_name: Optional[str]= None

