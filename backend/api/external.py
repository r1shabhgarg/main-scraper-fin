from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timezone
import asyncio

from db.database import get_db
from db.models import Event

router = APIRouter(prefix="/api", tags=["jarvis_api"])

# In-memory cache for performance optimization as requested
CACHE = {}
CACHE_TTL = 300  # 5 minutes

@router.get("/events")
async def get_external_events(
    category: Optional[str] = Query(None, description="Filter by category (e.g. quiz, workshop)"),
    keyword: Optional[str] = Query(None, description="Keyword search in title/description"),
    date: Optional[str] = Query(None, description="Optional date filter (YYYY-MM-DD or simply YYYY-MM)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns events in a clean JSON format for Jarvis.
    """
    try:
        # Cache key based on query params
        cache_key = f"events_{category}_{keyword}_{date}"
        now = datetime.now(timezone.utc).timestamp()
        
        if cache_key in CACHE:
            data, timestamp = CACHE[cache_key]
            if now - timestamp < CACHE_TTL:
                return data
                
        query = select(Event)
        
        if category:
            cat_search = category.lower()
            if cat_search.endswith('s') and cat_search not in ["series"]:
                cat_search = cat_search[:-1]  # basic singularization
            query = query.filter(Event.event_type.ilike(f"%{cat_search}%"))
            
        if keyword:
            query = query.filter(
                or_(
                    Event.title.ilike(f"%{keyword}%"),
                    Event.description.ilike(f"%{keyword}%"),
                    Event.summary.ilike(f"%{keyword}%")
                )
            )
            
        if date:
            # We filter for events occurring on or after the requested date String prefix
            # E.g. "2024-10" matches "2024-10-xx", but as a datetime we'll filter events newer than the parsed value
            try:
                # If exact YYYY-MM-DD
                if len(date) == 10:
                    parsed_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                elif len(date) == 7: # YYYY-MM
                    parsed_date = datetime.strptime(date, "%Y-%m").replace(tzinfo=timezone.utc)
                else: # fallback to year
                    parsed_date = datetime.strptime(date[:4], "%Y").replace(tzinfo=timezone.utc)
                query = query.filter(Event.event_date >= parsed_date)
            except Exception as e:
                # If date format is unrecognized, just ignore the filter or handle elegantly
                pass
                
        result = await db.execute(query.order_by(Event.event_date.asc().nulls_last()))
        events = result.scalars().all()
        
        formatted_events = []
        for e in events:
            # The schema requires: id, title, description, category, date, link, image
            formatted_events.append({
                "id": str(e.id),
                "title": e.title,
                "description": e.summary or e.description or "No description available.",
                "category": e.event_type,
                "date": e.event_date.isoformat() if e.event_date else None,
                "link": e.link,
                "image": None  # Assuming no image field in db initially, keeping it None to match schema
            })
            
        CACHE[cache_key] = (formatted_events, now)
        return formatted_events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Returns all available categories dynamically.
    """
    try:
        cache_key = "categories"
        now = datetime.now(timezone.utc).timestamp()
        
        if cache_key in CACHE:
            data, timestamp = CACHE[cache_key]
            if now - timestamp < CACHE_TTL:
                return data
                
        # Group by and get distinct
        # distinct() on column might be backend-dependent, let's use straightforward approach 
        # that definitely works on SQLite and Postgres
        query = select(Event.event_type)
        result = await db.execute(query)
        # Using a set to get unique categories, mapping to standard readable formats
        raw_categories = set(row[0] for row in result.all() if row[0])
        
        categories = sorted(list(raw_categories))
        
        CACHE[cache_key] = (categories, now)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
