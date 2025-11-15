"""
Video Transcode Model (VIDEO_TRANSCODES)
"""
from sqlalchemy import Column, Integer, String, BigInteger, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class ProcessingStatus(str, enum.Enum):
    """Enum for processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoTranscode(Base):
    """Video transcodes model (VIDEO_TRANSCODES)"""
    __tablename__ = "video_transcodes"

    transcode_id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media_files.media_id"), nullable=False)
    resolution = Column(String(50), nullable=False)  # 360p, 480p, 720p, 1080p
    bitrate = Column(Integer, nullable=True)
    codec = Column(String(50), nullable=True)  # h264, h265, vp9
    container_format = Column(String(50), nullable=True)  # mp4, webm
    storage_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # BIGINT
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_started_at = Column(Date, nullable=True)
    processing_completed_at = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    media = relationship("MultimediaFile", back_populates="video_transcodes")

