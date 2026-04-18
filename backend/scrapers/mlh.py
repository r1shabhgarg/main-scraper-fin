from typing import List, Dict, Any
from scrapers.base import BaseScraper

class MLHScraper(BaseScraper):
    def __init__(self):
        super().__init__("MLH", "https://mlh.io/seasons/2026/events")

    def scrape(self) -> List[Dict[str, Any]]:
        html = self.fetch_html(self.base_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
        events = []
        
        for event in soup.select("div.event-wrapper"):
            try:
                title = event.select_one("h3.event-name").text.strip()
                link = event.select_one("a.event-link")["href"]
                date = event.select_one("p.event-date").text.strip()
                location = event.select_one("div.event-location").text.strip()
                
                events.append({
                    "title": title,
                    "event_type": "", # let smart layer decide
                    "platform": "MLH",
                    "event_date": date,
                    "deadline": None,
                    "location": location,
                    "link": link,
                    "tags": ["hackathon"],
                    "prize": None,
                    "description": ""
                })
            except Exception:
                continue
                
        return events
