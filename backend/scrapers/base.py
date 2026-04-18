import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import random
import time
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

class BaseScraper:
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9"
        }

    def fetch_html(self, url: str) -> str | None:
        try:
            # random delay to avoid rate limiting
            time.sleep(random.uniform(1.0, 3.0))
            self.headers["User-Agent"] = random.choice(USER_AGENTS)
            response = requests.get(url, headers=self.headers, timeout=15.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[{self.name}] Error fetching {url}: {e}")
            return None

    def fetch_json(self, url: str) -> Dict | None:
        try:
            time.sleep(random.uniform(1.0, 3.0))
            self.headers["User-Agent"] = random.choice(USER_AGENTS)
            response = requests.get(url, headers=self.headers, timeout=15.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[{self.name}] Error fetching JSON from {url}: {e}")
            return None

    def fetch_html_playwright(self, url: str, wait_for_selector: str = None) -> str | None:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=random.choice(USER_AGENTS))
                page.goto(url, wait_until="networkidle", timeout=30000)
                if wait_for_selector:
                    page.wait_for_selector(wait_for_selector, timeout=10000)
                # Scroll a bit to trigger lazy loading if any
                page.evaluate("window.scrollBy(0, 500)")
                time.sleep(2)  # Wait for extra rendering
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            print(f"[{self.name}] Playwright Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def scrape(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Subclasses must implement scrape()")
