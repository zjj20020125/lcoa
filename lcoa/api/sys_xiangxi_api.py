"""
SysXiangxi表数据接口
提供读取SysXiangxi表全部数据的功能
"""
from flask import jsonify
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import SysXiangxi, db

def get_all_sys_xiangxi_data():
    """
    获取SysXiangxi表中的所有数据
    
    Returns:
        list: 包含所有SysXiangxi记录的列表
    """
    try:
        # 查询所有记录
        sys_xiangxi_records = SysXiangxi.query.all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_xiangxi_records:
            result.append({
                'id': record.id,
                'extracted_date': record.extracted_date,
                'node_operator': record.node_operator,
                'department': record.department,
                'node_operation_type': record.node_operation_type,
                'quantity': record.quantity
            })
        
        return result
    except Exception as e:
        print(f"获取SysXiangxi数据时出错: {e}")
        return []