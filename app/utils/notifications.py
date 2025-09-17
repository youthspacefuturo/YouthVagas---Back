import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from flask import current_app
import logging

class NotificationService:
    """Serviço para envio de notificações por email e SMS"""
    
    @staticmethod
    def send_email(to_email, subject, body, is_html=False):
        """
        Enviar email usando SMTP
        
        Args:
            to_email: Email de destino
            subject: Assunto do email
            body: Corpo do email
            is_html: Se o corpo é HTML (padrão: False)
        """
        try:
            # Configurações SMTP do ambiente
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_username = os.environ.get('SMTP_USERNAME')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            from_email = os.environ.get('FROM_EMAIL', smtp_username)
            
            if not smtp_username or not smtp_password:
                current_app.logger.warning("SMTP credentials not configured")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Adicionar corpo
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_sms(to_phone, message):
        """
        Enviar SMS usando Twilio
        
        Args:
            to_phone: Número de telefone de destino
            message: Mensagem SMS
        """
        try:
            # Configurações Twilio do ambiente
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
            
            if not account_sid or not auth_token or not from_phone:
                current_app.logger.warning("Twilio credentials not configured")
                return False
            
            # Criar cliente Twilio
            client = Client(account_sid, auth_token)
            
            # Enviar SMS
            message = client.messages.create(
                body=message,
                from_=from_phone,
                to=to_phone
            )
            
            current_app.logger.info(f"SMS sent successfully to {to_phone}, SID: {message.sid}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send SMS to {to_phone}: {str(e)}")
            return False
    
    @staticmethod
    def send_reset_code_email(email, code, user_name=""):
        """Enviar código de reset por email"""
        subject = "YouthSpace - Código de Redefinição de Senha"
        
        body = f"""
Olá{' ' + user_name if user_name else ''},

Você solicitou a redefinição de sua senha no YouthSpace.

Seu código de verificação é: {code}

Este código expira em 15 minutos.

Se você não solicitou esta redefinição, ignore este email.

Atenciosamente,
Equipe YouthSpace
        """.strip()
        
        return NotificationService.send_email(email, subject, body)
    
    @staticmethod
    def send_reset_code_sms(phone, code):
        """Enviar código de reset por SMS"""
        message = f"YouthSpace: Seu código de redefinição de senha é {code}. Válido por 15 minutos."
        return NotificationService.send_sms(phone, message)
    
    @staticmethod
    def format_phone_number(phone):
        """
        Formatar número de telefone para padrão internacional
        
        Args:
            phone: Número de telefone
            
        Returns:
            Número formatado com +55 (Brasil)
        """
        # Remove caracteres não numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Se não tem código do país, adiciona +55 (Brasil)
        if len(clean_phone) == 11 and clean_phone.startswith('11'):
            return f"+55{clean_phone}"
        elif len(clean_phone) == 10:
            return f"+55{clean_phone}"
        elif len(clean_phone) == 13 and clean_phone.startswith('55'):
            return f"+{clean_phone}"
        else:
            return f"+55{clean_phone}"
