from typing import List, Dict, Any
from scrapers.base import BaseScraper

class TenTimesScraper(BaseScraper):
    def __init__(self):
        # Using a broad queries for student events
        super().__init__("10Times", "https://10times.com/india/education")

    def scrape(self) -> List[Dict[str, Any]]:
        html = self.fetch_html(self.base_url)
        events = []
        if not html: return events
        soup = self.parse_html(html)
        
        for row in soup.select("tr.event-row"):
            try:
                name_elem = row.select_one("a.event-name")
                if not name_elem: continue
                title = name_elem.text.strip()
                link = name_elem.get("href", "")
                
                events.append({
                    "title": title,
                    "event_type": "",
                    "platform": "10Times",
                    "event_date": None,
                    "deadline": None,
                    "location": "India",
                    "link": link,
                    "tags": ["education", "conference"],
                    "prize": None,
                    "description": ""
                })
            except Exception:
                pass
        return events
