"""
SysClub表数据接口
提供读取SysClub表全部数据的功能
"""
from flask import jsonify
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import SysClub, db

def get_all_sys_club_data():
    """
    获取SysClub表中的所有数据
    
    Returns:
        list: 包含所有SysClub记录的列表
    """
    try:
        # 查询所有记录
        sys_club_records = SysClub.query.all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_club_records:
            result.append({
                'id': record.id,
                'extracted_date': record.extracted_date,
                'department': record.department,
                'personnel_count': record.personnel_count,
                'timeout_count': record.timeout_count
            })
        
        return result
    except Exception as e:
        print(f"获取SysClub数据时出错: {e}")
        return []
