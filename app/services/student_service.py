from app import db
from app.models.student import Student
from sqlalchemy.exc import IntegrityError

class StudentService:
    @staticmethod
    def create_student(data):
        # Validações para evitar violações de UNIQUE constraint
        email = data.get('email')
        cpf = data.get('cpf')

        if not email:
            raise ValueError('Email é obrigatório')
        
        if not cpf:
            raise ValueError('CPF é obrigatório')

        # Garantir unicidade do email
        if Student.query.filter_by(email=email).first():
            raise ValueError('Email já cadastrado')

        # Garantir unicidade do CPF
        if Student.query.filter_by(cpf=cpf).first():
            raise ValueError('CPF já cadastrado')

        # Hash da senha
        password = data.pop('password', None)
        if not password:
            raise ValueError('Senha é obrigatória')
            
        student = Student(**data)
        student.set_password(password)
        
        db.session.add(student)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Violação de unicidade: email ou cpf já cadastrados')
        return student
    
    @staticmethod
    def get_all_students():
        try:
            return Student.query.filter_by(is_active=True).all()
        except Exception as e:
            raise Exception(f"Erro ao buscar estudantes: {str(e)}")
    
    @staticmethod
    def get_student_by_id(id):
        return Student.query.get(id)
    
    @staticmethod
    def get_student_by_email(email):
        return Student.query.filter_by(email=email).first()
    
    @staticmethod
    def update_student(id, data):
        """Update student profile with comprehensive validation and error handling"""
        print(f'[STUDENT SERVICE] Updating student {id} with data: {data}')
        
        student = Student.query.get(id)
        if not student:
            raise ValueError('Estudante não encontrado')
        
        # Campos permitidos para atualização
        allowed_fields = {
            'name', 'email', 'phone', 'cpf', 'github_url', 'resume_url', 
            'city', 'skills', 'about'
        }
        
        # Campos obrigatórios que não podem ser vazios se fornecidos
        required_fields = {'name', 'email', 'phone', 'cpf'}
        
        # Campos opcionais que podem ser None/empty
        optional_fields = {'github_url', 'resume_url', 'city', 'skills', 'about'}
        
        # Hash da nova senha se fornecida
        if 'password' in data:
            password = data.pop('password')
            if password and password.strip():  # Só atualiza se não for vazio
                print('[STUDENT SERVICE] Updating password')
                student.set_password(password)
        
        # Validar unicidade de email e CPF se estão sendo alterados
        if 'email' in data and data['email'] and data['email'] != student.email:
            existing_email = Student.query.filter_by(email=data['email']).first()
            if existing_email:
                raise ValueError('Email já está em uso por outro estudante')
        
        if 'cpf' in data and data['cpf'] and data['cpf'] != student.cpf:
            existing_cpf = Student.query.filter_by(cpf=data['cpf']).first()
            if existing_cpf:
                raise ValueError('CPF já está em uso por outro estudante')
        
        # Atualizar apenas campos permitidos
        updated_fields = []
        for key, value in data.items():
            if key not in allowed_fields:
                print(f'[STUDENT SERVICE] Skipping field {key} - not allowed')
                continue
                
            # Campos obrigatórios: não podem ser None ou string vazia se fornecidos
            if key in required_fields:
                if value is None or (isinstance(value, str) and not value.strip()):
                    print(f'[STUDENT SERVICE] Skipping empty required field {key}')
                    continue  # Skip empty required fields in partial updates
                else:
                    print(f'[STUDENT SERVICE] Updating required field {key}: {value}')
                    setattr(student, key, value)
                    updated_fields.append(key)
            
            # Campos opcionais: podem ser None ou vazios
            elif key in optional_fields:
                print(f'[STUDENT SERVICE] Updating optional field {key}: {value}')
                setattr(student, key, value if value else None)
                updated_fields.append(key)
        
        print(f'[STUDENT SERVICE] Updated fields: {updated_fields}')
        
        try:
            db.session.commit()
            print(f'[STUDENT SERVICE] Successfully updated student {id}')
            # Forçar refresh do objeto após commit
            db.session.refresh(student)
        except IntegrityError as e:
            db.session.rollback()
            print(f'[STUDENT SERVICE] IntegrityError: {str(e)}')
            raise ValueError('Erro de integridade: email ou CNPJ já cadastrados')
        except Exception as e:
            db.session.rollback()
            print(f'[COMPANY SERVICE] Database error during commit: {str(e)}')
            raise ValueError(f'Erro no banco de dados: {str(e)}')
        
        return student
    
    @staticmethod
    def delete_student(id):
        student = Student.query.get(id)
        if not student:
            raise ValueError('Estudante não encontrado')
        
        # Verificar se há applications ativas
        from app.models.application import Application
        active_applications = Application.query.filter_by(student_id=id).count()
        if active_applications > 0:
            # Desativar ao invés de deletar se houver candidaturas
            student.is_active = False
            db.session.commit()
            return student
        
        db.session.delete(student)
        db.session.commit()