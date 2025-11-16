"""
Tax Data Schemas (HU005)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema
from app.models.tax_data import DocumentType, TaxRegime, BankAccountType, TaxDataVerificationStatus


class TaxDataCreateRequest(BaseModel):
    """Schema for creating tax data (HU005)"""
    # HU005: Tipo de documento y número
    document_type: DocumentType = Field(..., description="Tipo de documento (NIT, CC, CE, PASAPORTE, OTRO)")
    tax_identification_number: str = Field(..., min_length=5, max_length=50, description="Número de documento/NIT")
    
    # HU005: Régimen tributario
    tax_regime: TaxRegime = Field(..., description="Régimen tributario")
    
    # HU005: Upload de RUT (PDF/imagen) - URL del archivo subido a S3
    rut_document_url: Optional[str] = Field(None, max_length=500, description="URL del RUT subido a S3 (obtenida de /api/v1/files/upload)")
    
    # HU005: Datos bancarios
    bank_name: str = Field(..., min_length=2, max_length=100, description="Nombre del banco")
    bank_account_type: BankAccountType = Field(..., description="Tipo de cuenta bancaria (ahorros, corriente)")
    bank_account_number: str = Field(..., min_length=10, max_length=100, description="Número de cuenta bancaria")
    bank_account_holder: Optional[str] = Field(None, max_length=200, description="Titular de la cuenta (opcional)")
    
    @validator('tax_identification_number')
    def validate_tax_identification_number(cls, v):
        """Validate tax identification number format"""
        if not v.replace('-', '').replace('.', '').replace(' ', '').isdigit():
            raise ValueError('Tax identification number must contain only numbers, dashes, dots, or spaces')
        return v
    
    @validator('bank_account_number')
    def validate_bank_account_number(cls, v):
        """Validate bank account number format"""
        if not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Bank account number must contain only numbers, dashes, or spaces')
        return v


class TaxDataUpdateRequest(BaseModel):
    """Schema for updating tax data (HU005)"""
    # HU005: Tipo de documento y número
    document_type: Optional[DocumentType] = Field(None, description="Tipo de documento")
    tax_identification_number: Optional[str] = Field(None, min_length=5, max_length=50, description="Número de documento/NIT")
    
    # HU005: Régimen tributario
    tax_regime: Optional[TaxRegime] = Field(None, description="Régimen tributario")
    
    # HU005: Upload de RUT (PDF/imagen)
    rut_document_url: Optional[str] = Field(None, max_length=500, description="URL del RUT subido a S3")
    
    # HU005: Datos bancarios
    bank_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombre del banco")
    bank_account_type: Optional[BankAccountType] = Field(None, description="Tipo de cuenta bancaria")
    bank_account_number: Optional[str] = Field(None, min_length=10, max_length=100, description="Número de cuenta bancaria")
    bank_account_holder: Optional[str] = Field(None, max_length=200, description="Titular de la cuenta")
    
    @validator('tax_identification_number')
    def validate_tax_identification_number(cls, v):
        if v and not v.replace('-', '').replace('.', '').replace(' ', '').isdigit():
            raise ValueError('Tax identification number must contain only numbers, dashes, dots, or spaces')
        return v
    
    @validator('bank_account_number')
    def validate_bank_account_number(cls, v):
        if v and not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Bank account number must contain only numbers, dashes, or spaces')
        return v


class TaxDataResponse(BaseSchema):
    """Schema for tax data response (HU005)"""
    tax_data_id: int
    # HU005: Tipo de documento y número
    document_type: Optional[str] = None
    tax_identification_number: Optional[str] = None
    # HU005: Régimen tributario
    tax_regime: Optional[str] = None
    # HU005: Upload de RUT
    rut_document_url: Optional[str] = None
    # HU005: Datos bancarios
    bank_name: Optional[str] = None
    bank_account_type: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_account_holder: Optional[str] = None
    # HU005: Estado de validación
    verification_status: str
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    # Campos adicionales
    withholding_percentage: float
    is_iva_responsible: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Legacy fields (for compatibility)
    document: Optional[str] = None
    bank_account: Optional[str] = None
    withholdings: Optional[float] = None
    verified: Optional[bool] = None


class TaxDataHistoryResponse(BaseSchema):
    """Schema for tax data history"""
    tax_data_id: int
    document: str
    bank_account: str
    tax_regime: str
    withholdings: float
    created_at: datetime
    updated_at: Optional[datetime] = None


