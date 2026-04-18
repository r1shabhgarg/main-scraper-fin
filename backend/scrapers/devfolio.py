from typing import List, Dict, Any
from scrapers.base import BaseScraper

class DevfolioScraper(BaseScraper):
    def __init__(self):
        super().__init__("Devfolio", "https://devfolio.co/hackathons")

    def scrape(self) -> List[Dict[str, Any]]:
        html = self.fetch_html(self.base_url)
        events = []
        if not html: return events
        soup = self.parse_html(html)
        
        for card in soup.select("a"):
            try:
                href = card.get("href", "")
                title = card.text.strip().split("\n")[0]
                if ("/hackathons/" in href or "devfolio.co" in href) and len(title) > 5 and len(title) < 100:
                    events.append({
                        "title": title,
                        "event_type": "",
                        "platform": "Devfolio",
                        "event_date": None,
                        "deadline": None,
                        "location": "Online",
                        "link": href if "http" in href else f"https://devfolio.co{href}",
                        "tags": [],
                        "prize": None,
                        "description": ""
                    })
            except Exception:
                pass
        return events
