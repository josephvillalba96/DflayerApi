"""
User Model
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class UserType(str, enum.Enum):
    """
    Enum for user types
    
    NOTA CRÍTICA DE DISEÑO:
    - Solo existen 2 tipos: "admin" y "usuario"
    - TODOS los usuarios tienen EXACTAMENTE las mismas funcionalidades:
      * Crear contenido
      * Crear campañas publicitarias
      * Vender bonos
      * Ganar por interacciones
      * Invitar referidos
    - is_business_account es SOLO una etiqueta visual que NO otorga permisos adicionales
    """
    USER = "usuario"  # usuario estándar
    ADMIN = "admin"  # administrador


class VerificationStatus(str, enum.Enum):
    """Enum for verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class AccountStatus(str, enum.Enum):
    """Enum for account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class User(Base):
    """System user model"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # password_hash
    phone_number = Column(String(20), nullable=True, unique=True, index=True)
    name = Column(String(100), nullable=False)  # full_name
    profile_picture = Column(String(500), nullable=True)  # profile_picture_url
    biography = Column(String(500), nullable=True)  # bio
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.USER)
    
    # Business account fields (SOLO visual, NO funcional)
    is_business_account = Column(Boolean, default=False)  # distinción visual, NO de permisos
    business_name = Column(String(200), nullable=True)  # si is_business_account = true
    business_category = Column(String(100), nullable=True)
    
    verification_status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING)
    identity_document_type = Column(String(50), nullable=True)
    identity_document_number = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    account_status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE)
    
    # Legacy fields (kept for compatibility)
    email_verified = Column(Boolean, default=False)  # Email verification status
    is_active = Column(Boolean, default=True)  # Account active status (maps to account_status)
    cover_picture = Column(String(500), nullable=True)
    level = Column(Integer, default=1)
    balance = Column(Float, default=0.0)  # Legacy - use Wallet table instead
    verified = Column(Boolean, default=False)  # Legacy - use verification_status instead
    tax_data_id = Column(Integer, ForeignKey("tax_data.tax_data_id"), nullable=True)
    multiplier_plan_id = Column(Integer, ForeignKey("multiplier_plans.plan_id"), nullable=True)
    following_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    registration_date = Column(Date, default=datetime.utcnow)  # created_at
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(Date, nullable=True)

    # Relationships
    tax_data = relationship("TaxData", back_populates="user")
    multiplier_plan = relationship("MembershipPlan", foreign_keys=[multiplier_plan_id])  # MultiplierPlan is alias
    
    # Relationships as merchant/comercio
    contents = relationship("Content", back_populates="merchant", foreign_keys="Content.merchant_id")
    # vouchers removed - use bonos relationship instead
    bonos = relationship("Bono", foreign_keys="Bono.comercio_id", back_populates="comercio")
    campaigns = relationship("AdvertisingCampaign", foreign_keys="AdvertisingCampaign.user_id", back_populates="user")
    campaigns_legacy = relationship("AdvertisingCampaign", foreign_keys="AdvertisingCampaign.merchant_id", back_populates="merchant")  # Legacy
    
    # Social relationships
    following_sent = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower"
    )
    following_received = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed"
    )
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    
    # Monetization relationships
    interactions = relationship("Interaction", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payment_distributions = relationship("PaymentDistribution", back_populates="user")
    
    # Notifications relationship
    notifications = relationship("Notification", back_populates="user")
    
    # Plan relationships
    plans = relationship("UserMembership", back_populates="user")  # UserPlan is alias of UserMembership
    
    # New relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    referrals_sent = relationship("ReferralNetwork", foreign_keys="ReferralNetwork.referrer_id", back_populates="referrer")
    referrals_received = relationship("ReferralNetwork", foreign_keys="ReferralNetwork.referred_id", back_populates="referred")
    mentions_received = relationship("PostMention", foreign_keys="PostMention.mentioned_user_id", back_populates="mentioned_user")
    memberships = relationship("UserMembership", back_populates="user")
    survey_responses = relationship("SurveyResponse", back_populates="user")
    interaction_distributions_received = relationship("InteractionDistribution", foreign_keys="InteractionDistribution.beneficiary_user_id", back_populates="beneficiary_user")
    bono_purchases = relationship("BonoPurchase", back_populates="buyer")
    bono_codes_redeemed = relationship("BonoCode", foreign_keys="BonoCode.redeemed_by_user_id", back_populates="redeemed_by")
    commission_distributions_received = relationship("CommissionDistribution", back_populates="beneficiary_user")
    withdrawal_requests = relationship("WithdrawalRequest", back_populates="user")
    tax_records = relationship("TaxRecord", back_populates="user")
    admin_logs = relationship("AdminLog", back_populates="admin_user")

