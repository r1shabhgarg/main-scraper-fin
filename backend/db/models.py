from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Uuid
from db.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    event_date = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    location = Column(String, nullable=True)
    link = Column(String, unique=True, nullable=False)
    tags = Column(JSON, default=[])
    prize = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_beginner_friendly = Column(Boolean, default=False)
    is_free = Column(Boolean, default=True)
    summary = Column(String, nullable=True)
