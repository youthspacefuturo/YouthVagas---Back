from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
print(f"DEBUG: Carregando .env de: {env_path}")
print(f"DEBUG: Arquivo .env existe: {env_path.exists()}")
load_dotenv(env_path)

# Debug das variáveis carregadas
print("=== DEBUG VARIÁVEIS CARREGADAS ===")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:50] if os.getenv('DATABASE_URL') else 'None'}...")
print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"MAIL_APP_PASSWORD: {'***' if os.getenv('MAIL_APP_PASSWORD') else 'None'}")
print("==================================")

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados - MySQL como padrão
    database_url = os.environ.get('DATABASE_URL')
    use_mysql = os.environ.get('USE_MYSQL', 'true').lower() == 'true'
    
    if use_mysql and database_url:
        # Usar MySQL
        try:
            import pymysql
            # Convert standard MySQL URL to SQLAlchemy format
            if database_url.startswith('mysql://'):
                # Convert mysql:// to mysql+pymysql://
                sqlalchemy_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
                app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_url
                print(f"🔗 Configured for MySQL: {database_url.split('@')[1] if '@' in database_url else 'MySQL'}")
            elif database_url.startswith('mysql+pymysql://'):
                app.config['SQLALCHEMY_DATABASE_URI'] = database_url
                print(f"🔗 Configured for MySQL: {database_url.split('@')[1] if '@' in database_url else 'MySQL'}")
            else:
                raise ValueError("Invalid MySQL URL format")
        except (ImportError, ValueError) as e:
            print(f"⚠️ MySQL configuration failed: {e}")
            print("🔄 Falling back to SQLite for development")
            use_mysql = False
    
    if not use_mysql:
        # Fallback para SQLite
        base_dir = Path(__file__).parent.parent
        instance_path = base_dir / 'instance'
        instance_path.mkdir(exist_ok=True)
        db_path = instance_path / 'app.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        print(f"💾 Using SQLite: {db_path}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'youth-space')
    
    # Configuração de ambiente
    flask_env = os.environ.get('FLASK_ENV', 'development')
    is_production = flask_env == 'production'
    
    app.config['DEBUG'] = not is_production
    app.config['SQLALCHEMY_ECHO'] = not is_production  # Desabilita logs SQL em produção
    
    # Enable debug mode for development
    if app.config['DEBUG']:
        print("DEBUG MODE ENABLED - JWT Cookie debugging active")
    else:
        print("PRODUCTION MODE - Debug disabled")

    # Configurações de sessão (mantidas, mas podem ser opcionais com JWT)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'youth-space:'

    # Configurações JWT para cookies seguros
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'seu_segredo_jwt_muito_seguro')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    # Expiração dos tokens
    # Access token curto: 30 minutos
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
    # Refresh token médio: 7 dias
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    
    # Configurações de cookies seguros baseadas no ambiente
    if is_production:
        # Configurações seguras para produção
        app.config['JWT_COOKIE_SECURE'] = False  # HTTPS obrigatório
        app.config['JWT_COOKIE_HTTPONLY'] = True
        app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
        app.config['JWT_COOKIE_DOMAIN'] = None  # Domínio específico
        app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # CSRF habilitado
    else:
        # Configurações para desenvolvimento
        app.config['JWT_COOKIE_SECURE'] = False  # False para localhost HTTP
        app.config['JWT_COOKIE_HTTPONLY'] = True
        app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
        app.config['JWT_COOKIE_DOMAIN'] = None  # Permitir localhost
        app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # CSRF desabilitado
    
    app.config['JWT_COOKIE_PATH'] = '/'
    # Fazer com que o cookie tenha Max-Age/Expires (não somente cookie de sessão)
    app.config['JWT_SESSION_COOKIE'] = False
    
    # Nomes dos cookies
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Configuração CORS baseada no ambiente
    if is_production:
        # CORS para produção - domínios específicos
        allowed_origins = os.environ.get('ALLOWED_ORIGINS', '').split(',')
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
        
        CORS(app, 
             supports_credentials=True, 
             origins=["http://31.97.17.104:8080", "http://127.0.0.1:8080"],
             allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Cookie", "X-CSRF-TOKEN"],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             expose_headers=["Set-Cookie"],
             allow_credentials=True)
        print(f"🌐 CORS configurado para produção com origens: {allowed_origins}")
    else:
        # CORS para desenvolvimento - localhost
        CORS(app, 
             supports_credentials=True, 
             origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://31.97.17.104:8080", "http://127.0.0.1:8080"],
             allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Cookie", "X-CSRF-TOKEN"],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             expose_headers=["Set-Cookie"],
             allow_credentials=True)
        print("🌐 CORS configurado para desenvolvimento (localhost)")

    # Importar modelos
    with app.app_context():
        from app.models.company import Company
        from app.models.job import Job
        from app.models.student import Student
        from app.models.application import Application

        # Teste de conexão com o banco de dados
        try:
            # Test database connection
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            student_count = db.session.query(Student).count()
            db_type = "MySQL" if use_mysql else "SQLite"
            print(f"✅ Conexão {db_type} bem-sucedida. Número de estudantes: {student_count}")
        except Exception as e:
            db_type = "MySQL" if use_mysql else "SQLite"
            print(f"⚠️ Erro ao conectar ao banco {db_type}: {str(e)}")
            if use_mysql:
                print("💡 Verifique as credenciais do MySQL no .env ou defina USE_MYSQL=false para usar SQLite")

    # Registrar blueprints - ORDEM IMPORTANTE: mais específicos primeiro
    try:
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("auth_bp registrado com sucesso")
    except ImportError as e:
        print(f"Warning: auth_bp não encontrado - {e}")

    # Application blueprint DEVE vir antes do job blueprint para evitar conflitos
    # pois /jobs/<id>/apply é mais específico que /jobs
    try:
        from app.routes.r_application import application_bp
        app.register_blueprint(application_bp, url_prefix='/api')
        print("application_bp registrado com sucesso")
    except ImportError as e:
        print(f"Warning: application_bp não encontrado - {e}")

    try:
        from app.routes.r_job import job_bp
        app.register_blueprint(job_bp, url_prefix='/api')
        print("job_bp registrado com sucesso")
    except ImportError as e:
        print(f"Warning: job_bp não encontrado - {e}")

    try:
        from app.routes.r_company import company_bp
        app.register_blueprint(company_bp, url_prefix='/api')
        print("company_bp registrado com sucesso")
    except ImportError as e:
        print(f"Warning: company_bp não encontrado - {e}")

    try:
        from app.routes.r_student import student_bp
        app.register_blueprint(student_bp, url_prefix='/api')
        print("student_bp registrado com sucesso")
    except ImportError as e:
        print(f"Warning: student_bp não encontrado - {e}")

    # Rota raiz
    @app.route('/')
    def index():
        return {
            "message": "Youth Space API está funcionando!",
            "database_type": "MySQL (Production)",
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "auth_endpoints": [
                "GET /api/auth/ - Informações sobre autenticação",
                "POST /api/auth/register/student - Cadastrar estudante",
                "POST /api/auth/register/company - Cadastrar empresa",
                "POST /api/auth/login/student - Fazer login",
                "POST /api/auth/login/company - Fazer login",
                "POST /api/auth/logout - Fazer logout"
            ],
            "user_endpoints": [
                "GET /api/student/<id> - Obter dados do estudante",
                "PUT /api/student/<id> - Editar dados do estudante", 
                "DELETE /api/student/<id> - Excluir conta"
            ],
            "other_endpoints": [
                "POST /api/jobs - Criar vaga",
                "GET /api/jobs - Obter todas as vagas",
                "GET /api/jobs/<id> - Obter vaga"
            ]
        }

    return app