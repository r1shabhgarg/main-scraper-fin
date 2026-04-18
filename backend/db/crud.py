import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from db.models import Event
import schemas

async def get_events(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    event_type: str | None = None, 
    tag: str | None = None, 
    sort_by_date: bool = False,
    recommended: bool = False,
    ending_soon: bool = False
):
    query = select(Event)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if tag:
        # Cast to string for broad compatibility with JSON lists in sqlite.
        from sqlalchemy import String
        query = query.filter(Event.tags.cast(String).like(f"%{tag}%"))
    if recommended:
        query = query.filter(Event.is_beginner_friendly == True, Event.is_free == True)
    if ending_soon:
        now = datetime.datetime.now(datetime.timezone.utc)
        soon = now + datetime.timedelta(days=3)
        query = query.filter(Event.deadline.between(now, soon))
        
    if sort_by_date:
        query = query.order_by(Event.event_date.asc().nulls_last())
    else:
        query = query.order_by(desc(Event.created_at))
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_event(db: AsyncSession, event: schemas.EventCreate):
    db_event = Event(**event.model_dump())
    try:
        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)
        return db_event
    except Exception as e:
        await db.rollback()
        raise e

async def get_event_by_link(db: AsyncSession, link: str):
    query = select(Event).filter(Event.link == link)
    result = await db.execute(query)
    return result.scalars().first()

async def get_event_by_title(db: AsyncSession, title: str):
    query = select(Event).filter(Event.title == title)
    result = await db.execute(query)
    return result.scalars().first()
