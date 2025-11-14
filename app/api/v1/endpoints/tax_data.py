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
    - **document**: Documento de identificación fiscal (NIT, Cédula de Ciudadanía, etc.)
    - **bank_account**: Número de cuenta bancaria donde recibir pagos
    - **tax_regime**: Régimen fiscal del usuario. Ejemplos: 'Simplificado', 'Común', 'Gran Contribuyente', etc.
    
    **Comportamiento:**
    - Crea un registro de datos fiscales asociado al usuario autenticado
    - Calcula automáticamente las retenciones basándose en el régimen fiscal seleccionado
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
            document=tax_data_obj.document,
            bank_account=tax_data_obj.bank_account,
            tax_regime=tax_data_obj.tax_regime,
            withholdings=tax_data_obj.withholdings
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
    
    **Respuesta:**
    - Documento de identificación fiscal
    - Número de cuenta bancaria
    - Régimen fiscal actual
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
        document=tax_data.document,
        bank_account=tax_data.bank_account,
        tax_regime=tax_data.tax_regime,
        withholdings=tax_data.withholdings
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
    - **document**: Nuevo documento de identificación fiscal
    - **bank_account**: Nuevo número de cuenta bancaria
    - **tax_regime**: Nuevo régimen fiscal
    
    **Comportamiento:**
    - Solo actualiza los campos que se proporcionan en la solicitud
    - Si se actualiza el `tax_regime`, las retenciones se recalculan automáticamente
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
            document=tax_data_obj.document,
            bank_account=tax_data_obj.bank_account,
            tax_regime=tax_data_obj.tax_regime,
            withholdings=tax_data_obj.withholdings
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

