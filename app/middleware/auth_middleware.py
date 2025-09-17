from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, verify_jwt_in_request,
    create_access_token, set_access_cookies, get_jwt
)
from app.models.student import Student
from app.models.company import Company

class AuthMiddleware:
    """Middleware para autenticação e autorização segura"""
    
    @staticmethod
    def validate_user_exists(user_id, user_type):
        """Valida se o usuário ainda existe e está ativo"""
        if user_type == 'student':
            user = Student.query.get(user_id)
            return user and user.is_active
        elif user_type == 'company':
            user = Company.query.get(user_id)
            return user and user.is_active
        return False
    
    @staticmethod
    def get_user_data(user_id, user_type):
        """Retorna dados do usuário"""
        if user_type == 'student':
            return Student.query.get(user_id)
        elif user_type == 'company':
            return Company.query.get(user_id)
        return None

def auth_required(allowed_types=None):
    """
    Decorator para autenticação obrigatória
    
    Args:
        allowed_types: Lista de tipos permitidos ['student', 'company'] ou None para ambos
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                # Obter identity (string) e claims (dados do usuário)
                identity = get_jwt_identity()
                claims = get_jwt()
                
                if not identity or not claims:
                    return jsonify({'error': 'Token de autenticação inválido'}), 401
                
                # Extrair dados do usuário dos claims
                user_type = claims.get('type')
                user_id = claims.get('user_id')
                user_email = claims.get('email')
                
                if not user_type or not user_id:
                    return jsonify({'error': 'Token de autenticação malformado'}), 401
                
                # Verificar se o tipo de usuário é permitido
                if allowed_types and user_type not in allowed_types:
                    allowed_str = ', '.join(allowed_types)
                    return jsonify({'error': f'Acesso restrito a: {allowed_str}'}), 403
                
                # Verificar se o usuário ainda existe e está ativo
                if not AuthMiddleware.validate_user_exists(user_id, user_type):
                    return jsonify({'error': 'Conta inválida ou inativa'}), 403
                
                # Criar objeto current_user compatível com o código existente
                current_user = {
                    'id': user_id,
                    'email': user_email,
                    'type': user_type
                }
                
                # Adicionar dados do usuário ao contexto da requisição
                kwargs['current_user'] = current_user
                kwargs['user_data'] = AuthMiddleware.get_user_data(user_id, user_type)
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Erro na autenticação: {str(e)}")
                return jsonify({'error': 'Erro interno de autenticação'}), 500
                
        return decorated_function
    return decorator

def student_required(f):
    """Decorator específico para estudantes"""
    return auth_required(['student'])(f)

def company_required(f):
    """Decorator específico para empresas"""
    return auth_required(['company'])(f)

def student_or_company_required(f):
    """Decorator para estudantes OU empresas"""
    return auth_required(['student', 'company'])(f)

def refresh_token_if_needed():
    """
    Middleware para renovar token automaticamente se necessário
    Deve ser chamado antes de operações que precisam de token válido
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verificar se o token atual é válido
                verify_jwt_in_request()
                return f(*args, **kwargs)
                
            except Exception:
                # Se o token expirou, tentar renovar com refresh token
                try:
                    from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
                    from flask import make_response
                    
                    # Usar refresh token para gerar novo access token
                    verify_jwt_in_request(refresh=True)
                    identity = get_jwt_identity()
                    claims = get_jwt()
                    
                    if identity and claims:
                        # Validar se usuário ainda existe
                        user_type = claims.get('type')
                        user_id = claims.get('user_id')
                        
                        if AuthMiddleware.validate_user_exists(user_id, user_type):
                            # Criar novo access token com nova estrutura
                            user_identity = f"{user_type}:{user_id}"
                            new_token = create_access_token(
                                identity=user_identity,
                                additional_claims={
                                    'user_id': user_id,
                                    'email': claims.get('email'),
                                    'type': user_type
                                }
                            )
                            
                            # Executar função original
                            response = make_response(f(*args, **kwargs))
                            
                            # Definir novo cookie de access token
                            set_access_cookies(response, new_token)
                            
                            return response
                
                except Exception as refresh_error:
                    current_app.logger.error(f"Erro ao renovar token: {str(refresh_error)}")
                    return jsonify({'error': 'Token expirado. Faça login novamente'}), 401
                
                return jsonify({'error': 'Token inválido'}), 401
                
        return decorated_function
    return decorator
