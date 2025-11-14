"""
Email Service
Handles sending emails via SendGrid
"""
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.core.config import settings


class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        self.sendgrid_client = None
        if settings.SENDGRID_API_KEY:
            self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SendGrid
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            plain_content: Plain text content (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.sendgrid_client:
            # Log warning: SendGrid not configured
            print(f"WARNING: SendGrid not configured. Would send email to {to_email}")
            return False
        
        try:
            from_email = Email(settings.SENDGRID_FROM_EMAIL or "noreply@dflayer.com")
            to_email_obj = To(to_email)
            
            if plain_content:
                content = Content("text/plain", plain_content)
            else:
                content = Content("text/html", html_content)
            
            mail = Mail(from_email, to_email_obj, subject, content)
            
            response = self.sendgrid_client.send(mail)
            
            # Check if successful (2xx status codes)
            if 200 <= response.status_code < 300:
                return True
            else:
                print(f"Error sending email: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_verification_email(self, email: str, name: str, token: str) -> bool:
        """Send email verification email"""
        verification_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/verify-email?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to {settings.PROJECT_NAME}!</h2>
            <p>Hi {name},</p>
            <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 7 days.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </body>
        </html>
        """
        
        plain_content = f"""
        Welcome to {settings.PROJECT_NAME}!
        
        Hi {name},
        
        Thank you for registering. Please verify your email address by visiting:
        {verification_url}
        
        This link will expire in 7 days.
        
        If you didn't create an account, please ignore this email.
        """
        
        return self.send_email(
            to_email=email,
            subject=f"Verify your {settings.PROJECT_NAME} account",
            html_content=html_content,
            plain_content=plain_content
        )
    
    def send_password_reset_email(self, email: str, name: str, token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/reset-password?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {name},</p>
            <p>You requested to reset your password. Click the link below to reset it:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{reset_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request a password reset, please ignore this email.</p>
        </body>
        </html>
        """
        
        plain_content = f"""
        Password Reset Request
        
        Hi {name},
        
        You requested to reset your password. Visit this link to reset it:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request a password reset, please ignore this email.
        """
        
        return self.send_email(
            to_email=email,
            subject=f"Reset your {settings.PROJECT_NAME} password",
            html_content=html_content,
            plain_content=plain_content
        )

