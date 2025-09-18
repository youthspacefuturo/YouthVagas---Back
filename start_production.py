#!/usr/bin/env python3
"""
Script de inicialização para produção no VPS Hostinger
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def setup_production_environment():
    """Configura o ambiente de produção"""
    
    # Carrega variáveis do .env.production
    env_production = Path(__file__).parent / '.env.production'
    if env_production.exists():
        load_dotenv(env_production)
        print(f"✅ Carregado arquivo de configuração: {env_production}")
    else:
        print(f"⚠️ Arquivo .env.production não encontrado em {env_production}")
        print("📝 Usando variáveis de ambiente do sistema")
    
    # Força ambiente de produção
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    print("🚀 Configurando ambiente de produção...")
    print(f"📍 Diretório atual: {Path.cwd()}")
    print(f"🐍 Python: {sys.version}")
    print(f"🌍 FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"🔧 DEBUG: {os.environ.get('FLASK_DEBUG')}")
    print(f"🗄️ DATABASE: {'MySQL' if os.environ.get('USE_MYSQL') == 'true' else 'SQLite'}")
    
    return True

def start_application():
    """Inicia a aplicação Flask"""
    try:
        from app import create_app
        
        app = create_app()
        
        # Configurações do servidor
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        
        print(f"🌐 Iniciando servidor em {host}:{port}")
        print("🔒 Modo produção: SSL/HTTPS recomendado")
        print("📡 Servidor pronto para receber conexões...")
        
        # Inicia o servidor
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False  # Desabilita reloader em produção
        )
        
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 50)
    print("🏢 YOUTH SPACE - SERVIDOR DE PRODUÇÃO")
    print("=" * 50)
    
    # Configura ambiente
    if setup_production_environment():
        # Inicia aplicação
        start_application()
    else:
        print("❌ Falha na configuração do ambiente")
        sys.exit(1)
