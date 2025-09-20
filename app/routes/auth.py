from flask import Blueprint, request, jsonify, make_response, current_app
from app import db
from app.services.auth_services import AuthService
from app.services.student_service import StudentService
from app.services.company_services import CompanyService
from app.schemas.student_schema import StudentSchema
from app.schemas.company_schema import CompanySchema
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity, create_refresh_token,
    set_access_cookies, set_refresh_cookies, unset_jwt_cookies, verify_jwt_in_request,
    get_jwt
)
from app.middleware.auth_middleware import student_or_company_required

auth_bp = Blueprint('auth', __name__)
student_schema = StudentSchema()
company_schema = CompanySchema()

@auth_bp.route('/', methods=['GET'])
def auth_info():
    """Informações sobre endpoints de autenticação disponíveis"""
    return jsonify({
        'message': 'Endpoints de autenticação disponíveis',
        'endpoints': {
            'student_register': 'POST /api/auth/register/student',
            'company_register': 'POST /api/auth/register/company',
            'student_login': 'POST /api/auth/login/student',
            'company_login': 'POST /api/auth/login/company',
            'logout': 'POST /api/auth/logout',
            'refresh': 'POST /api/auth/refresh',
            'me': 'GET /api/auth/me',
            'debug': 'GET /api/auth/debug',
            'reset_password': 'POST /api/auth/reset-password',
            'verify_reset_code': 'POST /api/auth/verify-reset-code',
            'confirm_new_password': 'POST /api/auth/confirm-new-password'
        },
        'status': 'active'
    }), 200

@auth_bp.route('/debug', methods=['GET'])
def debug_cookies():
    """Endpoint de debug para verificar cookies"""
    cookies = request.cookies
    headers = dict(request.headers)
    
    debug_info = {
        'cookies_received': dict(cookies),
        'headers': headers,
        'has_access_token': 'access_token' in cookies,
        'has_refresh_token': 'refresh_token' in cookies,
        'access_token_value': cookies.get('access_token', 'NOT_FOUND')[:20] + '...' if cookies.get('access_token') else 'NOT_FOUND'
    }
    
    if current_app.debug:
        print(f"DEBUG COOKIES: {debug_info}")
    
    return jsonify(debug_info), 200

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    """Registrar novo estudante"""
    try:
        data = request.get_json()
        
        # Validar dados com schema
        errors = student_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Criar estudante
        student = AuthService.register_student(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            phone=data['phone'],
            cpf=data['cpf'],
            github_url=data.get('github_url'),
            resume_url=data.get('resume_url')
        )
        
        return jsonify({
            'message': 'Estudante cadastrado com sucesso',
            'student': student_schema.dump(student)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    """Registrar nova empresa"""
    try:
        data = request.get_json()
        
        # Validar dados com schema
        errors = company_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Criar empresa
        company = AuthService.register_company(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            phone=data['phone'],
            cnpj=data['cnpj'],
            website=data.get('website'),
            sector=data.get('sector'),
            company_size=data.get('company_size'),
            about=data.get('about')
        )
        
        return jsonify({
            'message': 'Empresa cadastrada com sucesso',
            'company': company_schema.dump(company)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/login/student', methods=['POST'])
def login_student():
    """Login para estudantes com cookies seguros"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        student = AuthService.login_student(email, password)
        
        # Criar tokens JWT - usar string como identity e adicionar claims customizados
        user_identity = f"student:{student.id}"
        access_token = create_access_token(
            identity=user_identity,
            additional_claims={
                'user_id': student.id,
                'email': student.email,
                'type': 'student'
            }
        )
        refresh_token = create_refresh_token(
            identity=user_identity,
            additional_claims={
                'user_id': student.id,
                'email': student.email,
                'type': 'student'
            }
        )
        
        # Criar resposta com cookies seguros
        response = make_response(jsonify({
            'message': 'Login realizado com sucesso',
            'user': {
                'id': student.id,
                'name': student.name,
                'email': student.email,
                'type': 'student'
            }
        }))
        
        # Definir cookies httpOnly seguros com configurações explícitas
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        # Configurações adicionais de cookie para garantir compatibilidade
        response.set_cookie(
            'access_token_set', 
            'true', 
            max_age=900,  # 15 minutos
            httponly=False,  # Para debug no frontend
            secure=False,
            samesite='Lax'
        )
        
        if current_app.debug:
            print(f"DEBUG: Cookies definidos para estudante {student.email}")
            print(f"DEBUG: Headers da resposta: {dict(response.headers)}")
        
        return response, 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Erro no login do estudante: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/login/company', methods=['POST'])
def login_company():
    """Login para empresas com cookies seguros"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        company = AuthService.login_company(email, password)
        
        # Criar tokens JWT - usar string como identity e adicionar claims customizados
        user_identity = f"company:{company.id}"
        access_token = create_access_token(
            identity=user_identity,
            additional_claims={
                'user_id': company.id,
                'email': company.email,
                'type': 'company'
            }
        )
        refresh_token = create_refresh_token(
            identity=user_identity,
            additional_claims={
                'user_id': company.id,
                'email': company.email,
                'type': 'company'
            }
        )
        
        # Criar resposta com cookies seguros
        response = make_response(jsonify({
            'message': 'Login realizado com sucesso',
            'user': {
                'id': company.id,
                'name': company.name,
                'email': company.email,
                'type': 'company'
            }
        }))
        
        # Definir cookies httpOnly seguros com configurações explícitas
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        # Configurações adicionais de cookie para garantir compatibilidade
        response.set_cookie(
            'access_token_set', 
            'true', 
            max_age=900,  # 15 minutos
            httponly=False,  # Para debug no frontend
            secure=False,
            samesite='Lax'
        )
        
        if current_app.debug:
            print(f"DEBUG: Cookies definidos para empresa {company.email}")
            print(f"DEBUG: Headers da resposta: {dict(response.headers)}")
        
        return response, 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Erro no login da empresa: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/logout', methods=['POST'])
#@student_or_company_required
def logout():
    """Logout seguro do usuário"""
    try:
        response = make_response(jsonify({'message': 'Logout realizado com sucesso'}))
        
        # Remover todos os cookies JWT
        unset_jwt_cookies(response)
        
        return response, 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar token de acesso usando refresh token"""
    try:
        # Debug logging para diagnosticar problemas
        if current_app.debug:
            print("🔄 DEBUG: Refresh endpoint chamado")
            print(f"🔄 DEBUG: Cookies recebidos: {dict(request.cookies)}")
        
        # Obter identity e claims do refresh token
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if current_app.debug:
            print(f"🔄 DEBUG: Identity: {identity}")
            print(f"🔄 DEBUG: Claims: {claims}")
        
        if not identity:
            if current_app.debug:
                print("❌ DEBUG: Identity não encontrada no refresh token")
            return jsonify({'error': 'Refresh token inválido - sem identity'}), 401
        
        if not claims:
            if current_app.debug:
                print("❌ DEBUG: Claims não encontradas no refresh token")
            return jsonify({'error': 'Refresh token inválido - sem claims'}), 401
        
        # Verificar se usuário ainda existe e está ativo
        user_type = claims.get('type')
        user_id = claims.get('user_id')
        
        if current_app.debug:
            print(f"🔄 DEBUG: user_type: {user_type}, user_id: {user_id}")
        
        if not user_type or not user_id:
            if current_app.debug:
                print(f"❌ DEBUG: Dados incompletos - user_type: {user_type}, user_id: {user_id}")
            return jsonify({'error': 'Refresh token inválido - dados incompletos'}), 401
        
        user = None
        if user_type == 'student':
            user = StudentService.get_student_by_id(user_id)
            if not user or not user.is_active:
                if current_app.debug:
                    print(f"❌ DEBUG: Estudante inválido ou inativo - user: {user}")
                return jsonify({'error': 'Conta de estudante inválida ou inativa'}), 403
        elif user_type == 'company':
            user = CompanyService.get_company_by_id(user_id)
            if not user or not user.is_active:
                if current_app.debug:
                    print(f"❌ DEBUG: Empresa inválida ou inativa - user: {user}")
                return jsonify({'error': 'Conta de empresa inválida ou inativa'}), 403
        else:
            if current_app.debug:
                print(f"❌ DEBUG: Tipo de usuário inválido: {user_type}")
            return jsonify({'error': 'Tipo de usuário inválido'}), 403
        
        # Criar novo access token
        user_identity = f"{user_type}:{user_id}"
        new_access_token = create_access_token(
            identity=user_identity,
            additional_claims={
                'user_id': user_id,
                'email': user.email,
                'type': user_type
            }
        )
        
        # Criar resposta e definir novo cookie de access token
        response = make_response(jsonify({
            'message': 'Token renovado com sucesso',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'type': user_type
            }
        }))
        
        set_access_cookies(response, new_access_token)

        
        if current_app.debug:
            print(f"✅ DEBUG: Token renovado com sucesso para {user.email} ({user_type})")
        
        return response, 200
        
    except Exception as e:
        if current_app.debug:
            print(f"❌ DEBUG: Erro no refresh: {str(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        current_app.logger.error(f"Erro ao renovar token: {str(e)}")
        return jsonify({'error': 'Token de refresh inválido ou expirado'}), 401

@auth_bp.route('/me', methods=['GET'])
@student_or_company_required
def get_current_user(**kwargs):
    """Obter informações do usuário atual autenticado"""
    try:
        current_user = kwargs.get('current_user')
        user_data = kwargs.get('user_data')
        user_type = current_user.get('type')
        
        if not user_data:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user_type == 'student':
            return jsonify({
                'user': student_schema.dump(user_data),
                'type': 'student'
            }), 200
            
        elif user_type == 'company':
            return jsonify({
                'user': company_schema.dump(user_data),
                'type': 'company'
            }), 200
        
        return jsonify({'error': 'Tipo de usuário inválido'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter usuário atual: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Enviar código de reset de senha por email ou SMS"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        method = data.get('method', 'email')
        email = data.get('email')
        phone = data.get('phone')
        
        # Validar método
        if method not in ['email', 'sms']:
            return jsonify({'error': 'Método deve ser "email" ou "sms"'}), 400
        
        # Validar dados baseado no método
        if method == 'email':
            if not email:
                return jsonify({'error': 'Email é obrigatório'}), 400
            # Validação básica de email
            if '@' not in email or '.' not in email:
                return jsonify({'error': 'Email inválido'}), 400
        elif method == 'sms':
            if not phone:
                return jsonify({'error': 'Telefone é obrigatório'}), 400
            # Validação básica de telefone
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) < 10:
                return jsonify({'error': 'Telefone inválido'}), 400
        
        # Enviar código
        result = AuthService.send_reset_code(
            email=email,
            phone=phone,
            method=method
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Reset password error: {str(e)}')
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    """Verificar código de reset de senha"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        code = data.get('code')
        method = data.get('method', 'email')
        email = data.get('email')
        phone = data.get('phone')
        
        # Validações
        if not code:
            return jsonify({'error': 'Código é obrigatório'}), 400
        
        if len(code) != 6 or not code.isdigit():
            return jsonify({'error': 'Código deve ter 6 dígitos'}), 400
        
        if method not in ['email', 'sms']:
            return jsonify({'error': 'Método deve ser "email" ou "sms"'}), 400
        
        if method == 'email' and not email:
            return jsonify({'error': 'Email é obrigatório'}), 400
        
        if method == 'sms' and not phone:
            return jsonify({'error': 'Telefone é obrigatório'}), 400
        
        # Verificar código
        result = AuthService.verify_reset_code(
            code=code,
            email=email,
            phone=phone,
            method=method
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Verify reset code error: {str(e)}')
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/confirm-new-password', methods=['POST'])
def confirm_new_password():
    """Confirmar nova senha após verificação do código"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        email = data.get('email')  # Opcional, para validação adicional
        phone = data.get('phone')  # Opcional, para validação adicional
        
        # Validações
        if not token:
            return jsonify({'error': 'Token é obrigatório'}), 400
        
        if not new_password:
            return jsonify({'error': 'Nova senha é obrigatória'}), 400
        
        if not confirm_password:
            return jsonify({'error': 'Confirmação de senha é obrigatória'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Senhas não coincidem'}), 400
        
        # Confirmar nova senha
        result = AuthService.confirm_new_password(
            token=token,
            new_password=new_password,
            confirm_password=confirm_password,
            email=email,
            phone=phone
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Confirm new password error: {str(e)}')
        return jsonify({'error': 'Erro interno do servidor'}), 500