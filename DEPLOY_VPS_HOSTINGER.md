# 🚀 Deploy do Youth Space Backend no VPS Hostinger Ubuntu

## 📋 Pré-requisitos

### No VPS Hostinger:
- Ubuntu 20.04+ 
- Python 3.8+
- MySQL (já configurado)
- Nginx (recomendado)
- Supervisor (para gerenciar processos)

## 🔧 Configuração no VPS

### 1. Preparar o ambiente

```bash
# Conectar ao VPS
ssh root@seu-ip-vps

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências
apt install python3 python3-pip python3-venv nginx supervisor git -y

# Instalar MySQL client (se necessário)
apt install mysql-client -y
```

### 2. Configurar o projeto

```bash
# Criar diretório para o projeto
mkdir -p /var/www/youthspace
cd /var/www/youthspace

# Clonar ou fazer upload do código
# git clone seu-repositorio backend
# ou fazer upload via SCP/SFTP

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn pymysql
```

### 3. Configurar variáveis de ambiente

```bash
# Copiar e editar arquivo de produção
cp .env.production .env

# Editar com seus dados reais
nano .env
```

**Variáveis importantes para ajustar:**

```env
# Domínios do seu site
ALLOWED_ORIGINS=https://seudominio.com,https://www.seudominio.com

# Domínio para cookies
COOKIE_DOMAIN=seudominio.com

# Porta (pode ser diferente se usar proxy)
PORT=5000

# Chaves de segurança (GERAR NOVAS!)
SECRET_KEY="nova_chave_super_segura_aqui"
JWT_SECRET_KEY="nova_jwt_chave_super_segura_aqui"
```

### 4. Testar a aplicação

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar com Flask development server
python start_production.py

# Ou testar com Gunicorn
gunicorn -c gunicorn.conf.py wsgi:application
```

## 🔄 Configuração do Supervisor

### Criar arquivo de configuração:

```bash
nano /etc/supervisor/conf.d/youthspace.conf
```

```ini
[program:youthspace]
command=/var/www/youthspace/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application
directory=/var/www/youthspace
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/youthspace.log
environment=FLASK_ENV=production
```

### Ativar o serviço:

```bash
# Recarregar configuração
supervisorctl reread
supervisorctl update

# Iniciar serviço
supervisorctl start youthspace

# Verificar status
supervisorctl status youthspace
```

## 🌐 Configuração do Nginx

### Criar configuração do site:

```bash
nano /etc/nginx/sites-available/youthspace
```

```nginx
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;

    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com www.seudominio.com;

    # Certificados SSL (Let's Encrypt recomendado)
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Proxy para a aplicação Flask
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Configurações para cookies
        proxy_cookie_path / /;
        proxy_cookie_domain localhost seudominio.com;
    }

    # Servir frontend (se estiver no mesmo servidor)
    location / {
        root /var/www/youthspace-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Logs
    access_log /var/log/nginx/youthspace_access.log;
    error_log /var/log/nginx/youthspace_error.log;
}
```

### Ativar o site:

```bash
# Criar link simbólico
ln -s /etc/nginx/sites-available/youthspace /etc/nginx/sites-enabled/

# Testar configuração
nginx -t

# Recarregar Nginx
systemctl reload nginx
```

## 🔒 SSL/HTTPS com Let's Encrypt

```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx -y

# Obter certificado
certbot --nginx -d seudominio.com -d www.seudominio.com

# Testar renovação automática
certbot renew --dry-run
```

## 📊 Monitoramento e Logs

### Verificar logs:

```bash
# Logs da aplicação
tail -f /var/log/youthspace.log

# Logs do Supervisor
tail -f /var/log/supervisor/supervisord.log

# Logs do Nginx
tail -f /var/log/nginx/youthspace_access.log
tail -f /var/log/nginx/youthspace_error.log

# Status dos serviços
supervisorctl status
systemctl status nginx
```

### Comandos úteis:

```bash
# Reiniciar aplicação
supervisorctl restart youthspace

# Recarregar Nginx
systemctl reload nginx

# Ver processos
ps aux | grep gunicorn
```

## 🔧 Comandos de Deploy

### Opção 1: Flask Development Server (não recomendado para produção)
```bash
cd /var/www/youthspace
source venv/bin/activate
python start_production.py
```

### Opção 2: Gunicorn (recomendado)
```bash
cd /var/www/youthspace
source venv/bin/activate
gunicorn -c gunicorn.conf.py wsgi:application
```

### Opção 3: Com Supervisor (recomendado para produção)
```bash
supervisorctl start youthspace
```

## 🛠️ Troubleshooting

### Problemas comuns:

1. **Erro de conexão MySQL:**
   - Verificar credenciais no .env
   - Testar conexão: `mysql -h srv1526.hstgr.io -u u155031960_adminYouth -p`

2. **Erro de CORS:**
   - Verificar ALLOWED_ORIGINS no .env
   - Certificar que o domínio está correto

3. **Cookies não funcionam:**
   - Verificar COOKIE_DOMAIN no .env
   - Certificar que está usando HTTPS

4. **Aplicação não inicia:**
   - Verificar logs: `tail -f /var/log/youthspace.log`
   - Verificar porta disponível: `netstat -tlnp | grep :5000`

### Verificar configuração:

```bash
# Testar conectividade
curl -I http://localhost:5000/

# Verificar variáveis de ambiente
env | grep FLASK

# Testar banco de dados
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')
print('DATABASE_URL:', os.environ.get('DATABASE_URL'))
"
```

## 📝 Checklist de Deploy

- [ ] VPS configurado com Python 3.8+
- [ ] Dependências instaladas (requirements.txt)
- [ ] Arquivo .env.production configurado
- [ ] Banco MySQL acessível
- [ ] Gunicorn instalado e configurado
- [ ] Supervisor configurado
- [ ] Nginx configurado
- [ ] SSL/HTTPS configurado
- [ ] CORS configurado para domínio correto
- [ ] Logs funcionando
- [ ] Aplicação acessível via domínio

## 🔄 Atualizações

Para atualizar a aplicação:

```bash
cd /var/www/youthspace
git pull  # ou fazer upload dos novos arquivos
source venv/bin/activate
pip install -r requirements.txt
supervisorctl restart youthspace
```

---

**🎉 Sua aplicação Youth Space estará rodando em produção no VPS Hostinger!**
