from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from datetime import datetime
from database import Base
import enum
from sqlalchemy.sql import func


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String, index=True)
    prompt = Column(String)
    negative_prompt = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobStatusEnum(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)  # UUID
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.PENDING)
    error = Column(Text, nullable=True)
    result_id = Column(Integer, nullable=True)  # FK → Generation.id
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())