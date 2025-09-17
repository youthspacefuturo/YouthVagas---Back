from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.models.student import Student
from app.models.company import Company
from flask_jwt_extended import JWTError

def student_required(f):
    """Decorator para verificar se usuário é estudante logado"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        if not current_user or current_user.get('type') != 'student':
            return jsonify({'error': 'Acesso restrito a estudantes'}), 403
        
        # Verificar se estudante ainda existe e está ativo
        student = Student.query.get(current_user['id'])
        if not student or not student.is_active:
            return jsonify({'error': 'Conta de estudante inválida ou inativa'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def company_required(f):
    """Decorator para verificar se usuário é empresa logada"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        if not current_user or current_user.get('type') != 'company':
            return jsonify({'error': 'Acesso restrito a empresas'}), 403
        
        # Verificar se empresa ainda existe e está ativa
        company = Company.query.get(current_user['id'])
        if not company or not company.is_active:
            return jsonify({'error': 'Conta de empresa inválida ou inativa'}), 403
        
        # 🔑 aqui injeta o usuário no kwargs
        kwargs["current_user"] = current_user  
        
        return f(*args, **kwargs)
    return decorated_function

def student_or_company_required(f):
    """Decorator para verificar se é estudante OU empresa"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        if not current_user:
            return jsonify({'error': 'Autenticação obrigatória'}), 401
        
        user_type = current_user.get('type')
        if user_type not in ['student', 'company']:
            return jsonify({'error': 'Tipo de usuário inválido'}), 403
        
        # Verificar se conta ainda existe e está ativa
        if user_type == 'student':
            user = Student.query.get(current_user['id'])
        else:
            user = Company.query.get(current_user['id'])
            
        if not user or not user.is_active:
            return jsonify({'error': 'Conta inválida ou inativa'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def own_resource_required(resource_type='student'):
    """
    Decorator para verificar se usuário pode acessar próprio recurso
    resource_type: 'student' ou 'company'
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            
            if not current_user:
                return jsonify({'error': 'Autenticação obrigatória'}), 401
            
            # Verificar tipo de usuário
            if current_user.get('type') != resource_type:
                return jsonify({'error': f'Acesso restrito a {resource_type}s'}), 403
            
            # Verificar se está tentando acessar próprio recurso
            resource_id = kwargs.get('id') or kwargs.get('student_id') or kwargs.get('company_id')
            
            if resource_id and current_user['id'] != resource_id:
                return jsonify({'error': 'Você só pode acessar seus próprios dados'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def job_owner_required(f):
    """Decorator para verificar se empresa é dona da vaga"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        if not current_user or current_user.get('type') != 'company':
            return jsonify({'error': 'Apenas empresas podem gerenciar vagas'}), 403
        
        # Verificar se a vaga pertence à empresa
        job_id = kwargs.get('id') or kwargs.get('job_id')
        if job_id:
            from app.models.job import Job
            job = Job.query.get(job_id)
            
            if not job:
                return jsonify({'error': 'Vaga não encontrada'}), 404
                
            if job.company_id != current_user['id']:
                return jsonify({'error': 'Você só pode gerenciar suas próprias vagas'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def application_owner_required(f):
    """Decorator para verificar se empresa pode ver/gerenciar candidatura"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        
        if not current_user or current_user.get('type') != 'company':
            return jsonify({'error': 'Apenas empresas podem gerenciar candidaturas'}), 403
        
        # Verificar se a candidatura é de vaga da empresa
        application_id = kwargs.get('id') or kwargs.get('application_id')
        if application_id:
            from app.models.application import Application
            application = Application.query.get(application_id)
            
            if not application:
                return jsonify({'error': 'Candidatura não encontrada'}), 404
                
            if application.job.company_id != current_user['id']:
                return jsonify({'error': 'Você só pode gerenciar candidaturas das suas vagas'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def optional_auth(f):
    """Decorator para rotas que funcionam com ou sem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            current_user = get_jwt_identity()
        except JWTError:
            current_user = None
            
        # Adicionar current_user aos kwargs para usar na função
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    return decorated_function

# Funções auxiliares para usar nas rotas
def get_current_student():
    """Retorna o estudante atual logado"""
    current_user = get_jwt_identity()
    if current_user and current_user.get('type') == 'student':
        return Student.query.get(current_user['id'])
    return None

def get_current_company():
    """Retorna a empresa atual logada"""
    current_user = get_jwt_identity()
    if current_user and current_user.get('type') == 'company':
        return Company.query.get(current_user['id'])
    return None

