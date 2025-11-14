"""
Tax Data Schemas (HU005)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class TaxDataCreateRequest(BaseModel):
    """Schema for creating tax data"""
    document: str = Field(..., min_length=5, max_length=50, description="Tax identification document (NIT, CC, etc.)")
    bank_account: str = Field(..., min_length=10, max_length=100, description="Bank account number")
    tax_regime: str = Field(..., max_length=100, description="Tax regime (e.g., 'Simplificado', 'Común', etc.)")
    
    @validator('document')
    def validate_document(cls, v):
        """Validate document format"""
        if not v.replace('-', '').replace('.', '').replace(' ', '').isdigit():
            raise ValueError('Document must contain only numbers, dashes, dots, or spaces')
        return v
    
    @validator('bank_account')
    def validate_bank_account(cls, v):
        """Validate bank account format"""
        if not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Bank account must contain only numbers, dashes, or spaces')
        return v


class TaxDataUpdateRequest(BaseModel):
    """Schema for updating tax data"""
    document: Optional[str] = Field(None, min_length=5, max_length=50)
    bank_account: Optional[str] = Field(None, min_length=10, max_length=100)
    tax_regime: Optional[str] = Field(None, max_length=100)
    
    @validator('document')
    def validate_document(cls, v):
        if v and not v.replace('-', '').replace('.', '').replace(' ', '').isdigit():
            raise ValueError('Document must contain only numbers, dashes, dots, or spaces')
        return v
    
    @validator('bank_account')
    def validate_bank_account(cls, v):
        if v and not v.replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Bank account must contain only numbers, dashes, or spaces')
        return v


class TaxDataResponse(BaseSchema):
    """Schema for tax data response"""
    tax_data_id: int
    document: str
    bank_account: str
    tax_regime: str
    withholdings: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaxDataHistoryResponse(BaseSchema):
    """Schema for tax data history"""
    tax_data_id: int
    document: str
    bank_account: str
    tax_regime: str
    withholdings: float
    created_at: datetime
    updated_at: Optional[datetime] = None


