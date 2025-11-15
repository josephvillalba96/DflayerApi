"""
Tax Record Model (TAX_RECORDS)
"""
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class TaxType(str, enum.Enum):
    """Enum for tax types"""
    IVA = "iva"
    RETEFUENTE = "retefuente"
    ICA = "ica"


class TaxRecord(Base):
    """Tax record model (TAX_RECORDS)"""
    __tablename__ = "tax_records"

    tax_record_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.transaction_id"), nullable=False)
    tax_period = Column(Date, nullable=False)  # mes/año
    base_amount = Column(Float, nullable=False)  # DECIMAL - monto base
    iva_amount = Column(Float, nullable=False)  # DECIMAL - 19%
    withholding_amount = Column(Float, default=0.0)  # DECIMAL
    net_amount = Column(Float, nullable=False)  # DECIMAL
    tax_type = Column(SQLEnum(TaxType), nullable=False)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tax_records")
    transaction = relationship("Transaction", back_populates="tax_records")

