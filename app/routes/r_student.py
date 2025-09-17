from flask import Blueprint, request, jsonify
from app.services.student_service import StudentService
from app.services.application_services import ApplicationService
from app.schemas.student_schema import StudentSchema
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

student_bp = Blueprint('student', __name__)
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

@student_bp.route('/students', methods=['GET'])
def get_students():
    """Listar todos os estudantes ativos"""
    try:
        students = StudentService.get_all_students()
        return jsonify(students_schema.dump(students)), 200
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@student_bp.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    """Buscar estudante por ID"""
    try:
        student = StudentService.get_student_by_id(id)
        if student:
            return jsonify(student_schema.dump(student)), 200
        return jsonify({'error': 'Estudante não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@student_bp.route('/students/profile/<int:id>', methods=['GET'])
@jwt_required()
def get_student_profile(id):
    """Buscar perfil do estudante por ID"""
    try:
        current_user = get_jwt_identity()
        if current_user.get('type') != 'student':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Verificar se o ID corresponde ao usuário logado
        if current_user['id'] != id:
            return jsonify({'error': 'Acesso negado - ID não corresponde'}), 403
            
        student = StudentService.get_student_by_id(id)
        if student:
            return jsonify(student_schema.dump(student)), 200
        return jsonify({'error': 'Estudante não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@student_bp.route('/students/profile', methods=['GET'])
@jwt_required()
def get_my_student_profile():
    """Buscar perfil do estudante logado"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        if user_type != 'student':
            return jsonify({'error': 'Acesso negado'}), 403
            
        student = StudentService.get_student_by_id(user_id)
        if student:
            return jsonify(student_schema.dump(student)), 200
        return jsonify({'error': 'Estudante não encontrado'}), 404
    except Exception as e:
        print('[GET MY STUDENT PROFILE] Unexpected error:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@student_bp.route('/students/profile', methods=['PUT'])
@jwt_required()
def update_student_profile():
    """Atualizar perfil do estudante"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        print('[UPDATE PROFILE] claims:', claims)
        print('[UPDATE PROFILE] user_type:', user_type)
        print('[UPDATE PROFILE] user_id:', user_id)
        
        if user_type != 'student':
            return jsonify({'error': 'Acesso negado'}), 403

        # Validação dos dados JSON
        raw_data = request.get_json()
        print('[UPDATE PROFILE] raw_data type:', type(raw_data))
        print('[UPDATE PROFILE] raw_data:', raw_data)
        
        # Verificar se os dados são válidos
        if not raw_data:
            return jsonify({'error': 'Nenhum dado fornecido'}), 400
            
        if not isinstance(raw_data, dict):
            return jsonify({'error': 'Dados inválidos, esperado um objeto JSON'}), 400

        # Mapeamento de campos (se necessário)
        field_mapping = {
            'name': 'name',
            'email': 'email',
            'phone': 'phone',
            'cpf': 'cpf',
            'github_url': 'github_url',
            'resume_url': 'resume_url',
            'city': 'city',
            'skills': 'skills',
            'company_size': 'company_size',
            'about': 'about',
            'city': 'city'
        }
        
        # Mapear e filtrar dados válidos
        mapped_data = {}
        for k, v in raw_data.items():
            if k in field_mapping and v is not None and v != '':
                mapped_data[field_mapping[k]] = v
        
        print('[UPDATE PROFILE] mapped_data:', mapped_data)
        
        if not mapped_data:
            return jsonify({'error': 'Nenhum campo válido para atualizar'}), 400

        # Atualizar estudante
        student = StudentService.update_student(user_id, mapped_data)
        return jsonify(student_schema.dump(student)), 200
        
    except ValueError as e:
        print('[UPDATE PROFILE] Validation error:', str(e))
        return jsonify({'error': f'Erro de validação: {str(e)}'}), 400
        
    except Exception as e:
        print('[UPDATE PROFILE] Unexpected error:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@student_bp.route('/students/applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Listar candidaturas do estudante logado"""
    try:
        current_user = get_jwt_identity()
        if current_user.get('type') != 'student':
            return jsonify({'error': 'Acesso negado'}), 403
            
        applications = ApplicationService.get_student_applications(current_user['id'])
        return jsonify([app.to_dict() for app in applications]), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@student_bp.route('/students/job/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_by_id(application_id):
    """Buscar vaga específica por ID (público)"""
    try:
        job = JobService.get_job_by_id(application_id)
        if job and job.is_active:
            return jsonify(job_schema.dump(job)), 200
        return jsonify({'error': 'Vaga não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500
