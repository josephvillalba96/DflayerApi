"""
Audio Track Model (AUDIO_TRACKS)
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class AudioTrack(Base):
    """Audio tracks model (AUDIO_TRACKS)"""
    __tablename__ = "audio_tracks"

    audio_id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media_files.media_id"), nullable=True)  # puede ser NULL si es audio original
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=True)  # puede vincular directo
    title = Column(String(200), nullable=True)
    artist = Column(String(200), nullable=True)
    duration_seconds = Column(Float, nullable=True)  # DECIMAL
    storage_path = Column(String(500), nullable=False)
    waveform_data = Column(Text, nullable=True)  # JSON con datos para visualización
    format = Column(String(50), nullable=False)  # mp3, aac, wav
    bitrate = Column(Integer, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    is_original_audio = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)  # cuántas veces se ha usado
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media = relationship("MultimediaFile", back_populates="audio_tracks")
    post = relationship("Content", back_populates="audio_tracks")

