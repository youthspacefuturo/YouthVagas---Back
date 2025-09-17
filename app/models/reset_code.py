from app import db
from datetime import datetime, timedelta
import secrets
import string

class ResetCode(db.Model):
    """Modelo para códigos de reset de senha"""
    __tablename__ = 'reset_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True, index=True)
    method = db.Column(db.Enum('email', 'sms', name='reset_method'), nullable=False)
    user_type = db.Column(db.Enum('student', 'company', name='user_type'), nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(64), nullable=True, index=True)  # Token para confirmar nova senha
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, email=None, phone=None, method='email', user_type='student', expires_in_minutes=15):
        """
        Criar novo código de reset
        
        Args:
            email: Email do usuário (se method='email')
            phone: Telefone do usuário (se method='sms')
            method: 'email' ou 'sms'
            user_type: 'student' ou 'company'
            expires_in_minutes: Tempo de expiração em minutos (padrão: 15)
        """
        self.code = self.generate_code()
        self.email = email
        self.phone = phone
        self.method = method
        self.user_type = user_type
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    
    @staticmethod
    def generate_code():
        """Gerar código de 6 dígitos"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def is_expired(self):
        """Verificar se o código expirou"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Verificar se o código é válido (não usado e não expirado)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Marcar código como usado"""
        self.is_used = True
        db.session.commit()
    
    def set_verification_token(self, token):
        """Definir token de verificação para confirmar nova senha"""
        self.verification_token = token
        db.session.commit()
    
    @classmethod
    def find_by_token(cls, token):
        """Encontrar código por token de verificação"""
        return cls.query.filter_by(
            verification_token=token,
            is_used=True  # Token só é válido após código ter sido usado
        ).filter(cls.expires_at > datetime.utcnow()).first()
    
    @classmethod
    def find_valid_code(cls, code, email=None, phone=None, method='email', user_type='student'):
        """
        Encontrar código válido
        
        Args:
            code: Código de 6 dígitos
            email: Email do usuário (se method='email')
            phone: Telefone do usuário (se method='sms')
            method: 'email' ou 'sms'
            user_type: 'student' ou 'company'
        """
        query = cls.query.filter_by(
            code=code,
            method=method,
            user_type=user_type,
            is_used=False
        ).filter(cls.expires_at > datetime.utcnow())
        
        if method == 'email' and email:
            query = query.filter_by(email=email)
        elif method == 'sms' and phone:
            query = query.filter_by(phone=phone)
        
        return query.first()
    
    @classmethod
    def cleanup_expired(cls):
        """Limpar códigos expirados (executar periodicamente)"""
        expired_codes = cls.query.filter(cls.expires_at <= datetime.utcnow()).all()
        for code in expired_codes:
            db.session.delete(code)
        db.session.commit()
        return len(expired_codes)
    
    def to_dict(self):
        """Converter para dicionário (sem expor o código)"""
        return {
            'id': self.id,
            'method': self.method,
            'user_type': self.user_type,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'is_used': self.is_used,
            'is_expired': self.is_expired()
        }
