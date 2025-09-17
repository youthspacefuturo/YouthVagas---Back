from app import db
from app.models.company import Company
from sqlalchemy.exc import IntegrityError

class CompanyService:
    @staticmethod
    def create_company(data):
        # Validações para evitar violações de UNIQUE constraint
        email = data.get('email')
        cnpj = data.get('cnpj')

        if not email:
            raise ValueError('Email é obrigatório')
        
        if not cnpj:
            raise ValueError('CNPJ é obrigatório')

        # Garantir unicidade do email
        if Company.query.filter_by(email=email).first():
            raise ValueError('Email já cadastrado')

        # Garantir unicidade do CNPJ
        if Company.query.filter_by(cnpj=cnpj).first():
            raise ValueError('CNPJ já cadastrado')

        # Hash da senha
        password = data.pop('password', None)
        if not password:
            raise ValueError('Senha é obrigatória')
            
        company = Company(**data)
        company.set_password(password)
        
        db.session.add(company)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Violação de unicidade: email ou cnpj já cadastrados')
        return company
    
    @staticmethod
    def get_all_companies():
        return Company.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_company_by_id(id):
        return Company.query.get(id)
    
    @staticmethod
    def get_company_by_email(email):
        return Company.query.filter_by(email=email).first()
    
    @staticmethod
    def update_company(id, data):
        """Update company profile with comprehensive validation and error handling"""
        print(f'[COMPANY SERVICE] Updating company {id} with data: {data}')
        
        company = Company.query.get(id)
        if not company:
            raise ValueError('Empresa não encontrada')
        
        # Campos permitidos para atualização
        allowed_fields = {
            'name', 'email', 'phone', 'cnpj', 'website', 
            'sector', 'company_size', 'about', 'fantasy_name', 'city'
        }
        
        # Campos obrigatórios que não podem ser vazios se fornecidos
        required_fields = {'name', 'email', 'phone', 'cnpj'}
        
        # Campos opcionais que podem ser None/empty
        optional_fields = {'website', 'sector', 'company_size', 'about', 'fantasy_name', 'city'}
        
        # Hash da nova senha se fornecida
        if 'password' in data:
            password = data.pop('password')
            if password and password.strip():  # Só atualiza se não for vazio
                print('[COMPANY SERVICE] Updating password')
                company.set_password(password)
        
        # Validar unicidade de email e CNPJ se estão sendo alterados
        if 'email' in data and data['email'] and data['email'] != company.email:
            existing_email = Company.query.filter_by(email=data['email']).first()
            if existing_email:
                raise ValueError('Email já está em uso por outra empresa')
        
        if 'cnpj' in data and data['cnpj'] and data['cnpj'] != company.cnpj:
            existing_cnpj = Company.query.filter_by(cnpj=data['cnpj']).first()
            if existing_cnpj:
                raise ValueError('CNPJ já está em uso por outra empresa')
        
        # Atualizar apenas campos permitidos
        updated_fields = []
        for key, value in data.items():
            if key not in allowed_fields:
                print(f'[COMPANY SERVICE] Skipping field {key} - not allowed')
                continue
                
            # Campos obrigatórios: não podem ser None ou string vazia se fornecidos
            if key in required_fields:
                if value is None or (isinstance(value, str) and not value.strip()):
                    print(f'[COMPANY SERVICE] Skipping empty required field {key}')
                    continue  # Skip empty required fields in partial updates
                else:
                    print(f'[COMPANY SERVICE] Updating required field {key}: {value}')
                    setattr(company, key, value)
                    updated_fields.append(key)
            
            # Campos opcionais: podem ser None ou vazios
            elif key in optional_fields:
                print(f'[COMPANY SERVICE] Updating optional field {key}: {value}')
                setattr(company, key, value if value else None)
                updated_fields.append(key)
        
        print(f'[COMPANY SERVICE] Updated fields: {updated_fields}')
        
        try:
            db.session.commit()
            print(f'[COMPANY SERVICE] Successfully updated company {id}')
            # Forçar refresh do objeto após commit
            db.session.refresh(company)
        except IntegrityError as e:
            db.session.rollback()
            print(f'[COMPANY SERVICE] IntegrityError: {str(e)}')
            raise ValueError('Erro de integridade: email ou CNPJ já cadastrados')
        except Exception as e:
            db.session.rollback()
            print(f'[COMPANY SERVICE] Database error during commit: {str(e)}')
            raise ValueError(f'Erro no banco de dados: {str(e)}')
        
        return company
    
    @staticmethod
    def delete_company(id):
        company = Company.query.get(id)
        if not company:
            raise ValueError('Empresa não encontrada')
        
        # Verificar se há jobs ativos
        from app.models.job import Job
        active_jobs = Job.query.filter_by(company_id=id, is_active=True).count()
        if active_jobs > 0:
            # Desativar ao invés de deletar se houver vagas ativas
            company.is_active = False
            db.session.commit()
            return company
        
        db.session.delete(company)
        db.session.commit()