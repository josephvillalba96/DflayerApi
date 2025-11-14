"""
Tax Data Model
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class TaxData(Base):
    """User tax data model"""
    __tablename__ = "tax_data"

    tax_data_id = Column(Integer, primary_key=True, index=True)
    document = Column(String(50), nullable=False)
    bank_account = Column(String(100), nullable=True)
    tax_regime = Column(String(100), nullable=True)
    withholdings = Column(Float, default=0.0)

    # 1:1 relationship with User
    user = relationship("User", back_populates="tax_data", uselist=False)

