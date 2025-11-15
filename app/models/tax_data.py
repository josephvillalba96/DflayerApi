"""
Tax Data Model (FISCAL_DATA)
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class TaxRegime(str, enum.Enum):
    """Enum for tax regimes"""
    SIMPLIFICADO = "simplificado"
    COMUN = "comun"
    GRAN_CONTRIBUYENTE = "gran_contribuyente"


class BankAccountType(str, enum.Enum):
    """Enum for bank account types"""
    AHORROS = "ahorros"
    CORRIENTE = "corriente"


class TaxData(Base):
    """User tax data model (FISCAL_DATA)"""
    __tablename__ = "tax_data"  # fiscal_data in spec

    tax_data_id = Column(Integer, primary_key=True, index=True)  # fiscal_id in spec
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    tax_regime = Column(SQLEnum(TaxRegime), nullable=True)
    rut_document_url = Column(String(500), nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_account_type = Column(SQLEnum(BankAccountType), nullable=True)
    bank_account_number = Column(String(100), nullable=True)  # bank_account in legacy
    bank_account_holder = Column(String(200), nullable=True)
    tax_identification_number = Column(String(50), nullable=True)
    is_iva_responsible = Column(Boolean, default=False)
    withholding_percentage = Column(Float, default=0.0)  # withholdings in legacy
    verified = Column(Boolean, default=False)
    verified_at = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    document = Column(String(50), nullable=True)  # Legacy - use tax_identification_number

    # 1:1 relationship with User
    user = relationship("User", back_populates="tax_data", uselist=False)

