from app import create_app, db
from flask_migrate import Migrate
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
env_prod_path = Path(__file__).parent / '.env.production'

print(f" Arquivo .env existe: {env_path.exists()}")
print(f" Arquivo .env.production existe: {env_prod_path.exists()}")

# Carregar .env primeiro
if env_path.exists():
    load_dotenv(env_path)
    print(f" Carregado .env - FLASK_ENV: {os.getenv('FLASK_ENV')}")

# Se estiver em produção, carregar .env.production por cima
if os.getenv('FLASK_ENV') == 'production' and env_prod_path.exists():
    load_dotenv(env_prod_path, override=True)
    print(f" Carregado .env.production - MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")

print(f"FINAL - MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"FINAL - MAIL_APP_PASSWORD: {'***' if os.getenv('MAIL_APP_PASSWORD') else 'None'}")

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=False, port=5000)