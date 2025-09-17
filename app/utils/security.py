# utils/security.py
import bcrypt

def hash_password(password):
    """EI VONLINDE AQUI É PRA IMPLEMENTAR AS API"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """EI VONLINDE AQUI É PRA IMPLEMENTAR AS API"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))