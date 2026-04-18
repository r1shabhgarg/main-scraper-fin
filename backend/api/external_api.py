from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from db.database import get_db
from services.cache_service import event_cache

router = APIRouter(prefix="/api", tags=["external_api"])

class ExternalEventResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[str] = None
    link: str
    image: Optional[str] = None

def format_date(dt):
    if not dt: return "TBA"
    return dt.strftime("%b %d, %Y")

@router.get("/events", response_model=List[ExternalEventResponse])
async def get_external_events(
    category: Optional[str] = Query(None, description="Filter by event category (e.g. quiz)"),
    keyword: Optional[str] = Query(None, description="Search keyword in title or description"),
    date: Optional[str] = Query(None, description="Optional date filter string"),
    db: AsyncSession = Depends(get_db)
):
    # Fetch from cache
    all_events = await event_cache.get_all_events(db)
    
    filtered = []
    category_lower = category.lower() if category else None
    keyword_lower = keyword.lower() if keyword else None
    
    for e in all_events:
        # Category filter
        if category_lower:
            evt_type = (e.event_type or "").lower()
            if category_lower not in evt_type and evt_type not in category_lower:
                continue
                
        # Keyword filter
        if keyword_lower:
            searchable = f"{e.title or ''} {e.description or ''} {e.summary or ''}".lower()
            if keyword_lower not in searchable:
                continue
                
        # Date filter mapping (simplified)
        start = format_date(e.event_date)
        end = format_date(e.deadline)
        
        if start == "TBA" and end == "TBA":
            date_str = "TBA"
        elif start == end:
            date_str = start
        elif start == "TBA":
            date_str = f"TBA - {end}"
        elif end == "TBA":
            date_str = f"{start} - TBA"
        else:
            date_str = f"{start} - {end}"
            
        if date and date.lower() not in date_str.lower():
            continue
            
        desc = e.summary if e.summary else e.description
        if not desc:
            desc = "No description available."
            
        filtered.append(ExternalEventResponse(
            id=str(e.id),
            title=e.title,
            description=desc,
            category=e.event_type.title() if e.event_type else None,
            date=date_str,
            link=e.link,
            image=None  # Image is currently not stored in DB
        ))
        
    return filtered

@router.get("/categories", response_model=List[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Dynamically returns all available categories from current data."""
    return await event_cache.get_all_categories(db)
