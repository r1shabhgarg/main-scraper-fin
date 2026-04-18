from typing import List, Dict, Any
from scrapers.base import BaseScraper

class AllEventsScraper(BaseScraper):
    def __init__(self):
        super().__init__("AllEvents", "https://allevents.in/india/all")

    def scrape(self) -> List[Dict[str, Any]]:
        html = self.fetch_html(self.base_url)
        events = []
        if not html: return events
        soup = self.parse_html(html)
        
        for card in soup.select("li.event-item"):
            try:
                title_elem = card.select_one("h3")
                if not title_elem: continue
                title = title_elem.text.strip()
                link = card.get("data-link", self.base_url)
                
                events.append({
                    "title": title,
                    "event_type": "",
                    "platform": "AllEvents",
                    "event_date": None,
                    "deadline": None,
                    "location": "India",
                    "link": link,
                    "tags": [],
                    "prize": None,
                    "description": ""
                })
            except Exception:
                pass
        return events
