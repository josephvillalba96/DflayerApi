"""
Multimedia File Model
Manages storage of videos, music, images and other multimedia files
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class FileType(str, enum.Enum):
    """Enum for multimedia file types"""
    VIDEO = "video"
    AUDIO = "audio"  # Music, sound
    IMAGE = "image"
    THUMBNAIL = "thumbnail"
    OTHER = "other"


class ProcessingStatus(str, enum.Enum):
    """Enum for file processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class UploadStatus(str, enum.Enum):
    """Enum for upload status"""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    FAILED = "failed"


class MediaType(str, enum.Enum):
    """Enum for media types (MEDIA_FILES)"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"


class MultimediaFile(Base):
    """Media files model (MEDIA_FILES)"""
    __tablename__ = "media_files"  # multimedia_files en legacy

    media_id = Column(Integer, primary_key=True, index=True)  # file_id en legacy
    post_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)  # content_id en legacy
    media_type = Column(SQLEnum(MediaType), nullable=False)  # file_type en legacy
    original_filename = Column(String(255), nullable=True)
    file_size = Column(BigInteger, nullable=False)  # BIGINT
    mime_type = Column(String(100), nullable=True)
    storage_path = Column(String(500), nullable=False)  # s3_key en legacy
    upload_status = Column(SQLEnum(UploadStatus), default=UploadStatus.UPLOADING)
    duration_seconds = Column(Float, nullable=True)  # DECIMAL - para videos/audio
    width = Column(Integer, nullable=True)  # para imágenes/videos
    height = Column(Integer, nullable=True)
    aspect_ratio = Column(String(20), nullable=True)
    uploaded_at = Column(Date, default=datetime.utcnow)
    created_at = Column(Date, default=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=True)  # Legacy
    file_type = Column(SQLEnum(FileType), nullable=True)  # Legacy
    bucket_name = Column(String(100), nullable=True)  # Legacy
    s3_key = Column(String(500), nullable=True)  # Legacy
    s3_url = Column(String(1000), nullable=True)  # Legacy
    file_name = Column(String(255), nullable=True)  # Legacy
    format = Column(String(50), nullable=True)  # Legacy
    duration = Column(Integer, nullable=True)  # Legacy
    resolution = Column(String(50), nullable=True)  # Legacy
    bitrate = Column(Integer, nullable=True)  # Legacy
    fps = Column(Float, nullable=True)  # Legacy
    sample_rate = Column(Integer, nullable=True)  # Legacy
    channels = Column(Integer, nullable=True)  # Legacy
    processing_status = Column(SQLEnum(ProcessingStatus), nullable=True)  # Legacy
    is_primary = Column(Boolean, default=False)  # Legacy
    is_public = Column(Boolean, default=True)  # Legacy
    cdn_url = Column(String(1000), nullable=True)  # Legacy
    preview_url = Column(String(1000), nullable=True)  # Legacy
    processed_at = Column(Date, nullable=True)  # Legacy
    
    # Relationship with Content (post_id)
    content = relationship("Content", foreign_keys=[post_id], back_populates="media_files")
    
    # Transcoding relationships
    video_transcodes = relationship("VideoTranscode", back_populates="media")
    image_variants = relationship("ImageVariant", back_populates="media")
    audio_tracks = relationship("AudioTrack", back_populates="media")

