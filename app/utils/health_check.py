#!/usr/bin/env python3
"""
Script de verificação de saúde para o Youth Space Backend
Verifica se todos os componentes estão funcionando corretamente
"""
import os
import sys
import requests
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import time

def load_environment():
    """Carrega variáveis de ambiente"""
    env_file = Path(__file__).parent / '.env.production'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Carregado: {env_file}")
    else:
        load_dotenv()
        print("⚠️ Usando .env padrão")

def check_database():
    """Verifica conexão com MySQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            return False, "DATABASE_URL não configurada"
        
        # Parse da URL do MySQL
        # mysql://user:pass@host/db
        if database_url.startswith('mysql://'):
            url_parts = database_url.replace('mysql://', '').split('/')
            db_name = url_parts[1] if len(url_parts) > 1 else None
            host_parts = url_parts[0].split('@')
            host = host_parts[1] if len(host_parts) > 1 else 'localhost'
            user_pass = host_parts[0].split(':')
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ''
            
            # Testa conexão
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return True, f"MySQL conectado: {host}/{db_name}"
        else:
            return False, "Formato de URL MySQL inválido"
            
    except Exception as e:
        return False, f"Erro MySQL: {str(e)}"

def check_api_server(port=5000):
    """Verifica se o servidor API está respondendo"""
    try:
        url = f"http://localhost:{port}/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return True, f"API respondendo: {data.get('message', 'OK')}"
        else:
            return False, f"API retornou status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return False, "API não está rodando ou não acessível"
    except Exception as e:
        return False, f"Erro ao testar API: {str(e)}"

def check_environment_vars():
    """Verifica variáveis de ambiente essenciais"""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'FLASK_ENV'
    ]
    
    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        return False, f"Variáveis faltando: {', '.join(missing)}"
    else:
        return True, "Todas as variáveis essenciais configuradas"

def check_cors_config():
    """Verifica configuração CORS"""
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '')
    
    if not allowed_origins:
        return False, "ALLOWED_ORIGINS não configurada"
    
    origins = [o.strip() for o in allowed_origins.split(',') if o.strip()]
    
    if not origins:
        return False, "ALLOWED_ORIGINS vazia"
    
    return True, f"CORS configurado para: {', '.join(origins)}"

def main():
    """Executa todas as verificações"""
    print("=" * 60)
    print("🏥 YOUTH SPACE - VERIFICAÇÃO DE SAÚDE")
    print("=" * 60)
    
    # Carrega ambiente
    load_environment()
    
    checks = [
        ("🔧 Variáveis de Ambiente", check_environment_vars),
        ("🗄️ Conexão MySQL", check_database),
        ("🌐 Configuração CORS", check_cors_config),
        ("🚀 Servidor API", lambda: check_api_server(int(os.environ.get('PORT', 5000))))
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            success, message = check_func()
            status = "✅ OK" if success else "❌ ERRO"
            print(f"  {status}: {message}")
            results.append(success)
        except Exception as e:
            print(f"  ❌ ERRO: {str(e)}")
            results.append(False)
    
    # Resumo
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 TODOS OS TESTES PASSARAM ({passed}/{total})")
        print("✅ Sistema pronto para produção!")
        return 0
    else:
        print(f"⚠️ ALGUNS TESTES FALHARAM ({passed}/{total})")
        print("❌ Corrija os problemas antes de usar em produção")
        return 1

if __name__ == '__main__':
    sys.exit(main())
