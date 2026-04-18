import os
import sys
from pathlib import Path

# Add the backend directory to sys.path so imports work on Vercel
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# These imports are lightweight (no playwright/scraper/AI deps)
from db.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if not exist (wrapped for Vercel stability)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"WARNING: Database init failed (may be normal on cold start): {e}")
    yield

app = FastAPI(
    title="Events Aggregation Engine API",
    description="API for fetching student-relevant events across platforms.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers AFTER sys.path is set
from api.routes import router as events_router
from api.external import router as jarvis_router

app.include_router(events_router)
app.include_router(jarvis_router)

# Try to mount the external_api router if it exists
try:
    from api.external_api import router as ext_api_router
    app.include_router(ext_api_router)
except Exception:
    pass

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/debug")
async def debug_endpoint():
    """Diagnose Vercel deployment issues."""
    from sqlalchemy import text
    
    db_url = os.getenv("DATABASE_URL", "NOT_SET")
    db_status = "Unknown"
    error_msg = None
    
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "Connected"
    except Exception as e:
        db_status = "Failed"
        error_msg = str(e)
        
    return {
        "database_url_configured": db_url != "NOT_SET" and "localhost" not in db_url,
        "database_connection": db_status,
        "error": error_msg,
        "environment": os.getenv("VERCEL_ENV", "local"),
        "python_path": sys.path[:5]
    }
