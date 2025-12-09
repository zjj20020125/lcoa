"""
SysNodeal表数据接口
提供读取SysNodeal表全部数据的功能
"""
from flask import jsonify
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import SysNodeal, db

def get_all_sys_nodeal_data():
    """
    获取SysNodeal表中的所有数据，按ID倒序排列
    
    Returns:
        list: 包含所有SysNodeal记录的列表，按ID倒序排列
    """
    try:
        # 查询所有记录，按ID倒序排列
        sys_nodeal_records = SysNodeal.query.order_by(SysNodeal.id.desc()).all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_nodeal_records:
            result.append({
                'id': record.id,
                'extracted_date': record.extracted_date,
                'process_node_id': record.process_node_id,
                'process_id': record.process_id,
                'process_title': record.process_title,
                'process_name': record.process_name,
                'process_type': record.process_type,
                'branch': record.branch,
                'department': record.department,
                'node_operator': record.node_operator,
                'node_operation_type': record.node_operation_type,
                'node_name': record.node_name,
                'first_receive_time': record.first_receive_time,
                'last_process_time': record.last_process_time,
                'total_duration': record.total_duration,
                'total_timeout': record.total_timeout
            })
        
        return result
    except Exception as e:
        print(f"获取SysNodeal数据时出错: {e}")
        return []