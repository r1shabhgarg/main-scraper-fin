from services.smart_layer import process_smart_layer
from datetime import datetime

def parse_date_safely(date_val):
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, str):
        try:
            date_val = date_val.replace("Z", "+00:00")
            return datetime.fromisoformat(date_val)
        except ValueError:
            return None
    return None

def is_in_india_or_online(location: str) -> bool:
    if not location:
        return True
        
    loc = location.lower()
    if any(word in loc for word in ["online", "virtual", "remote", "anywhere", "web", "india"]):
        return True
        
    foreign = [" usa", " usa ", "uk", "uk ", "canada", "london", "new york", "australia", "europe", "germany", "france", "singapore"]
    if any(word in loc for word in foreign):
        return False
        
    return True

def normalize_event(raw_event: dict) -> dict | None:
    # Ensure URL is clean
    link = str(raw_event.get("link", "")).strip()
    raw_event["link"] = link
    
    # Parse dates if they are strings
    raw_event["event_date"] = parse_date_safely(raw_event.get("event_date"))
    raw_event["deadline"] = parse_date_safely(raw_event.get("deadline"))
            
    # Apply smart layer
    normalized_event = process_smart_layer(raw_event)
    
    if not is_in_india_or_online(normalized_event.get("location")):
        return None
        
    return normalized_event
