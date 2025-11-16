"""
Database models (SQLAlchemy)
"""
from app.models.base import Base

# Base models
from app.models.tax_data import TaxData, TaxRegime, BankAccountType, DocumentType, TaxDataVerificationStatus
from app.models.user import User, UserType, VerificationStatus, AccountStatus
from app.models.user_profile import UserProfile, ProfileType
from app.models.email_verification import EmailVerification
from app.models.password_reset import PasswordReset
from app.models.two_factor_auth import TwoFactorAuth
from app.models.sms_verification import SMSVerification
from app.models.referral_network import ReferralNetwork
from app.models.wallet import Wallet
from app.models.post_mention import PostMention

# Content models
from app.models.content import Content, ContentType, ContentStatus, Visibility
from app.models.post_hashtag import PostHashtag
from app.models.multimedia_file import MultimediaFile, FileType, ProcessingStatus, UploadStatus, MediaType
from app.models.video_transcode import VideoTranscode
from app.models.image_variant import ImageVariant, VariantType
from app.models.audio_track import AudioTrack

# Social models
from app.models.follow import Follow
from app.models.like import Like
from app.models.comment import Comment

# Monetization models
from app.models.interaction import Interaction, ActionType, ValidationStatus
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.payment_distribution import InteractionDistribution, PaymentDistribution, DistributionStatus, DistributionLevel
from app.models.advertising_campaign import AdvertisingCampaign, SalesCommission, BudgetType, CampaignStatus, CommissionStatus
from app.models.campaign_post import CampaignPost
from app.models.action_reward import ActionReward
from app.models.campaign_segmentation import CampaignSegmentation, Gender
from app.models.survey import Survey, SurveyResponse, QuestionType

# Bono and plan models (only models from spec)
from app.models.voucher import Bono  # Voucher is alias, not in spec
from app.models.bono_image import BonoImage
from app.models.bono_purchase import BonoPurchase, PurchaseStatus
from app.models.bono_code import BonoCode, RedemptionStatus
from app.models.multiplier_plan import MembershipPlan, UserMembership  # MultiplierPlan/UserPlan are aliases, not in spec
from app.models.commission_distribution import CommissionDistribution

# Additional models (only from spec)
from app.models.notification import Notification, NotificationType
from app.models.event_fund import EventFund
from app.models.withdrawal_request import WithdrawalRequest, WithdrawalMethod, RequestStatus
from app.models.tax_record import TaxRecord, TaxType
from app.models.admin_log import AdminLog

__all__ = [
    "Base",
    "TaxData",
    "TaxRegime",
    "BankAccountType",
    "DocumentType",
    "TaxDataVerificationStatus",
    "User",
    "UserType",
    "VerificationStatus",
    "AccountStatus",
    "UserProfile",
    "ProfileType",
    "EmailVerification",
    "PasswordReset",
    "TwoFactorAuth",
    "SMSVerification",
    "ReferralNetwork",
    "Wallet",
    "PostMention",
    "Content",
    "ContentType",
    "ContentStatus",
    "Visibility",
    "PostHashtag",
    "MultimediaFile",
    "FileType",
    "ProcessingStatus",
    "UploadStatus",
    "MediaType",
    "VideoTranscode",
    "ImageVariant",
    "VariantType",
    "AudioTrack",
    "Follow",
    "Like",
    "Comment",
    "ActionType",
    "ValidationStatus",
    "Interaction",
    "Transaction",
    "TransactionType",
    "TransactionStatus",
    "InteractionDistribution",
    "PaymentDistribution",
    "DistributionStatus",
    "DistributionLevel",
    "Bono",
    "BonoImage",
    "BonoPurchase",
    "PurchaseStatus",
    "BonoCode",
    "RedemptionStatus",
    "MembershipPlan",
    "UserMembership",
    "AdvertisingCampaign",
    "SalesCommission",
    "BudgetType",
    "CampaignStatus",
    "CommissionStatus",
    "CampaignPost",
    "ActionReward",
    "CampaignSegmentation",
    "Gender",
    "Survey",
    "SurveyResponse",
    "QuestionType",
    "CommissionDistribution",
    "WithdrawalRequest",
    "WithdrawalMethod",
    "RequestStatus",
    "TaxRecord",
    "TaxType",
    "AdminLog",
    "Notification",
    "NotificationType",
    "EventFund",
]
