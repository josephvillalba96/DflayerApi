"""
Bono Image Model (BONO_IMAGES)
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class BonoImage(Base):
    """Bono images model (BONO_IMAGES)"""
    __tablename__ = "bono_images"

    image_id = Column(Integer, primary_key=True, index=True)
    bono_id = Column(Integer, ForeignKey("bonos.bono_id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(Date, default=datetime.utcnow)

    # Relationship
    bono = relationship("Bono", back_populates="images")

