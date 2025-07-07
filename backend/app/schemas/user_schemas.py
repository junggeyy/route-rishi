from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class SavedItineraryDocument(BaseModel):
    id: str
    title: str
    destination: str
    start_date: date
    end_date: date
    pdf_url: str
    created_at: datetime
    file_size_mb: float

class UserProfile(BaseModel):
    uid: str
    email: EmailStr
    display_name: str
    created_at: datetime
    updated_at: datetime
    saved_itineraries: List[SavedItineraryDocument] = []

