from app import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, interview, analysis
    cover_letter = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    job = db.relationship('Job', back_populates='applications')
    # student já está definido no backref do Student model
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'student_id': self.student_id,
            'status': self.status,
            'cover_letter': self.cover_letter,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'job': {
                'id': self.job.id if self.job else None,
                'title': self.job.title if self.job else None,
                'company_name': self.job.company.name if self.job and self.job.company else None,
            } if self.job else None,
            'student': {
                'id': self.student.id if self.student else None,
                'name': self.student.name if self.student else None,
                'email': self.student.email if self.student else None,
                'phone': self.student.phone if self.student else None,
                'cpf': self.student.cpf if self.student else None,
                'city': self.student.city if self.student else None,
                'about': self.student.about if self.student else None,
                'skills': self.student.skills.split(',') if self.student and self.student.skills else [],
                'github_url': self.student.github_url if self.student else None,
                'resume_url': self.student.resume_url if self.student else None,
            } if self.student else None}