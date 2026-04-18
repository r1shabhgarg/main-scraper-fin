from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
import uuid

class EventBase(BaseModel):
    title: str
    event_type: str
    platform: str
    event_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    location: Optional[str] = None
    link: str
    tags: List[str] = []
    prize: Optional[str] = None
    description: Optional[str] = None
    is_beginner_friendly: bool = False
    is_free: bool = True
    summary: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SearchQuery(BaseModel):
    query: str

class SearchItem(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    link: str
    source: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchItem]
