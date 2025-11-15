"""
SMS Service
Servicio para envío de códigos de verificación por SMS (HU001)
"""
import secrets
from typing import Optional
from app.core.config import settings


class SMSService:
    """
    Servicio para envío de SMS
    
    Soporta múltiples proveedores (Twilio, AWS SNS, etc.)
    Por ahora implementa una estructura base que puede extenderse.
    """
    
    def __init__(self):
        self.provider = getattr(settings, 'SMS_PROVIDER', 'twilio').lower()
        # Configuración de Twilio (si está disponible)
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.twilio_from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
    
    def send_verification_code(self, phone_number: str, code: str) -> bool:
        """
        Envía un código de verificación por SMS
        
        Args:
            phone_number: Número de teléfono del destinatario
            code: Código de verificación de 6 dígitos
        
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            if self.provider == 'twilio' and self.twilio_account_sid:
                return self._send_via_twilio(phone_number, code)
            else:
                # Modo desarrollo: solo loguear el código
                print(f"[SMS DEV MODE] Verification code for {phone_number}: {code}")
                return True
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False
    
    def _send_via_twilio(self, phone_number: str, code: str) -> bool:
        """
        Envía SMS usando Twilio
        
        Requiere: pip install twilio
        """
        try:
            from twilio.rest import Client
            
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
                print("WARNING: Twilio credentials not fully configured")
                return False
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=f"Your {settings.PROJECT_NAME} verification code is: {code}. Valid for 10 minutes.",
                from_=self.twilio_from_number,
                to=phone_number
            )
            
            return message.sid is not None
        except ImportError:
            print("WARNING: twilio package not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            print(f"Error sending SMS via Twilio: {str(e)}")
            return False
    
    @staticmethod
    def generate_code() -> str:
        """
        Genera un código de verificación de 6 dígitos
        
        Returns:
            Código de 6 dígitos como string
        """
        return f"{secrets.randbelow(1000000):06d}"

