"""
Servicio de Datos Fiscales (HU005)

Este servicio maneja la gestión de información fiscal de los usuarios:
- Creación y actualización de datos fiscales
- Cálculo automático de retenciones basado en régimen fiscal
- Historial de cambios en datos fiscales

Sistema fiscal colombiano:
- Régimen Simplificado: 5% de retención
- Régimen Común: 19% de retención (incluye IVA)
- Gran Contribuyente: 19% de retención
- Autorretenedor: 11% de retención

Historia de Usuario: HU005 (Gestión de Datos Fiscales)
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.tax_data import TaxData, TaxDataVerificationStatus
from app.models.user import User
from app.schemas.tax_data import TaxDataCreateRequest, TaxDataUpdateRequest


class TaxDataService:
    """
    Servicio de Gestión de Datos Fiscales
    
    Proporciona métodos para gestionar la información fiscal de los usuarios,
    incluyendo el cálculo automático de retenciones según el régimen fiscal.
    
    Características:
    - Cálculo automático de retenciones basado en régimen fiscal
    - Soporte para sistema fiscal colombiano
    - Validación de datos fiscales únicos por usuario
    """
    
    # Tasas de retención por régimen fiscal (Sistema fiscal colombiano)
    TAX_REGIME_RATES = {
        "simplificado": 0.05,  # 5% para régimen simplificado
        "común": 0.19,  # 19% para régimen común (incluye IVA)
        "gran_contribuyente": 0.19,  # 19% para gran contribuyente
        "autorretenedor": 0.11,  # 11% para autorretenedor
    }
    
    DEFAULT_WITHHOLDING_RATE = 0.19  # Por defecto 19% (tasa de IVA en Colombia)
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de datos fiscales
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def calculate_withholdings(self, tax_regime: str) -> float:
        """
        Calcula las retenciones automáticas basadas en el régimen fiscal
        
        Busca coincidencias exactas y parciales del nombre del régimen fiscal
        para determinar la tasa de retención correspondiente.
        
        Args:
            tax_regime: Nombre del régimen fiscal (ej: "Simplificado", "Común", etc.)
        
        Returns:
            Porcentaje de retención como decimal (0.0 a 1.0)
            - 0.05 para régimen simplificado (5%)
            - 0.19 para régimen común o gran contribuyente (19%)
            - 0.11 para autorretenedor (11%)
            - 0.19 por defecto si no se encuentra coincidencia
        """
        regime_lower = tax_regime.lower().replace(" ", "_")
        
        # Check exact match first
        if regime_lower in self.TAX_REGIME_RATES:
            return self.TAX_REGIME_RATES[regime_lower]
        
        # Check partial matches
        for regime_key, rate in self.TAX_REGIME_RATES.items():
            if regime_key in regime_lower or regime_lower in regime_key:
                return rate
        
        # Default to 19% (IVA rate)
        return self.DEFAULT_WITHHOLDING_RATE
    
    def create_tax_data(self, user_id: int, tax_data: TaxDataCreateRequest) -> TaxData:
        """
        Crea datos fiscales para un usuario (HU005)
        
        Crea un nuevo registro de datos fiscales y calcula automáticamente
        las retenciones basándose en el régimen fiscal proporcionado.
        
        Args:
            user_id: ID del usuario
            tax_data: Datos fiscales a crear (documento, cuenta bancaria, régimen)
        
        Returns:
            Objeto TaxData creado con las retenciones calculadas
        
        Raises:
            ValueError: Si el usuario no existe o ya tiene datos fiscales registrados
        
        Nota: Solo se permite un registro de datos fiscales por usuario.
        Para actualizar, use el método update_tax_data().
        """
        # Check if user exists
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if user already has tax data
        existing = self.db.query(TaxData).filter(TaxData.tax_data_id == user.tax_data_id).first()
        if existing:
            raise ValueError("User already has tax data. Use update endpoint instead.")
        
        # Calculate withholdings
        withholdings_rate = self.calculate_withholdings(tax_data.tax_regime.value if hasattr(tax_data.tax_regime, 'value') else str(tax_data.tax_regime))
        
        # Create tax data (HU005)
        new_tax_data = TaxData(
            user_id=user_id,
            # HU005: Tipo de documento y número
            document_type=tax_data.document_type,
            tax_identification_number=tax_data.tax_identification_number,
            # HU005: Régimen tributario
            tax_regime=tax_data.tax_regime,
            # HU005: Upload de RUT
            rut_document_url=tax_data.rut_document_url,
            # HU005: Datos bancarios
            bank_name=tax_data.bank_name,
            bank_account_type=tax_data.bank_account_type,
            bank_account_number=tax_data.bank_account_number,
            bank_account_holder=tax_data.bank_account_holder,
            # HU005: Estado de validación (inicia como pendiente)
            verification_status=TaxDataVerificationStatus.PENDING,
            # Campos adicionales
            withholding_percentage=withholdings_rate,
            # Legacy fields (for compatibility)
            document=tax_data.tax_identification_number,
            bank_account=tax_data.bank_account_number
        )
        
        self.db.add(new_tax_data)
        self.db.flush()
        
        # Link to user
        user.tax_data_id = new_tax_data.tax_data_id
        self.db.commit()
        self.db.refresh(new_tax_data)
        
        return new_tax_data
    
    def update_tax_data(self, user_id: int, tax_data: TaxDataUpdateRequest) -> TaxData:
        """
        Actualiza los datos fiscales de un usuario (HU005)
        
        Permite actualizar los campos de datos fiscales. Si se actualiza el
        régimen fiscal, las retenciones se recalculan automáticamente.
        
        Args:
            user_id: ID del usuario
            tax_data: Datos fiscales a actualizar (solo los campos proporcionados)
        
        Returns:
            Objeto TaxData actualizado
        
        Raises:
            ValueError: Si el usuario no existe o no tiene datos fiscales registrados
        
        Nota: Solo se actualizan los campos que se proporcionan en la solicitud.
        Si se actualiza el régimen fiscal, las retenciones se recalculan automáticamente.
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if not user.tax_data_id:
            raise ValueError("User has no tax data. Use create endpoint first.")
        
        tax_data_obj = self.db.query(TaxData).filter(
            TaxData.tax_data_id == user.tax_data_id
        ).first()
        
        if not tax_data_obj:
            raise ValueError("Tax data not found")
        
        # Update fields (HU005)
        if tax_data.document_type is not None:
            tax_data_obj.document_type = tax_data.document_type
        if tax_data.tax_identification_number is not None:
            tax_data_obj.tax_identification_number = tax_data.tax_identification_number
            tax_data_obj.document = tax_data.tax_identification_number  # Legacy
        if tax_data.tax_regime is not None:
            tax_data_obj.tax_regime = tax_data.tax_regime
            # Recalculate withholdings if regime changed
            regime_value = tax_data.tax_regime.value if hasattr(tax_data.tax_regime, 'value') else str(tax_data.tax_regime)
            tax_data_obj.withholding_percentage = self.calculate_withholdings(regime_value)
        if tax_data.rut_document_url is not None:
            tax_data_obj.rut_document_url = tax_data.rut_document_url
        if tax_data.bank_name is not None:
            tax_data_obj.bank_name = tax_data.bank_name
        if tax_data.bank_account_type is not None:
            tax_data_obj.bank_account_type = tax_data.bank_account_type
        if tax_data.bank_account_number is not None:
            tax_data_obj.bank_account_number = tax_data.bank_account_number
            tax_data_obj.bank_account = tax_data.bank_account_number  # Legacy
        if tax_data.bank_account_holder is not None:
            tax_data_obj.bank_account_holder = tax_data.bank_account_holder
        
        # Si se actualiza información, el estado vuelve a pendiente (requiere revalidación)
        if any([
            tax_data.document_type is not None,
            tax_data.tax_identification_number is not None,
            tax_data.tax_regime is not None,
            tax_data.rut_document_url is not None,
            tax_data.bank_name is not None,
            tax_data.bank_account_type is not None,
            tax_data.bank_account_number is not None
        ]):
            tax_data_obj.verification_status = TaxDataVerificationStatus.PENDING
            tax_data_obj.verified_at = None
            tax_data_obj.rejection_reason = None
        
        self.db.commit()
        self.db.refresh(tax_data_obj)
        
        return tax_data_obj
    
    def get_tax_data(self, user_id: int) -> Optional[TaxData]:
        """
        Obtiene los datos fiscales de un usuario (HU005)
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Objeto TaxData si existe, None si el usuario no tiene datos fiscales
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user or not user.tax_data_id:
            return None
        
        return self.db.query(TaxData).filter(
            TaxData.tax_data_id == user.tax_data_id
        ).first()
    
    def get_tax_data_history(self, user_id: int) -> List[TaxData]:
        """
        Obtiene el historial de datos fiscales de un usuario (HU005)
        
        Nota: La implementación actual retorna el registro actual.
        Para un historial completo, se requiere implementar una tabla de auditoría/versionado.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Lista de objetos TaxData (actualmente solo el registro actual)
        
        TODO: Implementar tabla de auditoría para mantener historial completo de cambios
        """
        tax_data = self.get_tax_data(user_id)
        if tax_data:
            return [tax_data]
        return []
    
    def update_verification_status(
        self,
        user_id: int,
        status: TaxDataVerificationStatus,
        rejection_reason: Optional[str] = None
    ) -> TaxData:
        """
        Actualiza el estado de validación de los datos fiscales (HU005)
        
        Solo puede ser llamado por administradores para validar o rechazar
        los datos fiscales de un usuario.
        
        Args:
            user_id: ID del usuario
            status: Nuevo estado de validación (VERIFIED o REJECTED)
            rejection_reason: Motivo de rechazo (solo si status es REJECTED)
        
        Returns:
            Objeto TaxData actualizado
        
        Raises:
            ValueError: Si el usuario no existe o no tiene datos fiscales
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if not user.tax_data_id:
            raise ValueError("User has no tax data")
        
        tax_data_obj = self.db.query(TaxData).filter(
            TaxData.tax_data_id == user.tax_data_id
        ).first()
        
        if not tax_data_obj:
            raise ValueError("Tax data not found")
        
        tax_data_obj.verification_status = status
        tax_data_obj.verified_at = datetime.utcnow()
        
        if status == TaxDataVerificationStatus.REJECTED:
            tax_data_obj.rejection_reason = rejection_reason
        else:
            tax_data_obj.rejection_reason = None
        
        self.db.commit()
        self.db.refresh(tax_data_obj)
        
        return tax_data_obj


