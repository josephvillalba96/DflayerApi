"""
Email Service using SMTP (Gmail compatible)
Handles sending emails via SMTP protocol
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings


class EmailSMTPService:
    """Service for sending emails via SMTP (Gmail compatible)"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER or "smtp.gmail.com"
        self.smtp_port = settings.SMTP_PORT or 587
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME or settings.PROJECT_NAME
        self.use_tls = settings.SMTP_USE_TLS if hasattr(settings, 'SMTP_USE_TLS') else True
        
        if not self.smtp_username or not self.smtp_password:
            print("WARNING: SMTP credentials not configured. Email sending may fail.")
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> MIMEMultipart:
        """Create a MIME multipart message"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.from_email}>"
        msg['To'] = to_email
        
        # Add plain text version if provided
        if plain_content:
            part1 = MIMEText(plain_content, 'plain', 'utf-8')
            msg.attach(part1)
        
        # Add HTML version
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part2)
        
        return msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            plain_content: Plain text content (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password or not self.from_email:
            print(f"WARNING: SMTP not fully configured. Would send email to {to_email}")
            return False
        
        try:
            # Create message
            msg = self._create_message(to_email, subject, html_content, plain_content)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Enable TLS if configured
            if self.use_tls:
                server.starttls()
            
            # Login
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            server.send_message(msg)
            
            # Close connection
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {str(e)}")
            print("Tip: For Gmail, you may need to use an App Password instead of your regular password.")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error sending email via SMTP: {str(e)}")
            return False
    
    def send_verification_email(self, email: str, name: str, token: str) -> bool:
        """Send email verification email"""
        verification_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #007bff;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Welcome to {settings.PROJECT_NAME}!</h2>
                <p>Hi {name},</p>
                <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                <p><a href="{verification_url}" class="button">Verify Email</a></p>
                <p>Or copy and paste this link in your browser:</p>
                <p><a href="{verification_url}">{verification_url}</a></p>
                <p>This link will expire in 7 days.</p>
                <p>If you didn't create an account, please ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
                </div>
            </div>
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
        
        Best regards,
        The {settings.PROJECT_NAME} Team
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
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #dc3545;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>Hi {name},</p>
                <p>You requested to reset your password. Click the button below to reset it:</p>
                <p><a href="{reset_url}" class="button">Reset Password</a></p>
                <p>Or copy and paste this link in your browser:</p>
                <p><a href="{reset_url}">{reset_url}</a></p>
                <div class="warning">
                    <p><strong>Important:</strong> This link will expire in 24 hours.</p>
                </div>
                <p>If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
                <div class="footer">
                    <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
        Password Reset Request
        
        Hi {name},
        
        You requested to reset your password. Visit this link to reset it:
        {reset_url}
        
        Important: This link will expire in 24 hours.
        
        If you didn't request a password reset, please ignore this email and your password will remain unchanged.
        
        Best regards,
        The {settings.PROJECT_NAME} Team
        """
        
        return self.send_email(
            to_email=email,
            subject=f"Reset your {settings.PROJECT_NAME} password",
            html_content=html_content,
            plain_content=plain_content
        )


