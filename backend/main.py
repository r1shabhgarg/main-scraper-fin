import os
import sys
from pathlib import Path

# Add the current directory to sys.path so imports like 'api', 'db', 'scheduler' work on Vercel
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as events_router
from api.external import router as jarvis_router
from db.database import engine, Base
from contextlib import asynccontextmanager
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if not exist (Wrapped in try-except for Vercel stability)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"CRITICAL: Database initialization failed: {e}")
    
    # Start scheduler removed for Vercel Serverless compatibility
    yield
    # Shutdown logic if any

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

app.include_router(events_router)
app.include_router(jarvis_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/debug")
async def debug_endpoint():
    """
    Helps diagnose Vercel deployment issues by checking env vars and DB status.
    """
    db_url = os.getenv("DATABASE_URL", "NOT_SET")
    db_status = "Unknown"
    error = None
    
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
            db_status = "Connected"
    except Exception as e:
        db_status = "Failed"
        error = str(e)
        
    return {
        "database_url_configured": db_url != "NOT_SET" and "localhost" not in db_url,
        "database_connection": db_status,
        "error": error,
        "environment": os.getenv("VERCEL_ENV", "local")
    }
