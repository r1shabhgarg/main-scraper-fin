import asyncio
import os
import json
from services.ai_search import aggregate_search
from db.database import AsyncSessionLocal

async def debug():
    print(f"GEMINI_API_KEY prefix: {os.environ.get('GEMINI_API_KEY', '')[:5]}")
    print(f"SERPER_API_KEY prefix: {os.environ.get('SERPER_API_KEY', '')[:5]}")
    async with AsyncSessionLocal() as db:
        res = await aggregate_search(db, "hackathons in New York")
        print("\n\nFINAL RESULT:")
        print(res.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(debug())
