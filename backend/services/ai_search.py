import os
import json
import asyncio
import httpx
from duckduckgo_search import DDGS
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from db import crud
import schemas

# Initialize Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

generation_config = genai.types.GenerationConfig(
    temperature=0.2,
    response_mime_type="application/json",
)

try:
    model = genai.GenerativeModel("gemini-2.5-flash", generation_config=generation_config)
except Exception:
    model = None

async def perform_serper_search(query: str):
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return []
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 5})
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=payload, timeout=10.0)
            data = response.json()
            organic = data.get("organic", [])
            return [{"title": item.get("title", ""), "snippet": item.get("snippet", ""), "link": item.get("link", ""), "source": "Serper"} for item in organic[:5]]
    except Exception as e:
        print(f"Serper error: {e}")
        return []

def perform_ddg_search(query: str):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            return [{"title": item.get("title", ""), "snippet": item.get("body", ""), "link": item.get("href", ""), "source": "DuckDuckGo"} for item in results]
    except Exception as e:
        print(f"DDG error: {e}")
        return []

async def aggregate_search(db: AsyncSession, query: str) -> schemas.SearchResponse:
    internal_events = await crud.get_events(db=db, skip=0, limit=10)
    internal_data = [{"title": e.title, "description": e.summary, "link": e.link, "source": "Internal API"} for e in internal_events if e.title]

    loop = asyncio.get_event_loop()
    ddg_task = loop.run_in_executor(None, perform_ddg_search, query)
    serper_task = perform_serper_search(query)
    
    ddg_results, serper_results = await asyncio.gather(ddg_task, serper_task)

    raw_context = {
        "user_query": query,
        "internal_api_results": internal_data,
        "duckduckgo_results": ddg_results,
        "serper_results": serper_results
    }
    
    context_str = json.dumps(raw_context, ensure_ascii=False)

    if not os.environ.get("GEMINI_API_KEY"):
        return schemas.SearchResponse(query=query, results=[
            schemas.SearchItem(
                title="Google Gemini API Key Missing",
                description="The AI Search Agent requires a valid GEMINI_API_KEY in your .env file to process the results.",
                location="System",
                date="Action Required",
                link="https://aistudio.google.com/",
                source="System"
            )
        ])

    prompt = f"""
    You are an advanced AI search agent designed to provide accurate, rich, and real-time results by aggregating multiple data sources.
    Your goal is to answer user queries with high-quality, structured, and relevant results.
    
    DATA SOURCES PROVIDED:
    {context_str}
    
    RULES:
    - Never rely on a single source. Combine them intelligently.
    - Remove duplicates. Prioritize official pages and trusted platforms.
    - If there are no results, suggest alternatives.
    - You MUST return a JSON object with this exact schema:
    {{
      "query": "<user_query>",
      "results": [
        {{
          "title": "Hackathon Name",
          "description": "Short summary",
          "location": "City/Online",
          "date": "Event date",
          "link": "URL",
          "source": "API / DuckDuckGo / Serper"
        }}
      ]
    }}
    """
    
    if not model:
        return schemas.SearchResponse(query=query, results=[])

    try:
        response = await model.generate_content_async(prompt)
        result_json = json.loads(response.text)
        
        items = []
        for r in result_json.get("results", []):
            items.append(schemas.SearchItem(**r))
            
        return schemas.SearchResponse(query=result_json.get("query", query), results=items)
    except Exception as e:
        print(f"LLM error: {e}")
        return schemas.SearchResponse(query=query, results=[
            schemas.SearchItem(
                title="Google Gemini API Error",
                description=f"The Gemini API rejected the request. Exact error: {str(e)}",
                location="System",
                date="Action Required",
                link="https://aistudio.google.com/",
                source="System Error"
            )
        ])
