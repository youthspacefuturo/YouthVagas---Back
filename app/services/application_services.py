from app import db
from app.models.application import Application
from app.models.student import Student

class ApplicationService:
    @staticmethod
    def apply_to_job(job_id, student_id, cover_letter=None):
        from app.models.job import Job
        
        # Verificar se a vaga existe e está ativa
        job = Job.query.filter_by(id=job_id, is_active=True).first()
        if not job:
            raise ValueError('Vaga não encontrada ou inativa')
        
        student = Student.query.filter_by(id=student_id, is_active=True).first()
        if not student:
            raise ValueError('Estudante não encontrado ou inativo')
        
        # Verificar se o estudante já se candidatou para esta vaga
        existing_application = Application.query.filter_by(
            job_id=job_id, 
            student_id=student_id
        ).first()
        if existing_application:
            raise ValueError('Você já se candidatou para esta vaga')

        application = Application(
            job_id=job_id,
            student_id=student.id,
            cover_letter=cover_letter
        )
        db.session.add(application)
        db.session.commit()
        return application
    
    @staticmethod
    def get_applications_for_job(job_id, company_id=None):
        from app.models.job import Job
        
        # Verificar se a vaga existe
        job = Job.query.get(job_id)
        if not job:
            raise ValueError('Vaga não encontrada')
        
        # Se company_id for fornecido, verificar se a vaga pertence à empresa
        if company_id and job.company_id != company_id:
            raise ValueError('Não autorizado a ver candidaturas desta vaga')
        
        # Buscar candidaturas da vaga com relacionamentos carregados
        from sqlalchemy.orm import joinedload
        return Application.query.options(
            joinedload(Application.student),
            joinedload(Application.job)
        ).filter_by(job_id=job_id).all()
    
    @staticmethod
    def get_company_applications(company_id):
        from app.models.job import Job
        
        jobs = Job.query.filter_by(company_id=company_id).all()
        job_ids = [job.id for job in jobs]
        
        from sqlalchemy.orm import joinedload
        return Application.query.options(
            joinedload(Application.student),
            joinedload(Application.job)
        ).filter(Application.job_id.in_(job_ids))\
         .order_by(Application.created_at.desc())\
         .all()
    
    @staticmethod
    def get_student_applications(student_id):
        """Buscar todas as candidaturas de um estudante"""
        from sqlalchemy.orm import joinedload
        return Application.query.options(
            joinedload(Application.student),
            joinedload(Application.job)
        ).filter_by(student_id=student_id)\
         .order_by(Application.created_at.desc())\
         .all()
    
    @staticmethod
    def update_application_status(application_id, status, company_id=None):
        application = Application.query.get(application_id)
        
        if not application:
            raise ValueError('Candidatura não encontrada')
            
        if company_id and application.job.company_id != company_id:
            raise ValueError('Não autorizado')
        
        # Status válidos: pending, analysis, interview, accepted, rejected
        valid_statuses = ['pending', 'analysis', 'interview', 'accepted', 'rejected']
        if status not in valid_statuses:
            raise ValueError(f'Status inválido. Use um de: {", ".join(valid_statuses)}')
            
        application.status = status
        db.session.commit()
        return application
    
    @staticmethod
    def get_company_applications_count(company_id):
        """Contar total de candidaturas para todas as vagas de uma empresa"""
        from app.models.job import Job
        
        # Buscar todas as vagas da empresa
        jobs = Job.query.filter_by(company_id=company_id).all()
        job_ids = [job.id for job in jobs]
        
        if not job_ids:
            return 0
        
        # Contar candidaturas para essas vagas
        return Application.query.filter(Application.job_id.in_(job_ids)).count()
    
    @staticmethod
    def delete_application(application_id, company_id=None):
        """Deletar uma candidatura (apenas empresa dona da vaga pode deletar)"""
        application = Application.query.get(application_id)
        
        if not application:
            raise ValueError('Candidatura não encontrada')
            
        # Verificar se a empresa tem permissão para deletar
        if company_id and application.job.company_id != company_id:
            raise ValueError('Não autorizado a deletar esta candidatura')
        
        db.session.delete(application)
        db.session.commit()
        return True
    
    @staticmethod
    def get_job_applications_count(job_id):
        """Contar candidaturas de uma vaga específica"""
        return Application.query.filter_by(job_id=job_id).count()