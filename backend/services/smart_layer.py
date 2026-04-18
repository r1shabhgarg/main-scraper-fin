import re

def classify_event_type(title: str, description: str, current_type: str) -> str:
    content = (title + " " + description).lower()
    
    if any(w in content for w in ["hackathon", "hack"]): return "hackathon"
    if any(w in content for w in ["workshop", "masterclass", "bootcamp"]): return "workshop"
    if any(w in content for w in ["quiz", "trivia"]): return "quiz"
    if any(w in content for w in ["conference", "summit", "symposium", "expo"]): return "conference"
    if any(w in content for w in ["cultural", "dance", "music", "art"]): return "cultural"
    if any(w in content for w in ["fest", "festival"]): return "fest"
    if any(w in content for w in ["competition", "challenge", "contest"]): return "competition"
    
    # Fallback to current type if valid, otherwise competition
    valid_types = ["competition", "hackathon", "workshop", "quiz", "conference", "cultural", "fest"]
    if current_type and current_type.lower() in valid_types:
        return current_type.lower()
    return "competition"

def is_beginner_friendly(title: str, description: str, tags: list[str]) -> bool:
    content = (title + " " + description + " " + " ".join(tags)).lower()
    keywords = ["beginner", "novice", "101", "intro", "student", "no experience", "first time"]
    return any(kw in content for kw in keywords)

def refine_tags(title: str, description: str, current_tags: list[str]) -> list[str]:
    content = (title + " " + description).lower()
    new_tags = set(current_tags)
    
    tag_map = {
        "ai": ["ai", "artificial intelligence", "machine learning", "ml", "nlp"],
        "web": ["web", "frontend", "backend", "react", "html", "fullstack"],
        "music": ["music", "audio", "sound", "songs", "singing"],
        "business": ["business", "pitch", "startup", "entrepreneur", "marketing", "finance"],
        "coding": ["coding", "programming", "software", "developer", "hackathon", "cp"]
    }
    
    for tag, keywords in tag_map.items():
        if any(kw in content for kw in keywords):
            new_tags.add(tag)
            
    return list(new_tags)

def extract_key_points(event: dict) -> list[str]:
    points = []
    desc = (event.get("description") or "").lower()
    title = (event.get("title") or "").lower()
    content = title + " " + desc
    location = (event.get("location") or "").lower()
    
    team_match = None
    team_patterns = [
        (r'team of\s*(\d+)', 1),
        (r'(\d+)\s*-\s*\d+\s*members?', 1),
        (r'(\d+)\s*member', 1),
        (r'(\d+)\s*participants?\s*per\s*team', 1),
        (r'solo|individual|single', 0),
    ]
    for pattern, val_idx in team_patterns:
        match = re.search(pattern, content)
        if match:
            if val_idx == 0:
                team_match = "Solo"
            else:
                team_match = f"Team of {match.group(1)}"
            break
    if team_match:
        points.append(team_match)
    
    if "online" in location or "virtual" in location or "anywhere" in location:
        points.append("Online")
    elif location and location != "india" and len(location) > 2:
        points.append("Offline")
    
    prize = event.get("prize")
    if prize and str(prize).lower() not in ["none", "null", "", "free", "0"]:
        if any(w in str(prize).lower() for w in ["prize", "₹", "$", "rs", "cash", " INR"]):
            points.append(f"Prize: {prize}")
    
    if any(w in content for w in ["student", "college", "university", "school"]):
        points.append("For Students")
    
    return points

def generate_summary(event: dict) -> str:
    e_type = event.get("event_type", "event")
    tags = event.get("tags", [])
    desc = event.get("description") or ""
    
    key_points = extract_key_points(event)
    
    desc_clean = desc.strip()
    if len(desc_clean) > 30:
        sentences = [s.strip() for s in desc_clean.split('.') if len(s.strip()) > 5]
        if sentences:
            first_sentence = sentences[0]
            if len(first_sentence) > 120:
                first_sentence = first_sentence[:117] + "..."
            desc_part = first_sentence + "."
        else:
            desc_part = None
    else:
        desc_part = None
    
    summary_parts = []
    
    if key_points:
        summary_parts.append(" • ".join(key_points))
    
    if desc_part:
        summary_parts.append(desc_part)
    
    if not summary_parts:
        tag_str = f" focused on {', '.join(tags[:2])}" if tags else ""
        beginner = "Beginner-friendly " if event.get("is_beginner_friendly") else ""
        summary_parts.append(f"{beginner}{e_type.title()}{tag_str} for students.")
    
    return " | ".join(summary_parts)

def process_smart_layer(event: dict) -> dict:
    title = event.get("title", "")
    desc = event.get("description", "") or ""
    tags = event.get("tags", [])
    
    event["event_type"] = classify_event_type(title, desc, event.get("event_type", ""))
    event["is_beginner_friendly"] = is_beginner_friendly(title, desc, tags)
    event["tags"] = refine_tags(title, desc, tags)
    
    content = (title + " " + desc).lower()
    if any(word in content for word in ["paid", "entry fee", "registration fee", "ticket"]):
        event["is_free"] = False
    else:
        event["is_free"] = True
        
    event["summary"] = generate_summary(event)
    return event
