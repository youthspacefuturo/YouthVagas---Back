import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('MAIL_PORT', '587'))
        self.email_user = os.getenv('MAIL_USERNAME')
        self.email_password = os.getenv('MAIL_APP_PASSWORD')
        self.from_name = os.getenv('FROM_NAME', 'YouthSpace')
        
    def _get_reset_password_template(self, user_name: str, verification_code: str) -> str:
        """
        Template HTML responsivo para email de redefinição de senha
        Baseado no design fornecido na imagem
        """
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Código de Verificação - YouthSpace</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            text-align: center;
            color: white;
        }}
        
        .logo {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        
        .header-subtitle {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .header-description {{
            font-size: 14px;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .greeting {{
            font-size: 16px;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .message {{
            font-size: 15px;
            margin-bottom: 15px;
            color: #555;
            line-height: 1.5;
        }}
        
        .code-container {{
            background-color: #f8f9ff;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .verification-code {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
        }}
        
        .security-info {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
        }}
        
        .security-title {{
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        
        .security-title::before {{
            content: "⚠️";
            margin-right: 8px;
        }}
        
        .security-list {{
            list-style: none;
            padding: 0;
        }}
        
        .security-list li {{
            color: #856404;
            margin-bottom: 5px;
            padding-left: 20px;
            position: relative;
        }}
        
        .security-list li::before {{
            content: "•";
            color: #f39c12;
            font-weight: bold;
            position: absolute;
            left: 0;
        }}
        
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}
        
        .footer-text {{
            font-size: 13px;
            color: #6c757d;
            margin-bottom: 10px;
        }}
        
        .footer-brand {{
            font-size: 14px;
            color: #667eea;
            font-weight: 600;
        }}
        
        .footer-tagline {{
            font-size: 12px;
            color: #adb5bd;
            font-style: italic;
        }}
        
        /* Responsividade para mobile */
        @media only screen and (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 30px 15px;
            }}
            
            .logo {{
                font-size: 28px;
            }}
            
            .header-subtitle {{
                font-size: 16px;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
            
            .verification-code {{
                font-size: 28px;
                letter-spacing: 4px;
            }}
            
            .code-container {{
                padding: 20px 15px;
                margin: 20px 0;
            }}
            
            .security-info {{
                padding: 15px;
                margin: 20px 0;
            }}
            
            .footer {{
                padding: 20px 15px;
            }}
        }}
        
        @media only screen and (max-width: 480px) {{
            .verification-code {{
                font-size: 24px;
                letter-spacing: 2px;
            }}
            
            .logo {{
                font-size: 24px;
            }}
            
            .header-subtitle {{
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Youth Space</div>
            <div class="header-subtitle">Código de Verificação</div>
            <div class="header-description">Redefinição de senha</div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <div class="greeting">Olá {user_name},</div>
            
            <div class="message">
                Recebemos uma solicitação para redefinir a senha da sua conta no YouthVagas.
            </div>
            
            <div class="message">
                Use o código de verificação abaixo para redefinir sua senha:
            </div>
            
            <!-- Verification Code -->
            <div class="code-container">
                <div class="verification-code">{verification_code}</div>
            </div>
            
            <!-- Security Information -->
            <div class="security-info">
                <div class="security-title">Informações de Segurança:</div>
                <ul class="security-list">
                    <li>Este código expira em 1 hora</li>
                    <li>Só pode ser usado uma vez</li>
                    <li>Se você não solicitou esta redefinição, ignore este email</li>
                    <li>Nunca compartilhe este código com outras pessoas</li>
                </ul>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-text">
                Este email foi enviado automaticamente pelo sistema YouthSpace.
            </div>
            <div class="footer-text">
                Se você tiver dúvidas, entre em contato conosco.
            </div>
            <div class="footer-brand">YouthSpace</div>
            <div class="footer-tagline">Conectando jovens ao futuro profissional</div>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_welcome_template(self, user_name: str, user_type: str) -> str:
        """
        Template HTML para email de boas-vindas
        """
        platform_name = "YouthVagas" if user_type == "student" else "YouthSpace Empresas"
        
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bem-vindo ao YouthSpace!</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            padding: 40px 20px;
            text-align: center;
            color: white;
        }}
        
        .logo {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        
        .header-subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .welcome-message {{
            font-size: 24px;
            font-weight: bold;
            color: #28a745;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .message {{
            font-size: 15px;
            margin-bottom: 15px;
            color: #555;
            line-height: 1.5;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
        }}
        
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}
        
        .footer-text {{
            font-size: 13px;
            color: #6c757d;
            margin-bottom: 10px;
        }}
        
        .footer-brand {{
            font-size: 14px;
            color: #28a745;
            font-weight: 600;
        }}
        
        .footer-tagline {{
            font-size: 12px;
            color: #adb5bd;
            font-style: italic;
        }}
        
        @media only screen and (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 30px 15px;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
            
            .welcome-message {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">Youth Space</div>
            <div class="header-subtitle">Bem-vindo ao {platform_name}!</div>
        </div>
        
        <div class="content">
            <div class="welcome-message">🎉 Conta criada com sucesso!</div>
            
            <div class="message">Olá {user_name},</div>
            
            <div class="message">
                Seja bem-vindo ao YouthSpace! Sua conta foi criada com sucesso e você já pode começar a explorar todas as oportunidades disponíveis.
            </div>
            
            <div class="message">
                {'Como estudante, você pode buscar vagas, aplicar para oportunidades e construir seu futuro profissional.' if user_type == 'student' else 'Como empresa, você pode publicar vagas, encontrar talentos jovens e fazer parte do futuro do mercado de trabalho.'}
            </div>
            
            <div style="text-align: center;">
                <a href="#" class="cta-button">Acessar Plataforma</a>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-text">
                Este email foi enviado automaticamente pelo sistema YouthSpace.
            </div>
            <div class="footer-brand">YouthSpace</div>
            <div class="footer-tagline">Conectando jovens ao futuro profissional</div>
        </div>
    </div>
</body>
</html>
        """
    
    def send_reset_password_email(self, to_email: str, user_name: str, verification_code: str) -> bool:
        """
        Enviar email de redefinição de senha
        """
        try:
            if not self.email_user or not self.email_password:
                logger.error("Credenciais de email não configuradas")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email
            msg['Subject'] = f"YouthSpace - Código de Verificação: {verification_code}"
            
            # Template HTML
            html_body = self._get_reset_password_template(user_name, verification_code)
            
            # Versão texto simples como fallback
            text_body = f"""
YouthSpace - Código de Verificação

Olá {user_name},

Recebemos uma solicitação para redefinir a senha da sua conta no YouthVagas.

Seu código de verificação é: {verification_code}

Informações importantes:
- Este código expira em 1 hora
- Só pode ser usado uma vez
- Se você não solicitou esta redefinição, ignore este email

YouthSpace - Conectando jovens ao futuro profissional
            """
            
            # Anexar ambas as versões
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email de redefinição de senha enviado para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de redefinição: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str, user_type: str) -> bool:
        """
        Enviar email de boas-vindas
        """
        try:
            if not self.email_user or not self.email_password:
                logger.error("Credenciais de email não configuradas")
                return False
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email
            msg['Subject'] = "Bem-vindo ao YouthSpace! 🎉"
            
            # Template HTML
            html_body = self._get_welcome_template(user_name, user_type)
            
            # Versão texto simples
            platform_name = "YouthVagas" if user_type == "student" else "YouthSpace Empresas"
            text_body = f"""
YouthSpace - Bem-vindo!

Olá {user_name},

Seja bem-vindo ao {platform_name}! Sua conta foi criada com sucesso.

YouthSpace - Conectando jovens ao futuro profissional
            """
            
            # Anexar ambas as versões
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email de boas-vindas enviado para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de boas-vindas: {str(e)}")
            return False
    
    def send_custom_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Enviar email customizado
        """
        try:
            if not self.email_user or not self.email_password:
                logger.error("Credenciais de email não configuradas")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.email_user}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email customizado enviado para {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email customizado: {str(e)}")
            return False

# Instância global do serviço
email_service = EmailService()