import asyncio
from db.database import AsyncSessionLocal
from services.smart_layer import generate_summary
from sqlalchemy.future import select
from db.models import Event

async def update_summaries():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Event))
        events = result.scalars().all()
        for event in events:
            # We need to construct a dict to pass to generate_summary
            event_dict = {
                "title": event.title,
                "event_type": event.event_type,
                "tags": event.tags,
                "prize": event.prize,
                "is_beginner_friendly": event.is_beginner_friendly,
                "description": event.description,
                "location": event.location
            }
            new_summary = generate_summary(event_dict)
            event.summary = new_summary
        await db.commit()
        print(f"Updated {len(events)} summaries!")

if __name__ == "__main__":
    asyncio.run(update_summaries())
