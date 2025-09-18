# Configuração do Gunicorn para produção no VPS Hostinger
import os
import multiprocessing

# Configurações do servidor
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = multiprocessing.cpu_count() * 2 + 1  # Fórmula recomendada
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Configurações de processo
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Configurações de log
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações SSL (se usar HTTPS direto no Gunicorn)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"

# Hook de inicialização
def on_starting(server):
    server.log.info("🚀 Youth Space API iniciando...")

def on_reload(server):
    server.log.info("🔄 Youth Space API recarregando...")

def worker_int(worker):
    worker.log.info("🛑 Worker interrompido pelo usuário")

def pre_fork(server, worker):
    server.log.info(f"👷 Worker {worker.pid} iniciando...")

def post_fork(server, worker):
    server.log.info(f"✅ Worker {worker.pid} pronto")

def worker_abort(worker):
    worker.log.info(f"❌ Worker {worker.pid} abortado")

# Configurações específicas para VPS
if os.environ.get('FLASK_ENV') == 'production':
    # Produção: mais workers, menos logs
    workers = min(workers, 4)  # Limita workers em VPS pequenos
    loglevel = "warning"
    preload_app = True
else:
    # Desenvolvimento: menos workers, mais logs
    workers = 1
    loglevel = "debug"
    reload = True
