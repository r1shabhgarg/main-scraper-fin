from typing import List, Dict, Any
from scrapers.base import BaseScraper

class HackerEarthScraper(BaseScraper):
    def __init__(self):
        super().__init__("HackerEarth", "https://www.hackerearth.com/challenges/")

    def scrape(self) -> List[Dict[str, Any]]:
        html = self.fetch_html(self.base_url)
        events = []
        if not html: return events
        soup = self.parse_html(html)
        
        for challenge in soup.select("div.challenge-card-modern"):
            try:
                title = challenge.select_one("span.challenge-list-title").text.strip()
                link = challenge.select_one("a.challenge-card-link").get("href", "")
                events.append({
                    "title": title,
                    "event_type": "",
                    "platform": "HackerEarth",
                    "event_date": None,
                    "deadline": None,
                    "location": "Online",
                    "link": link if "http" in link else f"https://www.hackerearth.com{link}",
                    "tags": ["coding"],
                    "prize": None,
                    "description": ""
                })
            except Exception:
                pass
        return events
