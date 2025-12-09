"""
修改日志API接口
提供查询修改日志的功能
"""
from flask import jsonify
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import ModificationLog, db

def get_all_modification_logs():
    """
    获取所有修改日志记录
    
    Returns:
        list: 包含所有修改日志记录的列表
    """
    try:
        # 查询所有修改日志记录，按操作时间倒序排列
        logs = ModificationLog.query.order_by(ModificationLog.operation_time.desc()).all()
        
        # 将记录转换为字典列表
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'table_name': log.table_name,
                'record_id': log.record_id,
                'operation_type': log.operation_type,
                'old_data': log.old_data,
                'new_data': log.new_data,
                'user_id': log.user_id,
                'username': log.username,
                'operation_time': log.operation_time.isoformat() if log.operation_time else None
            })
        
        return result
    except Exception as e:
        print(f"获取修改日志时出错: {e}")
        return []

def get_modification_logs_by_record(table_name, record_id):
    """
    根据表名和记录ID获取修改日志
    
    Args:
        table_name (str): 表名
        record_id (int): 记录ID
        
    Returns:
        list: 包含指定记录修改日志的列表
    """
    try:
        # 查询指定记录的所有修改日志，按操作时间倒序排列
        logs = ModificationLog.query.filter_by(
            table_name=table_name, 
            record_id=record_id
        ).order_by(ModificationLog.operation_time.desc()).all()
        
        # 将记录转换为字典列表
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'table_name': log.table_name,
                'record_id': log.record_id,
                'operation_type': log.operation_type,
                'old_data': log.old_data,
                'new_data': log.new_data,
                'user_id': log.user_id,
                'username': log.username,
                'operation_time': log.operation_time.isoformat() if log.operation_time else None
            })
        
        return result
    except Exception as e:
        print(f"获取修改日志时出错: {e}")
        return []