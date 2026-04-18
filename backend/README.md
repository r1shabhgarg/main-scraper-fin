# Events Aggregation Engine Backend

A scalable backend "Student Events Engine" that continuously collects and serves opportunities (hackathons, competitions, workshops, fests) for a college platform.

## Features
- **Centralized API:** Provides JSON responses optimized for frontend consumption.
- **Background Scraping:** Pre-configured APScheduler to scrape devpost, unstop, and eventbrite every 6 hours.
- **Smart Layer:** AI-driven tagging, beginner-friendly flags, free/paid inference, and summary generation.
- **Asynchronous Stack:** Built on FastAPI and SQLAlchemy async with asyncpg.

## Prerequisites
- Python 3.10+
- PostgreSQL server running locally or via Supabase.

## Setup Instructions

1. **Clone and Setup Virtual Environment:**
   Run `python -m venv venv`
   Activate it:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

2. **Install Dependencies:**
   `pip install -r requirements.txt`

3. **Database Configuration:**
   Create a `.env` file in the root directory with your PostgreSQL connection string:
   `DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/events_db`

4. **Run the Application:**
   Start the FastAPI server (which also starts the background scheduler):
   `uvicorn main:app --reload`
   
   The database tables will be created automatically on startup.

## API Endpoints

- `GET /health` : Health check
- `GET /events/` : Returns paginated events.
  - Query Params: `skip`, `limit`, `type`, `tag`, `sort` (use `sort=date` for ascending deadline order)
- `GET /events/recommended` : Returns beginner-friendly, free events.
- `GET /events/ending-soon` : Returns events with deadlines within 3 days.

All interactive documentation is available at `http://localhost:8000/docs` once the server is running.
