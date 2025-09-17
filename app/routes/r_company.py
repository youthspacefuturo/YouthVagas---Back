from flask import Blueprint, request, jsonify
from app.services.company_services import CompanyService
from app.services.application_services import ApplicationService
from app.schemas.company_schema import CompanySchema
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


company_bp = Blueprint('company', __name__)
company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)

@company_bp.route('/companies', methods=['GET'])
def get_companies():
    """Listar todas as empresas ativas"""
    try:
        companies = CompanyService.get_all_companies()
        return jsonify(companies_schema.dump(companies)), 200
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@company_bp.route('/companies/<int:id>', methods=['GET'])
def get_company(id):
    """Buscar empresa por ID"""
    try:
        company = CompanyService.get_company_by_id(id)
        if company:
            return jsonify(company_schema.dump(company)), 200
        return jsonify({'error': 'Empresa não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@company_bp.route('/companies/profile/<int:id>', methods=['GET'])
@jwt_required()
def get_company_profile(id):
    """Buscar perfil da empresa por ID"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        if user_type != 'company':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Verificar se o ID corresponde ao usuário logado
        if user_id != id:
            return jsonify({'error': 'Acesso negado - ID não corresponde'}), 403
            
        company = CompanyService.get_company_by_id(id)
        if company:
            return jsonify(company_schema.dump(company)), 200
        return jsonify({'error': 'Empresa não encontrada'}), 404
    except Exception as e:
        print('[GET COMPANY PROFILE] Unexpected error:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@company_bp.route('/companies/profile', methods=['GET'])
@jwt_required()
def get_my_company_profile():
    """Buscar perfil da empresa logada"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        if user_type != 'company':
            return jsonify({'error': 'Acesso negado'}), 403
            
        company = CompanyService.get_company_by_id(user_id)
        if company:
            return jsonify(company_schema.dump(company)), 200
        return jsonify({'error': 'Empresa não encontrada'}), 404
    except Exception as e:
        print('[GET MY COMPANY PROFILE] Unexpected error:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@company_bp.route('/companies/profile', methods=['PUT'])
@jwt_required()
def update_company_profile():
    """Atualizar perfil da empresa"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        print('[UPDATE PROFILE] claims:', claims)
        print('[UPDATE PROFILE] user_type:', user_type)
        print('[UPDATE PROFILE] user_id:', user_id)
        
        if user_type != 'company':
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
            'fantasy_name': 'fantasy_name', 
            'email': 'email',
            'phone': 'phone',
            'cnpj': 'cnpj',
            'website': 'website',
            'sector': 'sector',
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

        # Atualizar empresa
        company = CompanyService.update_company(user_id, mapped_data)
        return jsonify(company_schema.dump(company)), 200
        
    except ValueError as e:
        print('[UPDATE PROFILE] Validation error:', str(e))
        return jsonify({'error': f'Erro de validação: {str(e)}'}), 400
        
    except Exception as e:
        print('[UPDATE PROFILE] Unexpected error:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@company_bp.route('/companies/applications', methods=['GET'])
@jwt_required()
def get_company_applications():
    """Listar todas as candidaturas da empresa"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        if user_type != 'company':
            return jsonify({'error': 'Acesso negado'}), 403
            
        applications = ApplicationService.get_company_applications(user_id)
        return jsonify([app.to_dict() for app in applications]), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@company_bp.route('/companies/applications/count', methods=['GET'])
@jwt_required()
def get_company_applications_count():
    """Buscar total de candidaturas para todas as vagas da empresa"""
    try:
        # Obter dados do JWT claims
        claims = get_jwt()
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        if user_type != 'company':
            return jsonify({'error': 'Acesso negado'}), 403
        
        total_count = ApplicationService.get_company_applications_count(user_id)
        return jsonify({'total_applications': total_count}), 200
        
    except Exception as e:
        print('[GET COMPANY APPLICATIONS COUNT] Unexpected error:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500