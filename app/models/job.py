from app import db
from datetime import datetime, timezone

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary_range = db.Column(db.String(100))
    contract_type = db.Column(db.String(50))
    benefits = db.Column(db.Text)
    location = db.Column(db.String(100), nullable=False)
    work_hours = db.Column(db.String(50))
    work_mode = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    education = db.Column(db.String(100))
    experience = db.Column(db.String(100))
    skills = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys - agora referencia companies diretamente
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Relationships
    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job', lazy='dynamic')
    
    def __repr__(self):
        return f'<Job {self.title}>'
    
    def to_dict(self):
        # Parse benefits if it's a string
        benefits_list = []
        if self.benefits:
            if isinstance(self.benefits, str):
                benefits_list = [b.strip() for b in self.benefits.split(',') if b.strip()]
            else:
                benefits_list = self.benefits

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'salary_range': self.salary_range,
            'contract_type': self.contract_type,
            'benefits': benefits_list,
            'location': self.location,
            'work_hours': self.work_hours,
            'work_mode': self.work_mode,
            'requirements': self.requirements,
            'education': self.education,
            'experience': self.experience,
            'skills': [s.strip() for s in self.skills.split(',')] if self.skills else [],
            'is_active': self.is_active,
            'company_id': self.company_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            # Dados da empresa
            'company_name': self.company.name if self.company else 'Empresa não informada',
            'company_website': self.company.website if self.company else None,
            'company_sector': self.company.sector if self.company else 'Não informado',
            'company_size': self.company.company_size if self.company else 'Não informado',
            'company_about': self.company.about if self.company else 'Informações sobre a empresa não disponíveis.',
            'company_fantasy_name': self.company.fantasy_name if self.company else None,
            'company_city': self.company.city if self.company else None,
            'company_cnpj': self.company.cnpj if self.company else None,
            'company_phone': self.company.phone if self.company else None,
            'company_email': self.company.email if self.company else None,
            # Contagem de candidaturas
            'applications_count': self.applications.count() if self.applications else 0,
        }