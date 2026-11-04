from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from .database import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

class ChatMessage(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    room_name = Column(String)
    sender_name = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=lambda : datetime.now(timezone.utc))