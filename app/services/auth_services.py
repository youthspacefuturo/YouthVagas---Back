from app.models.student import Student
from app.models.company import Company
from app.models.reset_code import ResetCode
from app import db
from app.utils.notifications import NotificationService
from app.services.email_send import email_service
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import secrets
import string

class AuthService:
    @staticmethod
    def login_student(email, password):
        """Login para estudantes"""
        student = Student.query.filter_by(email=email, is_active=True).first()
        if not student:
            raise ValueError('Email não encontrado ou conta inativa')
        
        if not student.check_password(password):
            raise ValueError('Senha incorreta')
        
        return student
    
    @staticmethod
    def login_company(email, password):
        """Login para empresas"""
        company = Company.query.filter_by(email=email, is_active=True).first()
        if not company:
            raise ValueError('Email não encontrado ou conta inativa')
        
        if not company.check_password(password):
            raise ValueError('Senha incorreta')
        
        return company
    
    @staticmethod
    def register_student(name, email, password, phone, cpf, github_url=None, resume_url=None):
        """Registrar novo estudante"""
        try:
            from app.services.student_service import StudentService
            
            data = {
                'name': name,
                'email': email,
                'password': password,
                'phone': phone,
                'cpf': cpf,
                'github_url': github_url,
                'resume_url': resume_url
            }
            
            student = StudentService.create_student(data)
            
            # Enviar email de boas-vindas
            try:
                email_service.send_welcome_email(email, name, 'student')
            except Exception as e:
                # Log do erro mas não falha o registro
                print(f"Erro ao enviar email de boas-vindas: {str(e)}")
            
            return student
            
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Email ou CPF já cadastrados')
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Erro ao registrar estudante: {str(e)}')
    
    @staticmethod
    def register_company(name, email, password, phone, cnpj, website=None, sector=None, company_size=None, about=None):
        """Registrar nova empresa"""
        from app.services.company_services import CompanyService
        
        data = {
            'name': name,
            'email': email,
            'password': password,
            'phone': phone,
            'cnpj': cnpj,
            'website': website,
            'sector': sector,
            'company_size': company_size,
            'about': about
        }
        
        company = CompanyService.create_company(data)
        
        # Enviar email de boas-vindas
        try:
            email_service.send_welcome_email(email, name, 'company')
        except Exception as e:
            # Log do erro mas não falha o registro
            print(f"Erro ao enviar email de boas-vindas: {str(e)}")
        
        return company
    
    @staticmethod
    def send_reset_code(email=None, phone=None, method='email'):
        """
        Enviar código de reset de senha
        
        Args:
            email: Email do usuário (se method='email')
            phone: Telefone do usuário (se method='sms')
            method: 'email' ou 'sms'
        """
        try:
            # Determinar tipo de usuário e buscar usuário
            user = None
            user_type = None
            user_name = ""
            
            if method == 'email' and email:
                # Buscar por email em ambas as tabelas
                student = Student.query.filter_by(email=email, is_active=True).first()
                company = Company.query.filter_by(email=email, is_active=True).first()
                
                if student:
                    user = student
                    user_type = 'student'
                    user_name = student.name
                elif company:
                    user = company
                    user_type = 'company'
                    user_name = company.name
                else:
                    raise ValueError('Email não encontrado ou conta inativa')
                    
            elif method == 'sms' and phone:
                # Buscar por telefone em ambas as tabelas
                student = Student.query.filter_by(phone=phone, is_active=True).first()
                company = Company.query.filter_by(phone=phone, is_active=True).first()
                
                if student:
                    user = student
                    user_type = 'student'
                    user_name = student.name
                elif company:
                    user = company
                    user_type = 'company'
                    user_name = company.name
                else:
                    raise ValueError('Telefone não encontrado ou conta inativa')
            else:
                raise ValueError('Email ou telefone é obrigatório')
            
            print(f"DEBUG: Iniciando processo de reset para {email or phone} ({user_type})")
            
            # Invalidar códigos anteriores não utilizados
            if method == 'email':
                old_codes = ResetCode.query.filter_by(
                    email=email, 
                    method=method, 
                    user_type=user_type, 
                    is_used=False
                ).all()
            else:
                old_codes = ResetCode.query.filter_by(
                    phone=phone, 
                    method=method, 
                    user_type=user_type, 
                    is_used=False
                ).all()
            
            print(f"DEBUG: Encontrados {len(old_codes)} códigos antigos para invalidar")
            for old_code in old_codes:
                old_code.is_used = True
            
            # Criar novo código
            reset_code = ResetCode(
                email=email if method == 'email' else None,
                phone=phone if method == 'sms' else None,
                method=method,
                user_type=user_type,
                expires_in_minutes=15
            )
            
            print(f"DEBUG: Código gerado: {reset_code.code}")
            db.session.add(reset_code)
            
            try:
                db.session.commit()
                print(f"DEBUG: Código salvo no banco com sucesso")
            except Exception as e:
                print(f"ERRO: Falha ao salvar no banco: {str(e)}")
                db.session.rollback()
                raise ValueError(f'Erro ao salvar código no banco: {str(e)}')
            
            # Enviar código
            if method == 'email':
                print(f"DEBUG: Tentando enviar email para {email}")
                try:
                    success = email_service.send_reset_password_email(email, user_name, reset_code.code)
                    if success:
                        print(f"SUCCESS: Email enviado com sucesso para {email}")
                    else:
                        print(f"AVISO: Falha ao enviar email para {email}")
                        print(f"CÓDIGO DE RESET (para debug): {reset_code.code}")
                        # Não forçar sucesso - deixar o usuário saber que email falhou
                        # mas código está disponível no console
                except Exception as e:
                    print(f"ERRO EMAIL: {str(e)}")
                    print(f"CÓDIGO DE RESET (para debug): {reset_code.code}")
                    success = False  # Email falhou, mas código está no console
            else:
                formatted_phone = NotificationService.format_phone_number(phone)
                success = NotificationService.send_reset_code_sms(formatted_phone, reset_code.code)
                if not success:
                    raise ValueError(f'Erro ao enviar código por {method}')
            
            # Preparar resposta baseada no sucesso do envio
            if method == 'email':
                if success:
                    message = 'Código enviado para seu email'
                else:
                    message = 'Código gerado com sucesso. Verifique o console do servidor para o código (problema temporário com email)'
            else:
                if success:
                    message = 'Código enviado para seu telefone'
                else:
                    message = 'Erro ao enviar código por SMS'
            
            return {
                'message': message,
                'code_sent': success,
                'expires_at': reset_code.expires_at.isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Erro interno: {str(e)}')
    
    @staticmethod
    def verify_reset_code(code, email=None, phone=None, method='email'):
        """
        Verificar código de reset
        
        Args:
            code: Código de 6 dígitos
            email: Email do usuário (se method='email')
            phone: Telefone do usuário (se method='sms')
            method: 'email' ou 'sms'
        """
        try:
            # Determinar tipo de usuário
            user_type = None
            
            if method == 'email' and email:
                student = Student.query.filter_by(email=email, is_active=True).first()
                company = Company.query.filter_by(email=email, is_active=True).first()
                user_type = 'student' if student else ('company' if company else None)
            elif method == 'sms' and phone:
                student = Student.query.filter_by(phone=phone, is_active=True).first()
                company = Company.query.filter_by(phone=phone, is_active=True).first()
                user_type = 'student' if student else ('company' if company else None)
            
            if not user_type:
                raise ValueError('Usuário não encontrado')
            
            # Buscar código válido
            reset_code = ResetCode.find_valid_code(
                code=code,
                email=email,
                phone=phone,
                method=method,
                user_type=user_type
            )
            
            if not reset_code:
                raise ValueError('Código inválido ou expirado')
            
            # Gerar token temporário para confirmar nova senha
            token = secrets.token_urlsafe(32)
            
            # Marcar código como usado e salvar token
            reset_code.mark_as_used()
            reset_code.set_verification_token(token)
            
            return {
                'message': 'Código verificado com sucesso',
                'valid': True,
                'token': token,
                'user_type': user_type
            }
            
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f'Erro interno: {str(e)}')
    
    @staticmethod
    def confirm_new_password(token, new_password, confirm_password, email=None, phone=None):
        """
        Confirmar nova senha
        
        Args:
            token: Token de verificação
            new_password: Nova senha
            confirm_password: Confirmação da nova senha
            email: Email do usuário (opcional, para validação adicional)
            phone: Telefone do usuário (opcional, para validação adicional)
        """
        try:
            # Validar senhas
            if not new_password or len(new_password) < 6:
                raise ValueError('Senha deve ter pelo menos 6 caracteres')
            
            if new_password != confirm_password:
                raise ValueError('Senhas não coincidem')
            
            # Buscar código de reset pelo token
            reset_code = ResetCode.find_by_token(token)
            if not reset_code:
                raise ValueError('Token inválido ou expirado')
            
            # Buscar usuário baseado nos dados do código de reset
            user = None
            if reset_code.method == 'email' and reset_code.email:
                if reset_code.user_type == 'student':
                    user = Student.query.filter_by(email=reset_code.email, is_active=True).first()
                else:
                    user = Company.query.filter_by(email=reset_code.email, is_active=True).first()
            elif reset_code.method == 'sms' and reset_code.phone:
                if reset_code.user_type == 'student':
                    user = Student.query.filter_by(phone=reset_code.phone, is_active=True).first()
                else:
                    user = Company.query.filter_by(phone=reset_code.phone, is_active=True).first()
            
            if not user:
                raise ValueError('Usuário não encontrado')
            
            # Atualizar senha
            user.set_password(new_password)
            
            # Invalidar o código de reset após uso bem-sucedido
            db.session.delete(reset_code)
            db.session.commit()
            
            return {
                'message': 'Senha redefinida com sucesso',
                'success': True
            }
            
        except ValueError:
            raise
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'Erro interno: {str(e)}')
    
    @staticmethod
    def cleanup_expired_codes():
        """Limpar códigos expirados (executar periodicamente)"""
        return ResetCode.cleanup_expired()