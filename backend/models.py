from datetime import datetime, timedelta

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    portal = Column(String(32), index=True, nullable=False)
    title = Column(String(512), nullable=False)
    author = Column(String(256), default="")
    date = Column(String(32), default="")
    url = Column(String(1024), unique=True, nullable=False)
    content = Column(Text, default="")
    word_count = Column(Integer, default=0)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    audio_generated = Column(Boolean, default=False)

    audio_files = relationship("AudioFile", back_populates="article", cascade="all, delete-orphan")


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

    article = relationship("Article", back_populates="audio_files")


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, nullable=False, index=True)
    value = Column(Text, default="")
