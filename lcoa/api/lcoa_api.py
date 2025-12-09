"""
LCOA表数据接口
提供读取LCOA表全部数据的功能
"""
from flask import jsonify
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import Lcoa, db

def get_max_lcoa_id():
    """
    获取LCOA表中的最大ID值
    
    Returns:
        int: 最大ID值，如果没有记录则返回0
    """
    try:
        # 查询最大ID值
        max_id_record = db.session.query(db.func.max(Lcoa.id)).scalar()
        return max_id_record if max_id_record is not None else 0
    except Exception as e:
        print(f"获取LCOA最大ID时出错: {e}")
        return 0

def get_all_lcoa_data():
    """
    获取LCOA表中的所有数据
    
    Returns:
        list: 包含所有LCOA记录的列表
    """
    try:
        # 查询所有记录
        lcoa_records = Lcoa.query.all()
        
        # 将记录转换为字典列表
        result = []
        for record in lcoa_records:
            result.append({
                'id': record.id,  # 修复：使用实际的记录ID
                'process_id': record.process_id,  # 添加流程ID字段
                'processNode': record.process_node_id,
                'Title': record.process_title,
                'processType': record.process_type,
                'Department': record.department,
                'Club': record.branch,
                'name_process': record.process_name,
                'user_Name': record.node_operator,
                'Status': record.node_operation_type,
                'Process_Name': record.process_name,
                'start_time': record.first_receive_time,
                'final_time': record.last_process_time,
                'inter_time': record.total_duration,
                'import_date': record.extracted_date,
                'created_at': record.first_receive_time,
                'updated_at': record.last_process_time
            })
        
        return result
    except Exception as e:
        print(f"获取LCOA数据时出错: {e}")
        return []