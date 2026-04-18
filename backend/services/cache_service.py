import time
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Event

class SimpleCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache = {}
        self._timestamp = 0
        self._lock = asyncio.Lock()

    async def get_all_events(self, db: AsyncSession) -> List[Event]:
        now = time.time()
        async with self._lock:
            # Check if cache is still valid
            if hasattr(self, '_events_cache') and (now - self._timestamp < self.ttl):
                return self._events_cache
            
            # Rehydrate cache
            query = select(Event).order_by(Event.created_at.desc())
            result = await db.execute(query)
            events = result.scalars().all()
            
            self._events_cache = events
            self._timestamp = now
            return self._events_cache

    async def get_all_categories(self, db: AsyncSession) -> List[str]:
        events = await self.get_all_events(db)
        # Extract unique categories (case-insensitive deduplication)
        categories = set()
        for e in events:
            if e.event_type:
                # Lowercase for deduplication, but you can keep title case for display
                categories.add(e.event_type.title())
        return sorted(list(categories))

# Global instance for app-wide caching (5 minutes TTL)
event_cache = SimpleCache(ttl_seconds=300)
