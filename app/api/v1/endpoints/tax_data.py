"""
Tax Data Endpoints (HU005)
Handles tax data management for authenticated users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.base import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.tax_data_service import TaxDataService
from app.schemas.tax_data import (
    TaxDataCreateRequest,
    TaxDataUpdateRequest,
    TaxDataResponse,
    TaxDataHistoryResponse
)

router = APIRouter()


@router.post(
    "",
    response_model=TaxDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear datos fiscales",
    description="""
    **Creación de Datos Fiscales (HU005)**
    
    Permite al usuario autenticado crear su información fiscal para habilitar pagos y transacciones monetarias.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros requeridos:**
    - **document_type**: Tipo de documento (NIT, CC, CE, PASAPORTE, OTRO)
    - **tax_identification_number**: Número de documento/NIT
    - **tax_regime**: Régimen tributario (simplificado, común, gran_contribuyente)
    - **bank_name**: Nombre del banco
    - **bank_account_type**: Tipo de cuenta (ahorros, corriente)
    - **bank_account_number**: Número de cuenta bancaria
    
    **Parámetros opcionales:**
    - **rut_document_url**: URL del RUT (PDF/imagen) subido a S3
      - Primero sube el archivo usando: **POST /api/v1/files/upload**
      - Usa la URL retornada en este campo
    - **bank_account_holder**: Titular de la cuenta (opcional)
    
    **Flujo de trabajo para RUT:**
    1. Sube el RUT usando: `POST /api/v1/files/upload` con `s3_key: "tax_documents/rut_user_{user_id}.pdf"`
    2. Obtén la URL del archivo desde la respuesta
    3. Usa esa URL en `rut_document_url` al crear los datos fiscales
    
    **Comportamiento:**
    - Crea un registro de datos fiscales asociado al usuario autenticado
    - Calcula automáticamente las retenciones basándose en el régimen fiscal seleccionado
    - Estado inicial: **PENDING** (pendiente validación)
    - Los datos fiscales son necesarios para procesar pagos y generar facturas
    
    **Nota:** Solo se permite un registro de datos fiscales por usuario. Para actualizar, use el endpoint PUT.
    """,
    response_description="Datos fiscales creados con las retenciones calculadas automáticamente"
)
async def create_tax_data(
    tax_data: TaxDataCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tax_service = TaxDataService(db)
    
    try:
        tax_data_obj = tax_service.create_tax_data(current_user.user_id, tax_data)
        
        return TaxDataResponse(
            tax_data_id=tax_data_obj.tax_data_id,
            document_type=tax_data_obj.document_type.value if tax_data_obj.document_type else None,
            tax_identification_number=tax_data_obj.tax_identification_number,
            tax_regime=tax_data_obj.tax_regime.value if tax_data_obj.tax_regime else None,
            rut_document_url=tax_data_obj.rut_document_url,
            bank_name=tax_data_obj.bank_name,
            bank_account_type=tax_data_obj.bank_account_type.value if tax_data_obj.bank_account_type else None,
            bank_account_number=tax_data_obj.bank_account_number,
            bank_account_holder=tax_data_obj.bank_account_holder,
            verification_status=tax_data_obj.verification_status.value if tax_data_obj.verification_status else "pending",
            verified_at=tax_data_obj.verified_at,
            rejection_reason=tax_data_obj.rejection_reason,
            withholding_percentage=tax_data_obj.withholding_percentage,
            is_iva_responsible=tax_data_obj.is_iva_responsible,
            created_at=tax_data_obj.created_at,
            updated_at=tax_data_obj.updated_at,
            # Legacy fields
            document=tax_data_obj.document,
            bank_account=tax_data_obj.bank_account,
            withholdings=tax_data_obj.withholding_percentage,
            verified=(tax_data_obj.verification_status.value == "verified" if tax_data_obj.verification_status else False)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=TaxDataResponse,
    summary="Obtener datos fiscales",
    description="""
    **Consulta de Datos Fiscales (HU005)**
    
    Obtiene la información fiscal del usuario autenticado.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Respuesta incluye:**
    - Tipo y número de documento/NIT
    - Régimen tributario
    - URL del RUT subido (si existe)
    - Datos bancarios completos (banco, tipo de cuenta, número, titular)
    - Estado de validación (pending, verified, rejected)
    - Fecha de verificación y motivo de rechazo (si aplica)
    - Porcentaje de retenciones calculado automáticamente
    
    **Errores:**
    - Si el usuario no ha creado datos fiscales, retorna 404
    """,
    response_description="Datos fiscales del usuario autenticado"
)
async def get_tax_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tax_service = TaxDataService(db)
    
    tax_data = tax_service.get_tax_data(current_user.user_id)
    
    if not tax_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax data not found. Please create tax data first."
        )
    
    return TaxDataResponse(
        tax_data_id=tax_data.tax_data_id,
        document_type=tax_data.document_type.value if tax_data.document_type else None,
        tax_identification_number=tax_data.tax_identification_number,
        tax_regime=tax_data.tax_regime.value if tax_data.tax_regime else None,
        rut_document_url=tax_data.rut_document_url,
        bank_name=tax_data.bank_name,
        bank_account_type=tax_data.bank_account_type.value if tax_data.bank_account_type else None,
        bank_account_number=tax_data.bank_account_number,
        bank_account_holder=tax_data.bank_account_holder,
        verification_status=tax_data.verification_status.value if tax_data.verification_status else "pending",
        verified_at=tax_data.verified_at,
        rejection_reason=tax_data.rejection_reason,
        withholding_percentage=tax_data.withholding_percentage,
        is_iva_responsible=tax_data.is_iva_responsible,
        created_at=tax_data.created_at,
        updated_at=tax_data.updated_at,
        # Legacy fields
        document=tax_data.document,
        bank_account=tax_data.bank_account,
        withholdings=tax_data.withholding_percentage,
        verified=(tax_data.verification_status.value == "verified" if tax_data.verification_status else False)
    )


@router.put(
    "",
    response_model=TaxDataResponse,
    summary="Actualizar datos fiscales",
    description="""
    **Actualización de Datos Fiscales (HU005)**
    
    Permite actualizar la información fiscal del usuario autenticado.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Parámetros opcionales (solo se actualizan los campos proporcionados):**
    - **document_type**: Tipo de documento
    - **tax_identification_number**: Número de documento/NIT
    - **tax_regime**: Régimen tributario
    - **rut_document_url**: URL del RUT subido a S3 (obtenida de /api/v1/files/upload)
    - **bank_name**: Nombre del banco
    - **bank_account_type**: Tipo de cuenta bancaria
    - **bank_account_number**: Número de cuenta bancaria
    - **bank_account_holder**: Titular de la cuenta
    
    **Comportamiento:**
    - Solo actualiza los campos que se proporcionan en la solicitud
    - Si se actualiza el `tax_regime`, las retenciones se recalculan automáticamente
    - Si se actualiza cualquier campo, el estado vuelve a **PENDING** (requiere revalidación)
    - Si el usuario no tiene datos fiscales, debe usar el endpoint POST primero
    
    **Nota:** Los cambios en los datos fiscales pueden afectar los cálculos de retenciones en futuras transacciones.
    """,
    response_description="Datos fiscales actualizados con retenciones recalculadas si corresponde"
)
async def update_tax_data(
    tax_data: TaxDataUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tax_service = TaxDataService(db)
    
    try:
        tax_data_obj = tax_service.update_tax_data(current_user.user_id, tax_data)
        
        return TaxDataResponse(
            tax_data_id=tax_data_obj.tax_data_id,
            document_type=tax_data_obj.document_type.value if tax_data_obj.document_type else None,
            tax_identification_number=tax_data_obj.tax_identification_number,
            tax_regime=tax_data_obj.tax_regime.value if tax_data_obj.tax_regime else None,
            rut_document_url=tax_data_obj.rut_document_url,
            bank_name=tax_data_obj.bank_name,
            bank_account_type=tax_data_obj.bank_account_type.value if tax_data_obj.bank_account_type else None,
            bank_account_number=tax_data_obj.bank_account_number,
            bank_account_holder=tax_data_obj.bank_account_holder,
            verification_status=tax_data_obj.verification_status.value if tax_data_obj.verification_status else "pending",
            verified_at=tax_data_obj.verified_at,
            rejection_reason=tax_data_obj.rejection_reason,
            withholding_percentage=tax_data_obj.withholding_percentage,
            is_iva_responsible=tax_data_obj.is_iva_responsible,
            created_at=tax_data_obj.created_at,
            updated_at=tax_data_obj.updated_at,
            # Legacy fields
            document=tax_data_obj.document,
            bank_account=tax_data_obj.bank_account,
            withholdings=tax_data_obj.withholding_percentage,
            verified=(tax_data_obj.verification_status.value == "verified" if tax_data_obj.verification_status else False)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/history",
    response_model=List[TaxDataHistoryResponse],
    summary="Obtener historial de datos fiscales",
    description="""
    **Historial de Datos Fiscales (HU005)**
    
    Obtiene el historial de cambios en los datos fiscales del usuario autenticado.
    
    **Autenticación requerida:**
    - Requiere un token JWT válido en el header `Authorization: Bearer <token>`
    
    **Respuesta:**
    - Lista de registros históricos de datos fiscales
    - Cada registro incluye los valores en ese momento y las fechas de creación/actualización
    
    **Nota:** Actualmente retorna el registro actual. El historial completo requiere la implementación de una tabla de auditoría.
    
    **Uso típico:**
    - Auditoría de cambios en información fiscal
    - Verificación de datos para reportes fiscales
    - Trazabilidad de modificaciones
    """,
    response_description="Lista del historial de datos fiscales del usuario"
)
async def get_tax_data_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tax_service = TaxDataService(db)
    
    history = tax_service.get_tax_data_history(current_user.user_id)
    
    return [
        TaxDataHistoryResponse(
            tax_data_id=item.tax_data_id,
            document=item.document,
            bank_account=item.bank_account,
            tax_regime=item.tax_regime,
            withholdings=item.withholdings,
            created_at=datetime.utcnow(),  # TODO: Add created_at to model
            updated_at=None  # TODO: Add updated_at to model
        )
        for item in history
    ]

