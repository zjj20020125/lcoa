"""
修改日志记录工具
用于记录数据库表的修改操作，以便后续查看、复原和追责
"""
import json
from datetime import datetime
from flask import g
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, ModificationLog
import traceback

def log_modification(table_name, record_id, operation_type, old_data=None, new_data=None, user_id=None, username=None):
    """
    记录数据库修改操作
    
    Args:
        table_name (str): 表名
        record_id (int): 记录ID
        operation_type (str): 操作类型 (INSERT, UPDATE, DELETE)
        old_data (dict): 修改前的数据
        new_data (dict): 修改后的数据
        user_id (int): 操作用户ID
        username (str): 操作用户名称
    """
    try:
        # 创建修改日志记录
        log_entry = ModificationLog(
            table_name=table_name,
            record_id=record_id,
            operation_type=operation_type,
            old_data=json.dumps(old_data, ensure_ascii=False) if old_data else None,
            new_data=json.dumps(new_data, ensure_ascii=False) if new_data else None,
            user_id=user_id,
            username=username,
            operation_time=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        print(f"修改日志记录成功: {table_name}:{record_id}:{operation_type}")
    except Exception as e:
        db.session.rollback()
        print(f"记录修改日志时出错: {e}")
        traceback.print_exc()

def get_current_user_info():
    """
    获取当前用户信息
    """
    try:
        # 尝试从Flask的g对象获取用户信息
        if hasattr(g, 'user') and g.user:
            return g.user.get('id'), g.user.get('username')
        return None, None
    except Exception as e:
        print(f"获取当前用户信息时出错: {e}")
        traceback.print_exc()
        return None, None

def log_insert(table_name, record_id, new_data):
    """
    记录插入操作
    
    Args:
        table_name (str): 表名
        record_id (int): 记录ID
        new_data (dict): 新插入的数据
    """
    try:
        user_id, username = get_current_user_info()
        log_modification(table_name, record_id, 'INSERT', new_data=new_data, user_id=user_id, username=username)
    except Exception as e:
        print(f"记录插入操作时出错: {e}")
        traceback.print_exc()

def log_update(table_name, record_id, old_data, new_data):
    """
    记录更新操作
    
    Args:
        table_name (str): 表名
        record_id (int): 记录ID
        old_data (dict): 修改前的数据
        new_data (dict): 修改后的数据
    """
    try:
        user_id, username = get_current_user_info()
        log_modification(table_name, record_id, 'UPDATE', old_data=old_data, new_data=new_data, user_id=user_id, username=username)
    except Exception as e:
        print(f"记录更新操作时出错: {e}")
        traceback.print_exc()

def log_delete(table_name, record_id, old_data):
    """
    记录删除操作
    
    Args:
        table_name (str): 表名
        record_id (int): 记录ID
        old_data (dict): 删除前的数据
    """
    try:
        user_id, username = get_current_user_info()
        log_modification(table_name, record_id, 'DELETE', old_data=old_data, user_id=user_id, username=username)
    except Exception as e:
        print(f"记录删除操作时出错: {e}")
        traceback.print_exc()