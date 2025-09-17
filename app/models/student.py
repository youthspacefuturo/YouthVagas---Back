from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    github_url = db.Column(db.String(200))
    resume_url = db.Column(db.String(200))
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    city = db.Column(db.String(100))
    skills = db.Column(db.Text)
    about = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.name} - {self.email}>'
    
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
            'github_url': self.github_url,
            'resume_url': self.resume_url,
            'cpf': self.cpf,
            'city': self.city,
            'skills': self.skills,
            'about': self.about,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }