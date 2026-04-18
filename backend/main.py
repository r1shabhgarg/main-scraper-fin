from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as events_router
from api.external import router as jarvis_router
from scheduler import start_scheduler
from db.database import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start scheduler
    start_scheduler()
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
