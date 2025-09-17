from app import db
from app.models.job import Job
from app.models.company import Company

class JobService:
    @staticmethod
    def create_job(data, extra_payload=None):
        # Garantir que company_id está presente
        if 'company_id' not in data:
            raise ValueError('company_id é obrigatório para criar uma vaga')
        
        # Buscar dados completos da empresa
        company = Company.query.get(data['company_id'])
        if not company:
            raise ValueError('Empresa não encontrada')
        
        # Atualizar dados da empresa se vierem no payload extra (opcional)
        if extra_payload:
            # company (nome curto) e companyUrl (website)
            if isinstance(extra_payload.get('company'), str):
                company.name = extra_payload['company']

            if isinstance(extra_payload.get('companyUrl'), str):
                company.website = extra_payload['companyUrl']

            # companyInfo { sector, size, website, about }
            info = extra_payload.get('companyInfo')
            if isinstance(info, dict):
                if info.get('sector'):
                    company.sector = info.get('sector')
                if info.get('size'):
                    company.company_size = info.get('size')
                if info.get('website'):
                    company.website = info.get('website')
                if info.get('about'):
                    company.about = info.get('about')
            
            # Salvar mudanças na empresa se houver
            db.session.flush()

        # Criar a vaga com os dados fornecidos
        job = Job(**data)
        db.session.add(job)
        db.session.commit()
        
        # Recarregar a vaga com os dados da empresa para garantir que o relacionamento está carregado
        from sqlalchemy.orm import joinedload
        job_with_company = Job.query.options(joinedload(Job.company)).get(job.id)
        
        return job_with_company
    
    @staticmethod
    def get_all_jobs():
        from sqlalchemy.orm import joinedload
        return Job.query.options(joinedload(Job.company)).filter_by(is_active=True).all()
    
    @staticmethod
    def get_job_by_id(id):
        from sqlalchemy.orm import joinedload
        return Job.query.options(joinedload(Job.company)).get(id)
    
    @staticmethod
    def get_jobs_by_company(company_id):
        from sqlalchemy.orm import joinedload
        return Job.query.options(joinedload(Job.company)).filter_by(company_id=company_id, is_active=True).all()
    
    @staticmethod
    def update_job(id, data, extra_payload=None):
        job = Job.query.get(id)
        if not job:
            raise ValueError('Vaga não encontrada')
        
        # Atualizar dados da empresa vinculada, se vierem no payload
        if extra_payload and 'company_id' in data:
            company = Company.query.get(data['company_id'])
            if company:
                if isinstance(extra_payload.get('company'), str):
                    company.name = extra_payload['company']
                if isinstance(extra_payload.get('companyUrl'), str):
                    company.website = extra_payload['companyUrl']
                info = extra_payload.get('companyInfo')
                if isinstance(info, dict):
                    if 'sector' in info:
                        company.sector = info.get('sector')
                    if 'size' in info:
                        company.company_size = info.get('size')
                    if 'website' in info:
                        company.website = info.get('website')
                    if 'about' in info:
                        company.about = info.get('about')

        for key, value in data.items():
            setattr(job, key, value)
        
        db.session.commit()
        return job
    
    @staticmethod
    def delete_job(id):
        job = Job.query.get(id)
        if not job:
            raise ValueError('Vaga não encontrada')
        
        db.session.delete(job)
        db.session.commit()
    
    @staticmethod
    def deactivate_job(id):
        job = Job.query.get(id)
        if not job:
            raise ValueError('Vaga não encontrada')
        
        job.is_active = False
        db.session.commit()
        return job