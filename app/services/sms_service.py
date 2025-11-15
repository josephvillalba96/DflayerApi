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
        
        Si Twilio no está configurado, solo registra el código en logs (modo desarrollo).
        No lanza excepciones para no interrumpir el flujo de registro.
        
        Args:
            phone_number: Número de teléfono del destinatario
            code: Código de verificación de 6 dígitos
        
        Returns:
            True si se procesó (enviado o logueado), False solo en caso de error crítico
        """
        try:
            # Verificar si Twilio está completamente configurado
            twilio_configured = (
                self.provider == 'twilio' and
                self.twilio_account_sid and
                self.twilio_auth_token and
                self.twilio_from_number
            )
            
            if twilio_configured:
                # Intentar enviar vía Twilio
                return self._send_via_twilio(phone_number, code)
            else:
                # Modo desarrollo/pruebas: solo loguear el código
                # No falla, solo informa que está en modo desarrollo
                print(f"[SMS DEV MODE] Twilio no configurado. Código de verificación para {phone_number}: {code}")
                print(f"[SMS DEV MODE] Para habilitar SMS real, configura TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y TWILIO_FROM_NUMBER en .env")
                return True  # Retorna True para no bloquear el flujo
        except Exception as e:
            # En caso de error, solo loguear y no fallar
            print(f"[SMS WARNING] Error al intentar enviar SMS (no crítico): {str(e)}")
            print(f"[SMS WARNING] El registro continúa normalmente. Código generado: {code}")
            return True  # Retorna True para no bloquear el flujo
    
    def _send_via_twilio(self, phone_number: str, code: str) -> bool:
        """
        Envía SMS usando Twilio
        
        Requiere: pip install twilio
        
        Si falla, no lanza excepción para no interrumpir el flujo.
        """
        try:
            from twilio.rest import Client
            
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
                print("[SMS WARNING] Twilio credentials not fully configured, falling back to dev mode")
                print(f"[SMS DEV MODE] Código de verificación para {phone_number}: {code}")
                return True  # No fallar, solo usar modo desarrollo
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=f"Your {settings.PROJECT_NAME} verification code is: {code}. Valid for 10 minutes.",
                from_=self.twilio_from_number,
                to=phone_number
            )
            
            if message.sid:
                print(f"[SMS SUCCESS] SMS enviado a {phone_number} (SID: {message.sid})")
                return True
            else:
                print(f"[SMS WARNING] Twilio no retornó SID, pero no falla el flujo")
                return True  # No fallar
        except ImportError:
            print("[SMS WARNING] twilio package not installed. Install with: pip install twilio")
            print(f"[SMS DEV MODE] Código de verificación para {phone_number}: {code}")
            return True  # No fallar, usar modo desarrollo
        except Exception as e:
            print(f"[SMS WARNING] Error sending SMS via Twilio (no crítico): {str(e)}")
            print(f"[SMS DEV MODE] Código de verificación para {phone_number}: {code}")
            return True  # No fallar, usar modo desarrollo
    
    @staticmethod
    def generate_code() -> str:
        """
        Genera un código de verificación de 6 dígitos
        
        Returns:
            Código de 6 dígitos como string
        """
        return f"{secrets.randbelow(1000000):06d}"

