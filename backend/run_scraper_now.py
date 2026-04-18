import asyncio
from scheduler import fetch_and_store_events

if __name__ == "__main__":
    asyncio.run(fetch_and_store_events())
