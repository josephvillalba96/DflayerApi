"""
User Service (HU004)
Handles user profile management and interests
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.user import User
# UserCategory removed - UserPreferences model not in spec
from app.schemas.user import (
    ProfileUpdateRequest,
    ProfilePictureUpdateRequest,
    CoverPictureUpdateRequest,
    InterestCategoryRequest,
    BusinessAccountActivateRequest
)


class UserService:
    """
    Servicio de Gestión de Perfil de Usuario (HU004)
    
    Proporciona métodos para gestionar el perfil del usuario:
    - Actualización de información personal
    - Gestión de fotos de perfil y portada
    - Gestión de categorías de interés
    """
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio de usuario
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def update_profile(self, user_id: int, profile_data: ProfileUpdateRequest) -> User:
        """
        Actualiza el perfil del usuario (HU004)
        
        Permite actualizar información personal del usuario:
        - Nombre
        - Biografía
        - Fecha de nacimiento
        - Ubicación
        
        Args:
            user_id: ID del usuario
            profile_data: Datos del perfil a actualizar
        
        Returns:
            Objeto User actualizado
        
        Raises:
            ValueError: Si el usuario no existe
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Update fields if provided
        if profile_data.name is not None:
            user.name = profile_data.name
        if profile_data.biography is not None:
            user.biography = profile_data.biography
        if profile_data.birth_date is not None:
            user.birth_date = profile_data.birth_date
        if profile_data.city is not None:
            user.city = profile_data.city
        if profile_data.country is not None:
            user.country = profile_data.country
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_profile_picture(self, user_id: int, picture_data: ProfilePictureUpdateRequest) -> User:
        """
        Actualiza la foto de perfil del usuario (HU004)
        
        Args:
            user_id: ID del usuario
            picture_data: URL de la foto de perfil
        
        Returns:
            Objeto User actualizado
        
        Raises:
            ValueError: Si el usuario no existe
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.profile_picture = picture_data.profile_picture_url
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_cover_picture(self, user_id: int, picture_data: CoverPictureUpdateRequest) -> User:
        """
        Actualiza la foto de portada del usuario (HU004)
        
        Args:
            user_id: ID del usuario
            picture_data: URL de la foto de portada
        
        Returns:
            Objeto User actualizado
        
        Raises:
            ValueError: Si el usuario no existe
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.cover_picture = picture_data.cover_picture_url
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def add_interest_category(self, user_id: int, category_id: int):
        """
        NOTA: Funcionalidad deshabilitada - UserCategory model no está en el documento.
        """
        raise ValueError("Interest categories functionality is disabled - UserCategory model not in spec")
    
    def remove_interest_category(self, user_id: int, category_id: int) -> bool:
        """
        NOTA: Funcionalidad deshabilitada - UserCategory model no está en el documento.
        """
        raise ValueError("Interest categories functionality is disabled - UserCategory model not in spec")
    
    def get_user_interests(self, user_id: int) -> List[dict]:
        """
        NOTA: Funcionalidad deshabilitada - UserCategory model no está en el documento.
        """
        return []  # Return empty list as UserCategory model doesn't exist
    
    def get_user_profile(self, user_id: int) -> Optional[User]:
        """
        Obtiene el perfil completo del usuario (HU004)
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Objeto User si existe, None en caso contrario
        """
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def activate_business_account(self, user_id: int, business_data: BusinessAccountActivateRequest) -> User:
        """
        Activa la cuenta de negocio del usuario (HU003)
        
        Convierte una cuenta personal en cuenta de negocio. Esta es una distinción
        puramente visual/branding que NO otorga funcionalidades adicionales.
        
        Cualquier usuario YA puede crear campañas, vender bonos, etc., sin necesidad
        de activar la cuenta de negocio.
        
        Args:
            user_id: ID del usuario
            business_data: Datos de la cuenta de negocio (nombre, categoría, datos fiscales opcionales)
        
        Returns:
            Objeto User actualizado con cuenta de negocio activada
        
        Raises:
            ValueError: Si el usuario no existe o si los datos fiscales no existen (cuando se proporciona tax_data_id)
        
        Nota importante:
        - NO otorga funcionalidades adicionales
        - Es solo una distinción de presentación/branding
        - Se puede desactivar en cualquier momento
        - Un influencer personal puede crear campañas SIN ser cuenta de negocio
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Validate tax_data_id if provided
        if business_data.tax_data_id:
            from app.models.tax_data import TaxData
            tax_data = self.db.query(TaxData).filter(
                TaxData.tax_data_id == business_data.tax_data_id
            ).first()
            if not tax_data:
                raise ValueError("Tax data not found")
            # Verify tax data belongs to user
            if tax_data.user_id != user_id:
                raise ValueError("Tax data does not belong to this user")
        
        # Activate business account
        user.is_business_account = True
        user.business_name = business_data.business_name
        user.business_category = business_data.business_category
        if business_data.tax_data_id:
            user.tax_data_id = business_data.tax_data_id
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_business_account(self, user_id: int) -> User:
        """
        Desactiva la cuenta de negocio del usuario (HU003)
        
        Convierte una cuenta de negocio de vuelta a cuenta personal.
        Esto solo afecta la presentación visual del perfil.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Objeto User actualizado con cuenta de negocio desactivada
        
        Raises:
            ValueError: Si el usuario no existe
        
        Nota: Los datos de negocio (business_name, business_category) se mantienen
        en la base de datos pero se ocultan cuando is_business_account = False.
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Deactivate business account
        user.is_business_account = False
        # Note: We keep business_name and business_category in DB for potential reactivation
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_business_account_info(self, user_id: int) -> Optional[User]:
        """
        Obtiene la información de cuenta de negocio del usuario (HU003)
        
        Args:
            user_id: ID del usuario
        
        Returns:
            Objeto User si existe, None en caso contrario
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

