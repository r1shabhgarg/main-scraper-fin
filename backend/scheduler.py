import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db.database import AsyncSessionLocal
from db import crud
import schemas
from services.processor import normalize_event
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_and_store_events():
    logger.info("Starting background scraping job...")
    
    # Lazy imports to prevent crashing the API process on platforms like Vercel
    from scrapers import (
        DevpostScraper, UnstopScraper, EventbriteScraper, CollegeFestScraper, 
        MLHScraper, DevfolioScraper, HackerEarthScraper, AllEventsScraper, TenTimesScraper
    )

    scrapers = [
        DevpostScraper(),
        UnstopScraper(),
        EventbriteScraper(),
        CollegeFestScraper(),
        MLHScraper(),
        DevfolioScraper(),
        HackerEarthScraper(),
        AllEventsScraper(),
        TenTimesScraper()
    ]
    
    all_events = []
    for s in scrapers:
        try:
            logger.info(f"Running scraper: {s.name}")
            events = await asyncio.to_thread(s.scrape)
            
            valid_events = []
            if events:
                for event in events:
                    title = event.get("title", "")
                    link = event.get("link", "")
                    if not title or not str(title).strip():
                        continue
                    if not link or not str(link).startswith("http"):
                        continue
                    valid_events.append(event)
                    
            if len(valid_events) == 0:
                logger.error(f"{s.name}: 0 events -> ERROR (blocked or selector failed or empty results)")
            else:
                logger.info(f"{s.name}: {len(valid_events)} events scraped successfully.")
                
            all_events.extend(valid_events)
        except Exception as e:
            logger.error(f"{s.name}: 0 events -> ERROR ({str(e)})")
            
    logger.info(f"Scraped {len(all_events)} valid events total. Normalizing and storing...")
    
    async with AsyncSessionLocal() as db:
        new_count = 0
        for raw_event in all_events:
            if not raw_event.get("link"):
                continue
                
            norm_event = normalize_event(raw_event)
            if not norm_event:
                continue
                
            link = norm_event.get("link")
            title = norm_event.get("title", "").strip()
            
            exists_link = await crud.get_event_by_link(db, link)
            exists_title = await crud.get_event_by_title(db, title)
            if not exists_link and not exists_title:
                try:
                    event_in = schemas.EventCreate(**norm_event)
                    await crud.create_event(db, event_in)
                    new_count += 1
                except Exception as e:
                    logger.error(f"Failed to insert event {link}: {e}")
                    
        logger.info(f"Inserted {new_count} new events.")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Run every 6 hours, starting immediately
    scheduler.add_job(fetch_and_store_events, 'interval', hours=6, next_run_time=datetime.now())
    scheduler.start()
    logger.info("Scheduler started.")
