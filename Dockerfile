FROM python:3.12-slim

# Configurações básicas do Python


# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DATABASE_URL=mysql://u155031960_adminYouth:YouthV4g4s!!yV@srv1526.hstgr.io/u155031960_YouthVagas
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False

# Database Configuration (MySQL Produção)
ENV USE_MYSQL=true

# Database Performance Configuration (produção)

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/instance /app/logs

# Expor porta
EXPOSE 5000

# Health check simples
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/auth || exit 1

# Comando padrão
CMD ["python", "run.py"]
