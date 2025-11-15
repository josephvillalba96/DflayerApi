"""
Image Variant Model (IMAGE_VARIANTS)
"""
from sqlalchemy import Column, Integer, String, BigInteger, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class VariantType(str, enum.Enum):
    """Enum for image variant types"""
    THUMBNAIL = "thumbnail"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ORIGINAL = "original"


class ImageVariant(Base):
    """Image variants model (IMAGE_VARIANTS)"""
    __tablename__ = "image_variants"

    variant_id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media_files.media_id"), nullable=False)
    variant_type = Column(SQLEnum(VariantType), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # BIGINT
    format = Column(String(50), nullable=False)  # jpg, png, webp
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    media = relationship("MultimediaFile", back_populates="image_variants")

