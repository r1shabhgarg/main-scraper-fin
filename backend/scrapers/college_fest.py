from typing import List, Dict, Any
from scrapers.base import BaseScraper
from datetime import datetime, timedelta

class CollegeFestScraper(BaseScraper):
    def __init__(self):
        super().__init__("CollegeFest", "https://example-college-fest.com/events")

    def scrape(self) -> List[Dict[str, Any]]:
        print(f"[{self.name}] Scraping placeholder data...")
        # Since this is a placeholder, we generate some fake data
        now = datetime.now()
        data = [
            {
                "title": "Annual Tech Symposium",
                "event_type": "fest",
                "platform": "CollegeFest_Example",
                "event_date": (now + timedelta(days=10)).isoformat(),
                "deadline": (now + timedelta(days=5)).isoformat(),
                "location": "Campus Main Auditorium",
                "link": "https://example-college-fest.com/events/tech-symposium",
                "tags": ["tech", "college", "competition"],
                "prize": "$500",
                "description": "The biggest annual tech symposium."
            },
            {
                "title": "Cultural Dance Off",
                "event_type": "cultural",
                "platform": "CollegeFest_Example",
                "event_date": (now + timedelta(days=15)).isoformat(),
                "deadline": (now + timedelta(days=12)).isoformat(),
                "location": "Open Air Theatre",
                "link": "https://example-college-fest.com/events/dance-off",
                "tags": ["dance", "cultural"],
                "prize": "$200",
                "description": "Showcase your college's dance talent."
            }
        ]
        return data
