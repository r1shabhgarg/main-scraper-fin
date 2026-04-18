from typing import List, Dict, Any
from scrapers.base import BaseScraper
from datetime import datetime

class DevpostScraper(BaseScraper):
    def __init__(self):
        super().__init__("Devpost", "https://devpost.com/api/hackathons")

    def scrape(self) -> List[Dict[str, Any]]:
        # Using devpost API logic if possible, otherwise mock it up or use soup
        # Note: robust scraping requires handling pagination. Mocking basic fields for now.
        data = self.fetch_json(self.base_url)
        events = []
        
        if not data or "hackathons" not in data:
            # Fallback to HTML if API is strictly protected
            return self._scrape_html()
            
        for h in data.get("hackathons", []):
            try:
                events.append({
                    "title": h.get("title", "Unknown"),
                    "event_type": "hackathon",
                    "platform": "Devpost",
                    "event_date": None,
                    "deadline": None,
                    "location": h.get("location", "Online"),
                    "link": h.get("url", ""),
                    "tags": [t.get("name", "") for t in h.get("themes", [])],
                    "prize": str(h.get("prize_amount", "")),
                    "description": ""
                })
            except Exception as e:
                print(f"[{self.name}] Parse error: {e}")
                
        return events
        
    def _scrape_html(self) -> List[Dict[str, Any]]:
        html = self.fetch_html("https://devpost.com/hackathons")
        if not html:
            # Fallback to playwright
            print(f"[{self.name}] Trying playwright fallback for HTML...")
            html = self.fetch_html_playwright("https://devpost.com/hackathons", wait_for_selector="div.hackathon-tile")
            
        if not html:
            return []
            
        soup = self.parse_html(html)
        events = []
        
        for hackathon in soup.select("div.hackathon-tile"):
            try:
                title_elem = hackathon.select_one("h3.title")
                title = title_elem.text.strip() if title_elem else "Unknown Hackathon"
                
                link_elem = hackathon.select_one("a.clearfix")
                link = link_elem["href"] if link_elem else self.base_url
                
                location_elem = hackathon.select_one("div.info span.info-icon")
                location = location_elem.find_next_sibling(text=True).strip() if location_elem and location_elem.find_next_sibling(text=True) else "Online"
                
                tags = [t.text.strip() for t in hackathon.select("span.theme-label")]
                
                prize_elem = hackathon.select_one("span.prize-amount")
                prize = prize_elem.text.strip() if prize_elem else None
                
                events.append({
                    "title": title,
                    "event_type": "hackathon",
                    "platform": "Devpost",
                    "event_date": None,
                    "deadline": None,
                    "location": location,
                    "link": link,
                    "tags": tags,
                    "prize": prize,
                    "description": ""
                })
            except Exception as e:
                print(f"[{self.name}] Parse error: {e}")
                continue
                
        return events
