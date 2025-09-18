from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    # Configuração CORS para produção
    if os.environ.get('FLASK_ENV') == 'production':
        # Permitir apenas IPs/domínios específicos
        CORS(app, 
             origins=[
                 "http://31.97.17.104",
                 "https://31.97.17.104",
                 "http://localhost:3000",  # Para desenvolvimento
             ],
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        )
    else:
        # Desenvolvimento - mais permissivo
        CORS(app, supports_credentials=True)
    
    return app