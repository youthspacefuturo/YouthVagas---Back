import os
from app import create_app

if __name__ == '__main__':
    # Configurar para desenvolvimento
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Criar a aplicação usando a factory function do app/__init__.py
    app = create_app()
    
    print("🚀 Iniciando YouthSpace API em modo desenvolvimento...")
    print("📍 API disponível em: http://localhost:5000")
    print("🌐 Frontend deve apontar para: http://localhost:5000/api")
    print("🔧 Modo DEBUG ativado")
    
    # Executar em modo desenvolvimento
    app.run(
        host='0.0.0.0',  # Aceitar conexões de qualquer IP
        port=5000,       # Porta padrão do Flask
        debug=True,      # Modo debug ativado
        threaded=True    # Suporte a múltiplas threads
    )