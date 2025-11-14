"""
Transcoding Job Model
Manages video/audio transcoding jobs and their status
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class TranscodingStatus(str, enum.Enum):
    """Enum for transcoding job status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TranscodingPriority(str, enum.Enum):
    """Enum for transcoding job priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TranscodingJob(Base):
    """Model for managing transcoding jobs"""
    __tablename__ = "transcoding_jobs"

    job_id = Column(Integer, primary_key=True, index=True)
    source_file_id = Column(Integer, ForeignKey("multimedia_files.file_id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("transcoding_profiles.profile_id"), nullable=False)
    
    # Job status and tracking
    status = Column(SQLEnum(TranscodingStatus), default=TranscodingStatus.PENDING)
    priority = Column(SQLEnum(TranscodingPriority), default=TranscodingPriority.NORMAL)
    progress_percentage = Column(Float, default=0.0)  # 0-100
    
    # Processing information
    started_at = Column(Date, nullable=True)
    completed_at = Column(Date, nullable=True)
    estimated_completion = Column(Date, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Output file information
    output_file_id = Column(Integer, ForeignKey("multimedia_files.file_id"), nullable=True)
    output_s3_key = Column(String(500), nullable=True)
    output_s3_url = Column(String(1000), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Worker/processor information
    worker_id = Column(String(100), nullable=True)  # ID of the worker processing this job
    processor_type = Column(String(50), nullable=True)  # ffmpeg, aws_media_convert, etc.
    
    # Metadata
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_file = relationship("MultimediaFile", foreign_keys=[source_file_id], back_populates="transcoding_jobs")
    output_file = relationship("MultimediaFile", foreign_keys=[output_file_id], back_populates="transcoded_from_job")
    profile = relationship("TranscodingProfile", back_populates="jobs")


class TranscodingProfile(Base):
    """Model for transcoding configuration profiles"""
    __tablename__ = "transcoding_profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "1080p_h264", "720p_h264", "480p_h264"
    description = Column(String(255), nullable=True)
    
    # Video settings
    video_codec = Column(String(50), nullable=False)  # h264, h265, vp9, etc.
    video_bitrate = Column(Integer, nullable=True)  # kbps
    video_bitrate_mode = Column(String(20), nullable=True)  # VBR, CBR, ABR
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)  # Frames per second
    keyframe_interval = Column(Integer, nullable=True)  # GOP size
    
    # Audio settings
    audio_codec = Column(String(50), nullable=True)  # aac, mp3, opus, etc.
    audio_bitrate = Column(Integer, nullable=True)  # kbps
    audio_sample_rate = Column(Integer, nullable=True)  # Hz
    audio_channels = Column(Integer, nullable=True)  # 1=mono, 2=stereo
    
    # Container/format
    container_format = Column(String(20), nullable=False)  # mp4, webm, mkv, etc.
    
    # Quality settings
    quality_preset = Column(String(50), nullable=True)  # fast, medium, slow, etc.
    crf = Column(Integer, nullable=True)  # Constant Rate Factor (for quality-based encoding)
    
    # Thumbnail generation
    generate_thumbnail = Column(Boolean, default=True)
    thumbnail_count = Column(Integer, default=1)  # Number of thumbnails to generate
    thumbnail_interval = Column(Integer, nullable=True)  # Seconds between thumbnails
    
    # HLS/DASH streaming support
    enable_hls = Column(Boolean, default=False)
    enable_dash = Column(Boolean, default=False)
    segment_duration = Column(Integer, nullable=True)  # Seconds per segment
    
    # Active status
    active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)
    
    # Relationships
    jobs = relationship("TranscodingJob", back_populates="profile")


class TranscodingQueue(Base):
    """Model for managing transcoding queue"""
    __tablename__ = "transcoding_queue"

    queue_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("transcoding_jobs.job_id"), unique=True, nullable=False)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    queued_at = Column(Date, default=datetime.utcnow)
    started_at = Column(Date, nullable=True)
    
    # Relationship
    job = relationship("TranscodingJob", backref="queue_entry")


class TranscodingLog(Base):
    """Model for transcoding job logs and history"""
    __tablename__ = "transcoding_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("transcoding_jobs.job_id"), nullable=False)
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    log_data = Column(Text, nullable=True)  # JSON string with additional data
    created_at = Column(Date, default=datetime.utcnow)
    
    # Relationship
    job = relationship("TranscodingJob", backref="logs")

