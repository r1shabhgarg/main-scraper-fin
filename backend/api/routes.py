from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db.database import get_db
from db import crud
import schemas

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=List[schemas.EventResponse])
async def read_events(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="Filter by event type"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    sort: Optional[str] = Query(None, description="Sort by 'date' for upcoming"),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_events(
        db=db, skip=skip, limit=limit, 
        event_type=type, tag=tag, sort_by_date=(sort == "date")
    )

@router.get("/recommended", response_model=List[schemas.EventResponse])
async def get_recommended(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await crud.get_events(db=db, skip=skip, limit=limit, recommended=True)

@router.get("/ending-soon", response_model=List[schemas.EventResponse])
async def get_ending_soon(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await crud.get_events(db=db, skip=skip, limit=limit, ending_soon=True)

from services.ai_search import aggregate_search

@router.post("/search", response_model=schemas.SearchResponse)
async def ai_search_endpoint(
    request: schemas.SearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced AI Search Agent Endpoint mapping DDG, Serper, and Internal APIs via an LLM.
    """
    return await aggregate_search(db=db, query=request.query)

from sqlalchemy.future import select
from sqlalchemy import or_
from db.models import Event

@router.get("/export")
@router.options("/export")
async def export_events(
    q: Optional[str] = Query(None, description="Search/filter string"),
    category: Optional[str] = Query(None, description="Event category"),
    db: AsyncSession = Depends(get_db)
):
    """
    Export events in a customized JSON shape for external integrations.
    Supports filtering by generic search query 'q' and 'category'.
    """
    query = select(Event)
    
    if q:
        search_term = f"%{q.lower()}%"
        # Case-insensitive match against title and description (and summary just in case)
        query = query.filter(
            or_(
                Event.title.ilike(search_term),
                Event.description.ilike(search_term),
                Event.summary.ilike(search_term)
            )
        )
        
    if category:
        # Match categories gracefully handling plural forms like 'hackathons' -> 'hackathon'
        cat_search = category.lower()
        if cat_search.endswith('s'):
            cat_search = cat_search[:-1]
        cat_search = f"%{cat_search}%"
        query = query.filter(Event.event_type.ilike(cat_search))
        
    result = await db.execute(query.order_by(Event.created_at.desc()))
    events = result.scalars().all()
    
    events_list = []
    for e in events:
        def format_date(dt):
            if not dt: return "TBA"
            return dt.strftime("%b %d, %Y")
        
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
            
        desc = e.summary if e.summary else e.description
        if not desc:
            desc = "No description available."
            
        events_list.append({
            "title": e.title,
            "date": date_str,
            "location": e.location or "Online",
            "description": desc,
            "url": e.link,
            "source": e.platform
        })
        
    # The JSON structure returned exactly matches the user request: {"events": [...]}
    # FastAPI's CORSMiddleware handles OPTIONS and proper headers globally.
    return {"events": events_list}

