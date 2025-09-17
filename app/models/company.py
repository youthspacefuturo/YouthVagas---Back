from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    website = db.Column(db.String(200))
    sector = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    about = db.Column(db.Text)
    fantasy_name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    jobs = db.relationship('Job', back_populates='company', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Company {self.name} - {self.email}>'
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'cnpj': self.cnpj,
            'website': self.website,
            'sector': self.sector,
            'company_size': self.company_size,
            'about': self.about,
            'fantasy_name': self.fantasy_name,
            'city': self.city,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }