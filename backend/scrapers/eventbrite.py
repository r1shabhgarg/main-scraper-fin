from typing import List, Dict, Any
from scrapers.base import BaseScraper

class EventbriteScraper(BaseScraper):
    def __init__(self):
        super().__init__("Eventbrite", "https://www.eventbrite.com/d/india/student-events/")

    def scrape(self) -> List[Dict[str, Any]]:
        html = self.fetch_html(self.base_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
        events = []
        
        cards = soup.select("div.event-card")
        for card in cards:
            try:
                title_elem = card.select_one("div.event-card__title")
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                link_elem = card.select_one("a.event-card-link")
                link = link_elem["href"] if link_elem else ""
                
                events.append({
                    "title": title,
                    "event_type": "conference",
                    "platform": "Eventbrite",
                    "event_date": None,
                    "deadline": None,
                    "location": "Online",
                    "link": link,
                    "tags": ["student", "conference"],
                    "prize": None,
                    "description": ""
                })
            except Exception as e:
                pass
                
        return events
