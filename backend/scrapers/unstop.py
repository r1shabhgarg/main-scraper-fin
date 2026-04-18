from typing import List, Dict, Any
from scrapers.base import BaseScraper
import random
import time
from playwright.sync_api import sync_playwright
import json

class UnstopScraper(BaseScraper):
    def __init__(self):
        super().__init__("Unstop", "https://unstop.com/competitions")

    def scrape(self) -> List[Dict[str, Any]]:
        events = []
        api_data = []

        # Intercept the API response using Playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Adding some stealth arguments
                context = browser.new_context(
                    user_agent=self.headers["User-Agent"],
                    viewport={'width': 1280, 'height': 720}
                )
                page = context.new_page()

                def handle_response(response):
                    if "opportunity/search-result" in response.url and response.status == 200:
                        try:
                            # We only care about the JSON search result
                            if response.request.method == "GET":
                                api_data.append(response.json())
                        except Exception:
                            pass

                page.on("response", handle_response)

                # Go to the category pages which trigger the search-result API
                for url in [
                    "https://unstop.com/competitions",
                    "https://unstop.com/hackathons",
                    "https://unstop.com/workshops",
                    "https://unstop.com/quizzes"
                ]:
                    try:
                        page.goto(url, wait_until="networkidle", timeout=30000)
                        # Scroll a bit to make sure requests are triggered
                        page.evaluate("window.scrollBy(0, 500)")
                        time.sleep(2)
                    except Exception as e:
                        print(f"[{self.name}] Playwright warning loading {url}: {e}")

                browser.close()
        except Exception as e:
            print(f"[{self.name}] Playwright error: {e}")

        # Parse extracted API data
        try:
            for response_json in api_data:
                data_list = response_json.get("data", {}).get("data", [])
                for item in data_list:
                    op_type = str(item.get("opportunity_type", "")).lower()
                    
                    if "quiz" in op_type:
                        event_type = "quiz"
                    elif "workshop" in op_type:
                        event_type = "workshop"
                    elif "hackathon" in op_type:
                        event_type = "hackathon"
                    else:
                        event_type = "competition"
                        
                    title = item.get("title", "")
                    if not title:
                        continue
                        
                    events.append({
                        "title": title,
                        "event_type": event_type,
                        "platform": "Unstop",
                        "event_date": item.get("start_date"),
                        "deadline": item.get("end_date"),
                        "location": "Online" if item.get("is_online") else item.get("location"),
                        "link": f"https://unstop.com/{item.get('public_url')}",
                        "tags": [cat.get("name") for cat in item.get("categories", [])] if type(item.get("categories")) == list else [],
                        "prize": item.get("prize"),
                        "description": item.get("short_description")
                    })
        except Exception as e:
            print(f"[{self.name}] Parse error: {e}")
            
        print(f"[{self.name}] Scraped {len(events)} events.")
        return events
