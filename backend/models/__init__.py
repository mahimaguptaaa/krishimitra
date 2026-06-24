import uuid
from sqlalchemy import Column, String, DateTime, Text, Float, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name          = Column(String(255), nullable=False)
    email         = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    language      = Column(String(5), default="hi")
    state         = Column(String(100))
    crops         = Column(JSON, default=list)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

class Chat(Base):
    __tablename__ = "chats"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title      = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id    = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"))
    role       = Column(String(15))
    content    = Column(Text, nullable=False)
    agent_used = Column(String(100))
    sources    = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    filename    = Column(String(500), nullable=False)
    file_path   = Column(Text, nullable=False)
    status      = Column(String(20), default="pending")
    crop_tag    = Column(String(100))
    chunk_count = Column(Integer)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"
    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    image_path   = Column(Text, nullable=False)
    disease_name = Column(String(255))
    confidence   = Column(Float)
    top_k        = Column(JSON)
    llm_report   = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    crops            = Column(JSON, default=list)
    location         = Column(String(200))
    land_area_acres  = Column(Float)
    soil_type        = Column(String(100))
    irrigation_type  = Column(String(100))
    language         = Column(String(10), default="hi")
    updated_at       = Column(DateTime(timezone=True), server_default=func.now())

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    agent_name  = Column(String(100))
    input_text  = Column(Text)
    output_text = Column(Text)
    latency_ms  = Column(Integer)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

class WeatherCache(Base):
    __tablename__ = "weather_cache"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city       = Column(String(100))
    data       = Column(JSON)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
