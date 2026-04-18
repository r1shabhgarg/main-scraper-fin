import re
import requests
import webbrowser
from datetime import datetime, timedelta
import urllib.parse
from typing import Optional, Dict, Any

class JarvisController:
    """
    Jarvis Integration Layer Controller.
    Responsible for parsing natural language, interfacing with the backend API,
    generating responses, and dynamically triggering the Frontend UI.
    """
    
    def __init__(self, api_base="http://127.0.0.1:8000/api", ui_base="https://your-domain.com/events"):
        self.api_base = api_base
        self.ui_base = ui_base
        self.cache = {}
        
        # Normalization map
        self.category_map = {
            "quiz": "quiz",
            "quizzes": "quiz",
            "test": "quiz",
            "competition": "competition",
            "competitions": "competition",
            "contest": "competition",
            "contests": "competition",
            "workshop": "workshop",
            "workshops": "workshop",
            "hackathon": "hackathon",
            "hackathons": "hackathon"
        }
        
        self.stop_words = {"show", "me", "find", "some", "the", "in", "for", "events", "live", "about", "are", "there", "any"}
        self.date_words = {"this", "next", "month", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"}

    def open_url(self, url: str):
        """Opens the UI in the browser or webview."""
        print(f"\n[JARVIS SYSTEM] Executing: Opening UI Browser -> {url}")
        webbrowser.open(url)

    def _extract_category(self, text: str) -> Optional[str]:
        words = text.lower().replace(",", "").replace(".", "").split()
        for w in words:
            if w in self.category_map:
                return self.category_map[w]
        return None
        
    def _is_category_word(self, word: str) -> bool:
        return word in self.category_map

    def _extract_date(self, text: str) -> Optional[str]:
        text = text.lower()
        now = datetime.now()
        
        if "this month" in text:
            return now.strftime("%Y-%m")
        if "next month" in text:
            next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
            return next_month.strftime("%Y-%m")
            
        # Regex for Month YYYY e.g. "April 2026"
        match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', text)
        if match:
            month_str = match.group(1)
            year_str = match.group(2)
            month_date = datetime.strptime(month_str, "%B")
            return f"{year_str}-{month_date.month:02d}"
            
        return None

    def _detect_intent(self, command: str) -> Dict[str, Any]:
        """Detect intent from natural language command."""
        text_lower = command.lower()
        
        # Clean punctuation
        clean_text = re.sub(r'[^\w\s]', '', text_lower)
        
        # 1. Open Intent
        if text_lower.startswith("open ") or text_lower.startswith("go to "):
            return {
                "type": "open",
                "category": self._extract_category(text_lower)
            }
            
        # 2. Extract structured entities for query intent
        category = self._extract_category(text_lower)
        date_val = self._extract_date(text_lower)
        
        # 3. Extract Keyword Intent (words that are not stop words, categories, or date tokens)
        words = clean_text.split()
        keyword_candidate = []
        for w in words:
            if w not in self.stop_words and not self._is_category_word(w) and w not in self.date_words and not w.isdigit():
                keyword_candidate.append(w)
                
        keyword = " ".join(keyword_candidate) if keyword_candidate else None
        
        return {
            "type": "query",
            "category": category,
            "date": date_val,
            "keyword": keyword
        }

    def _call_api(self, query_params: Dict[str, str]):
        """Call the backend API with simple cache."""
        url = f"{self.api_base}/events"
        if query_params:
            url += "?" + urllib.parse.urlencode(query_params)
            
        if url in self.cache:
            return self.cache[url]
            
        try:
            resp = requests.get(url, timeout=2.0) # fast fail
            if resp.status_code == 200:
                data = resp.json()
                self.cache[url] = data
                return data
        except requests.exceptions.RequestException as e:
            print(f"[JARVIS SYSTEM] API request failed: {e}")
        return []

    def _generate_nl_response(self, events, intent_data) -> str:
        """Format the output for Jarvis to speak."""
        if not events:
            return "No events found right now, try another category or search term."
            
        top_events = events[:5]
        
        context_str = "events"
        if intent_data.get('category'): context_str = intent_data['category'] + "s"
        if intent_data.get('keyword'): context_str = f"{intent_data['keyword']} {context_str}"
        
        response = f"I found {len(top_events)} {context_str} for you.\n"
        
        for i, e in enumerate(top_events, 1):
            title = e.get("title", "Unknown Event")
            date = e.get("date", "TBA")
            link = e.get("link", "#")
            response += f"{i}. {title} | Date: {date} | {link}\n"
            
        response += "\nI've opened the results on your screen."
        return response

    def handle_command(self, command: str) -> str:
        """Main entrypoint for processing Jarvis commands."""
        print(f"\n==============================================")
        print(f"[JARVIS RECOGNIZED]: \"{command}\"")
        
        intent = self._detect_intent(command)
        
        # Route logic based on intent type
        if intent["type"] == "open":
            category = intent["category"]
            if category:
                url = f"{self.ui_base}?category={category}"
                response_msg = f"Opening the {category} dashboard."
            else:
                url = self.ui_base
                response_msg = "Opening the main events dashboard."
                
            self.open_url(url)
            return response_msg
            
        elif intent["type"] == "query":
            # Build API params and UI params
            api_params = {}
            ui_params = {}
            
            if intent["category"]:
                api_params["category"] = intent["category"]
                ui_params["category"] = intent["category"]
            if intent["date"]:
                api_params["date"] = intent["date"]
            if intent["keyword"]:
                api_params["keyword"] = intent["keyword"]
                ui_params["keyword"] = intent["keyword"]
                
            # Execute API call
            events = self._call_api(api_params)
            
            # Formulate voice/text response
            response_msg = self._generate_nl_response(events, intent)
            
            # Execute UI navigation
            ui_url = self.ui_base
            if ui_params:
                ui_url += "?" + urllib.parse.urlencode(ui_params)
            self.open_url(ui_url)
            
            return response_msg

# --- Example Usage --- #
if __name__ == "__main__":
    jarvis = JarvisController()
    
    # Test Scenario 1: General Events
    print(jarvis.handle_command("Show me live events"))
    
    # Test Scenario 2: Keyword + Category
    print(jarvis.handle_command("Find some AI workshops"))
    
    # Test Scenario 3: Date
    print(jarvis.handle_command("Show me hackathons in April 2026"))
    
    # Test Scenario 4: Open Command
    print(jarvis.handle_command("Open quizzes"))
