#!/usr/bin/env python3
"""
WSGI entry point para produção com Gunicorn
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente para produção
env_production = Path(__file__).parent / '.env.production'
if env_production.exists():
    load_dotenv(env_production)

# Força ambiente de produção
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Importa e cria a aplicação
from app import create_app

application = create_app()

if __name__ == "__main__":
    # Para desenvolvimento direto (não recomendado em produção)
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
