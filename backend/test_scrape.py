import asyncio
from scrapers import DevpostScraper, UnstopScraper, EventbriteScraper, CollegeFestScraper
from services.processor import normalize_event
import json
import uuid
from datetime import datetime

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return obj.hex
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

async def test_scrapers():
    scrapers = [CollegeFestScraper(), DevpostScraper(), EventbriteScraper(), UnstopScraper()]
    
    for scraper in scrapers:
        print(f"--- Testing {scraper.name} Scraper ---")
        try:
            events = await asyncio.to_thread(scraper.scrape)
            print(f"Found {len(events)} events from {scraper.name}.")
            if events:
                print("First event AFTER normalization (Smart Layer applied):")
                norm = normalize_event(events[0])
                print(json.dumps(norm, indent=2, cls=UUIDEncoder))
        except Exception as e:
            print(f"Error testing {scraper.name}: {e}")
        print("\n")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
