import re

def validate_email(email):
    """Validar formato de email com verificações adicionais"""
    if not email or not isinstance(email, str):
        return False
    
    # Remover espaços em branco
    email = email.strip()
    
    # Verificar comprimento
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    # Regex melhorado para email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        return False
    
    # Verificações adicionais de segurança
    # Não permitir múltiplos pontos consecutivos
    if '..' in email:
        return False
    
    # Verificar se não começa ou termina com ponto
    local_part = email.split('@')[0]
    if local_part.startswith('.') or local_part.endswith('.'):
        return False
    
    return True

def validate_password_strength(password):
    """Validar força da senha com critérios de segurança"""
    if not password or not isinstance(password, str):
        return False
    
    # Comprimento mínimo
    if len(password) < 8:
        return False
    
    # Máximo razoável (evitar DoS)
    if len(password) > 128:
        return False
    
    # Verificar critérios
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>_+=\-\[\]\\;/`~]', password))
    
    # Pelo menos 3 dos 4 critérios (flexibilidade)
    criteria_met = sum([has_upper, has_lower, has_digit, has_special])
    
    if criteria_met < 3:
        return False
    
    # Verificar padrões fracos comuns
    weak_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'abc123',
        r'admin',
        r'letmein'
    ]
    
    password_lower = password.lower()
    for pattern in weak_patterns:
        if pattern in password_lower:
            return False
    
    return True

def validate_name(name):
    """Validar nome com verificações de segurança"""
    if not name or not isinstance(name, str):
        return False
    
    # Remover espaços extras
    name = name.strip()
    
    # Verificar comprimento
    if len(name) < 2 or len(name) > 100:
        return False
    
    # Permitir apenas letras, espaços, hífens e apostrofes
    # Inclui caracteres acentuados
    name_regex = r'^[a-zA-ZÀ-ÿĀ-žА-я\s\-\'\.]+$'
    
    if not re.match(name_regex, name):
        return False
    
    # Não permitir apenas espaços ou caracteres especiais
    if not re.search(r'[a-zA-ZÀ-ÿĀ-žА-я]', name):
        return False
    
    # Não permitir múltiplos espaços consecutivos
    if re.search(r'\s{2,}', name):
        return False
    
    return True

def validate_phone(phone):
    """Validar número de telefone brasileiro"""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remover caracteres não numéricos
    phone_clean = re.sub(r'\D', '', phone)
    
    # Verificar comprimento (10 ou 11 dígitos)
    if len(phone_clean) not in [10, 11]:
        return False
    
    # Verificar padrões brasileiros
    # Celular: 11 dígitos começando com DDD + 9 + número
    # Fixo: 10 dígitos começando com DDD + número
    
    if len(phone_clean) == 11:
        # Celular: (11) 9XXXX-XXXX
        if not phone_clean[2] == '9':
            return False
    
    # Verificar se DDD é válido (códigos brasileiros)
    ddd = phone_clean[:2]
    valid_ddds = [
        '11', '12', '13', '14', '15', '16', '17', '18', '19',  # SP
        '21', '22', '24',  # RJ
        '27', '28',  # ES
        '31', '32', '33', '34', '35', '37', '38',  # MG
        '41', '42', '43', '44', '45', '46',  # PR
        '47', '48', '49',  # SC
        '51', '53', '54', '55',  # RS
        '61',  # DF
        '62', '64',  # GO
        '63',  # TO
        '65', '66',  # MT
        '67',  # MS
        '68',  # AC
        '69',  # RO
        '71', '73', '74', '75', '77',  # BA
        '79',  # SE
        '81', '87',  # PE
        '82',  # AL
        '83',  # PB
        '84',  # RN
        '85', '88',  # CE
        '86', '89',  # PI
        '91', '93', '94',  # PA
        '92', '97',  # AM
        '95',  # RR
        '96',  # AP
        '98', '99'   # MA
    ]
    
    return ddd in valid_ddds

def validate_cpf(cpf):
    """Validar CPF brasileiro"""
    if not cpf or not isinstance(cpf, str):
        return False
    
    # Remover caracteres não numéricos
    cpf_clean = re.sub(r'\D', '', cpf)
    
    # Verificar comprimento
    if len(cpf_clean) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais (inválido)
    if cpf_clean == cpf_clean[0] * 11:
        return False
    
    # Validar dígitos verificadores
    def calculate_digit(cpf_partial, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Primeiro dígito verificador
    weights1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = calculate_digit(cpf_clean[:9], weights1)
    
    if int(cpf_clean[9]) != digit1:
        return False
    
    # Segundo dígito verificador
    weights2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    digit2 = calculate_digit(cpf_clean[:10], weights2)
    
    return int(cpf_clean[10]) == digit2

def validate_cnpj(cnpj):
    """Validar CNPJ brasileiro"""
    if not cnpj or not isinstance(cnpj, str):
        return False
    
    # Remover caracteres não numéricos
    cnpj_clean = re.sub(r'\D', '', cnpj)
    
    # Verificar comprimento
    if len(cnpj_clean) != 14:
        return False
    
    # Verificar se todos os dígitos são iguais (inválido)
    if cnpj_clean == cnpj_clean[0] * 14:
        return False
    
    # Validar dígitos verificadores
    def calculate_cnpj_digit(cnpj_partial, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    # Primeiro dígito verificador
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digit1 = calculate_cnpj_digit(cnpj_clean[:12], weights1)
    
    if int(cnpj_clean[12]) != digit1:
        return False
    
    # Segundo dígito verificador
    weights2 = [6, 7, 8, 9, 2, 3, 4, 5, 6, 7, 8, 9]
    digit2 = calculate_cnpj_digit(cnpj_clean[:13], weights2)
    
    return int(cnpj_clean[13]) == digit2

def validate_not_empty(value, field_name):
    """Validar se campo não está vazio"""
    if value is None:
        raise ValueError(f"{field_name} é obrigatório")
    
    if isinstance(value, str) and not value.strip():
        raise ValueError(f"{field_name} não pode estar vazio")
    
    return True

def sanitize_input(value):
    """Sanitizar input para prevenir XSS básico"""
    if not isinstance(value, str):
        return value
    
    # Remover tags HTML básicas
    value = re.sub(r'<[^>]+>', '', value)
    
    # Remover scripts
    value = re.sub(r'<script.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
    
    # Limitar tamanho para prevenir DoS
    if len(value) > 10000:
        value = value[:10000]
    
    return value.strip()

def validate_url(url):
    """Validar URL"""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # Regex para URL
    url_regex = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    
    return bool(re.match(url_regex, url)) and len(url) <= 2000