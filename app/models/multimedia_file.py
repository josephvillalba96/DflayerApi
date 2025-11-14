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


class MultimediaFile(Base):
    """Model for managing multimedia files stored in S3"""
    __tablename__ = "multimedia_files"

    file_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.content_id"), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    
    # S3 storage information
    bucket_name = Column(String(100), nullable=False)  # S3 bucket name
    s3_key = Column(String(500), nullable=False, unique=True, index=True)  # S3 key/path
    s3_url = Column(String(1000), nullable=False)  # Full S3 file URL
    
    # File metadata
    original_name = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=False)  # Processed file name
    format = Column(String(50), nullable=False)  # mp4, mp3, jpg, png, etc.
    size_bytes = Column(BigInteger, nullable=False)  # Size in bytes
    duration = Column(Integer, nullable=True)  # Duration in seconds (for video/audio)
    
    # Technical information (for videos)
    resolution = Column(String(50), nullable=True)  # 1080p, 720p, etc.
    width = Column(Integer, nullable=True)  # Width in pixels
    height = Column(Integer, nullable=True)  # Height in pixels
    bitrate = Column(Integer, nullable=True)  # Bitrate in kbps
    fps = Column(Float, nullable=True)  # Frames per second (for video)
    
    # Technical information (for audio)
    sample_rate = Column(Integer, nullable=True)  # Sample rate in Hz
    channels = Column(Integer, nullable=True)  # Number of channels (mono, stereo, etc.)
    
    # Status and processing
    processing_status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    is_primary = Column(Boolean, default=False)  # If it's the main file of the content
    is_public = Column(Boolean, default=True)  # If it's publicly accessible
    
    # URLs and references
    cdn_url = Column(String(1000), nullable=True)  # CDN URL if used
    preview_url = Column(String(1000), nullable=True)  # Preview/thumbnail URL
    
    # Timestamps
    uploaded_at = Column(Date, default=datetime.utcnow)
    processed_at = Column(Date, nullable=True)
    
    # Relationship with Content
    content = relationship("Content", back_populates="multimedia_files")
    
    # Transcoding relationships
    transcoding_jobs = relationship("TranscodingJob", foreign_keys="TranscodingJob.source_file_id", back_populates="source_file")
    transcoded_from_job = relationship("TranscodingJob", foreign_keys="TranscodingJob.output_file_id", back_populates="output_file", uselist=False)


class FileVersion(Base):
    """Model for managing different versions/qualities of the same file"""
    __tablename__ = "file_versions"

    version_id = Column(Integer, primary_key=True, index=True)
    original_file_id = Column(Integer, ForeignKey("multimedia_files.file_id"), nullable=False)
    quality = Column(String(50), nullable=False)  # original, hd, sd, low, etc.
    resolution = Column(String(50), nullable=True)
    s3_key = Column(String(500), nullable=False, unique=True, index=True)
    s3_url = Column(String(1000), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    format = Column(String(50), nullable=False)
    created_at = Column(Date, default=datetime.utcnow)
    
    # Relationship with original file
    original_file = relationship("MultimediaFile", backref="versions")

