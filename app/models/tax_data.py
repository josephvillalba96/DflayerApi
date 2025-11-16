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


class DocumentType(str, enum.Enum):
    """Enum for document types (HU005)"""
    NIT = "nit"  # Número de Identificación Tributaria
    CC = "cc"  # Cédula de Ciudadanía
    CE = "ce"  # Cédula de Extranjería
    PASAPORTE = "pasaporte"
    OTRO = "otro"


class TaxDataVerificationStatus(str, enum.Enum):
    """Enum for tax data verification status (HU005)"""
    PENDING = "pending"  # Pendiente validación
    VERIFIED = "verified"  # Validado
    REJECTED = "rejected"  # Rechazado


class TaxData(Base):
    """User tax data model (FISCAL_DATA)"""
    __tablename__ = "tax_data"  # fiscal_data in spec

    tax_data_id = Column(Integer, primary_key=True, index=True)  # fiscal_id in spec
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    
    # HU005: Tipo de documento y número
    document_type = Column(SQLEnum(DocumentType), nullable=True)  # Tipo de documento
    tax_identification_number = Column(String(50), nullable=True)  # Número de documento/NIT
    
    # HU005: Régimen tributario
    tax_regime = Column(SQLEnum(TaxRegime), nullable=True)
    
    # HU005: Upload de RUT (PDF/imagen) - URL del archivo subido a S3
    rut_document_url = Column(String(500), nullable=True)
    
    # HU005: Datos bancarios
    bank_name = Column(String(100), nullable=True)  # Nombre del banco
    bank_account_type = Column(SQLEnum(BankAccountType), nullable=True)  # Tipo de cuenta
    bank_account_number = Column(String(100), nullable=True)  # Número de cuenta
    bank_account_holder = Column(String(200), nullable=True)  # Titular de la cuenta
    
    # HU005: Estado de validación
    verification_status = Column(SQLEnum(TaxDataVerificationStatus), default=TaxDataVerificationStatus.PENDING)
    verified_at = Column(Date, nullable=True)  # Fecha de verificación/rechazo
    rejection_reason = Column(String(500), nullable=True)  # Motivo de rechazo (si aplica)
    
    # Campos adicionales
    is_iva_responsible = Column(Boolean, default=False)
    withholding_percentage = Column(Float, default=0.0)  # Porcentaje de retención calculado
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Legacy fields (kept for compatibility)
    document = Column(String(50), nullable=True)  # Legacy - use tax_identification_number
    verified = Column(Boolean, default=False)  # Legacy - use verification_status instead

    # 1:1 relationship with User
    user = relationship("User", back_populates="tax_data", uselist=False)

