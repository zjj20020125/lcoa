"""
工具模块
提供JWT token生成和验证等功能
"""
import jwt
from datetime import datetime, timedelta

def generate_token(secret_key, user_id, username, role):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)  # token 24小时过期
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def verify_token(secret_key, token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # token已过期
    except jwt.InvalidTokenError:
        return None  # token无效