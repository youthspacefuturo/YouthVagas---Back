from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    
    # Configuração para produção ou desenvolvimento
    environment = os.environ.get('FLASK_ENV', 'development')
    
    if environment == 'production':
        # Configuração para produção no VPS Hostinger
        app.run(
            host='0.0.0.0',  # Aceita conexões de qualquer IP
            port=int(os.environ.get('PORT', 5000)),  # Porta configurável via env
            debug=False,  # Debug desabilitado em produção
            threaded=True  # Suporte a múltiplas threads
        )
    else:
        # Configuração para desenvolvimento local
        app.run(
            host='127.0.0.1',  # Apenas localhost
            port=5000,
            debug=True
        )