"""
Email Service Factory
Provides a unified interface for email sending that supports both SMTP and SendGrid
"""
from typing import Optional
from app.core.config import settings
from app.services.email_service import EmailService as SendGridEmailService
from app.services.email_smtp_service import EmailSMTPService


class EmailServiceFactory:
    """Factory for creating email service instances"""
    
    @staticmethod
    def get_email_service():
        """
        Get the appropriate email service based on configuration
        
        Returns:
            Email service instance (SMTP or SendGrid)
        """
        provider = settings.EMAIL_PROVIDER.lower()
        
        if provider == "smtp":
            return EmailSMTPService()
        elif provider == "sendgrid":
            return SendGridEmailService()
        else:
            # Default to SMTP if provider is not recognized
            print(f"WARNING: Unknown email provider '{provider}'. Defaulting to SMTP.")
            return EmailSMTPService()


# Unified Email Service Interface
class UnifiedEmailService:
    """
    Unified email service that automatically selects the appropriate provider
    based on configuration (SMTP or SendGrid)
    """
    
    def __init__(self):
        self._service = EmailServiceFactory.get_email_service()
        self._provider = settings.EMAIL_PROVIDER.lower()
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email using the configured provider
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            plain_content: Plain text content (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        return self._service.send_email(to_email, subject, html_content, plain_content)
    
    def send_verification_email(self, email: str, name: str, token: str) -> bool:
        """Send email verification email"""
        return self._service.send_verification_email(email, name, token)
    
    def send_password_reset_email(self, email: str, name: str, token: str) -> bool:
        """Send password reset email"""
        return self._service.send_password_reset_email(email, name, token)
    
    @property
    def provider(self) -> str:
        """Get the current email provider"""
        return self._provider


