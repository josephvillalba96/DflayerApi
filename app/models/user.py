"""
User Model
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class UserType(str, enum.Enum):
    """Enum for user types"""
    ADMIN = "admin"
    MERCHANT = "merchant"
    AFFILIATE = "affiliate"
    CLIENT = "client"


class User(Base):
    """System user model"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_type = Column(SQLEnum(UserType), nullable=False, default=UserType.CLIENT)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # Password hash
    email_verified = Column(Boolean, default=False)  # Email verification status
    is_active = Column(Boolean, default=True)  # Account active status
    profile_picture = Column(String(500), nullable=True)
    cover_picture = Column(String(500), nullable=True)
    biography = Column(String(500), nullable=True)
    level = Column(Integer, default=1)
    balance = Column(Float, default=0.0)
    verified = Column(Boolean, default=False)
    birth_date = Column(Date, nullable=True)
    tax_data_id = Column(Integer, ForeignKey("tax_data.tax_data_id"), nullable=True)
    multiplier_plan_id = Column(Integer, ForeignKey("multiplier_plans.plan_id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.location_id"), nullable=True)
    following_count = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    registration_date = Column(Date, default=datetime.utcnow)

    # Relationships
    tax_data = relationship("TaxData", back_populates="user")
    location = relationship("Location", foreign_keys=[location_id])
    multiplier_plan = relationship("MultiplierPlan", foreign_keys=[multiplier_plan_id])
    
    # Relationships as merchant
    contents = relationship("Content", back_populates="merchant", foreign_keys="Content.merchant_id")
    vouchers = relationship("Voucher", back_populates="merchant")
    campaigns = relationship("AdvertisingCampaign", back_populates="merchant")
    
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
    
    # Feed and preferences relationships
    feed_items = relationship("FeedItem", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    interest_categories = relationship("UserCategory", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    # Plan relationships
    plans = relationship("UserPlan", back_populates="user")
    
    # Authentication relationships
    email_verification = relationship("EmailVerification", back_populates="user", uselist=False)
    two_factor_auth = relationship("TwoFactorAuth", back_populates="user", uselist=False)
    two_factor_codes = relationship("TwoFactorCode", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")

