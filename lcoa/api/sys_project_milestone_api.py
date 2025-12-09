"""
SysProjectMilestone表数据接口
提供读取SysProjectMilestone表全部数据的功能
"""
from flask import jsonify
# 使用绝对导入而不是相对导入
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from models import SysProjectMilestone, SysProject, SysProjectMilestoneImpactHistory, db

# 修复utils导入
sys.path.append(project_root)
try:
    from utils.modification_logger import log_update
except ImportError:
    # 如果上面的方式失败，尝试直接导入
    try:
        from modification_logger import log_update
    except ImportError:
        # 使用完整路径导入
        utils_path = os.path.join(project_root, 'utils')
        sys.path.append(utils_path)
        from modification_logger import log_update

def get_all_sys_project_milestone_data():
    """
    获取SysProjectMilestone表中的所有数据
    
    Returns:
        list: 包含所有SysProjectMilestone记录的列表
    """
    try:
        # 查询所有记录
        sys_project_milestone_records = SysProjectMilestone.query.all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_project_milestone_records:
            result.append({
                'id': record.id,
                'project_id': record.project_id,
                'milestone': record.milestone,
                'responsible_department': record.responsible_department,
                'planned_start_time': record.planned_start_time,
                'planned_end_time': record.planned_end_time,
                'actual_completion_time': record.actual_completion_time,
                'responsible_person': record.responsible_person,
                'exception_type': record.exception_type,
                'impact_cycle': record.impact_cycle,
                'response_measures': record.response_measures,
                'modification_log': record.modification_log,
                'created_at': record.created_at.isoformat() if record.created_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None
            })
        
        return result
    except Exception as e:
        print(f"获取SysProjectMilestone数据时出错: {e}")
        return []


def update_sys_project_milestone(milestone_id, data):
    """
    更新SysProjectMilestone表中的指定记录
    
    Args:
        milestone_id (int): 里程碑记录的ID
        data (dict): 包含要更新字段的字典
        
    Returns:
        dict: 更新结果
    """
    try:
        # 查找指定的里程碑记录
        milestone = SysProjectMilestone.query.get(milestone_id)
        if not milestone:
            return {
                'code': 404,
                'message': '里程碑记录不存在'
            }
        
        # 保存更新前的数据
        old_data = {
            'milestone': milestone.milestone,
            'responsible_department': milestone.responsible_department,
            'planned_start_time': milestone.planned_start_time,
            'planned_end_time': milestone.planned_end_time,
            'actual_completion_time': milestone.actual_completion_time,
            'responsible_person': milestone.responsible_person,
            'exception_type': milestone.exception_type,
            'impact_cycle': milestone.impact_cycle,
            'response_measures': milestone.response_measures,
            'modification_log': milestone.modification_log
        }
        
        # 更新记录字段
        if 'milestone' in data:
            milestone.milestone = data['milestone']
        if 'responsible_department' in data:
            milestone.responsible_department = data['responsible_department']
        if 'planned_start_time' in data:
            milestone.planned_start_time = data['planned_start_time']
        if 'planned_end_time' in data:
            milestone.planned_end_time = data['planned_end_time']
        if 'actual_completion_time' in data:
            milestone.actual_completion_time = data['actual_completion_time']
        if 'responsible_person' in data:
            milestone.responsible_person = data['responsible_person']
        if 'exception_type' in data:
            milestone.exception_type = data['exception_type']
        if 'impact_cycle' in data:
            milestone.impact_cycle = data['impact_cycle']
        if 'response_measures' in data:
            milestone.response_measures = data['response_measures']
        if 'modification_log' in data:
            milestone.modification_log = data['modification_log']
        
        # 提交更改
        db.session.commit()
        
        # 记录修改日志
        new_data = {
            'milestone': milestone.milestone,
            'responsible_department': milestone.responsible_department,
            'planned_start_time': milestone.planned_start_time,
            'planned_end_time': milestone.planned_end_time,
            'actual_completion_time': milestone.actual_completion_time,
            'responsible_person': milestone.responsible_person,
            'exception_type': milestone.exception_type,
            'impact_cycle': milestone.impact_cycle,
            'response_measures': milestone.response_measures,
            'modification_log': milestone.modification_log
        }
        
        try:
            log_update('sys_project_milestone', milestone_id, old_data, new_data)
            
            # 检查影响周期是否发生了变化，如果变化则记录到专门的历史表中
            old_impact_cycle = old_data.get('impact_cycle')
            new_impact_cycle = new_data.get('impact_cycle')
            
            # 处理空值情况，将None或空字符串转换为0
            old_impact_cycle_int = 0
            if old_impact_cycle is not None and str(old_impact_cycle).strip() != '':
                try:
                    old_impact_cycle_int = int(float(str(old_impact_cycle)))
                except (ValueError, TypeError):
                    old_impact_cycle_int = 0
            
            new_impact_cycle_int = 0
            if new_impact_cycle is not None and str(new_impact_cycle).strip() != '':
                try:
                    new_impact_cycle_int = int(float(str(new_impact_cycle)))
                except (ValueError, TypeError):
                    new_impact_cycle_int = 0
            
            # 如果影响周期发生了变化，则记录到历史表
            if old_impact_cycle_int != new_impact_cycle_int:
                # 获取当前用户名（如果有）
                # 注意：在这个上下文中我们无法直接获取当前用户，所以在前端需要传递modified_by参数
                modified_by = data.get('modified_by', 'Unknown')
                
                # 创建影响周期修改历史记录
                impact_history = SysProjectMilestoneImpactHistory(
                    milestone_id=milestone.id,
                    project_id=milestone.project_id,
                    old_impact_cycle=old_impact_cycle_int,
                    new_impact_cycle=new_impact_cycle_int,
                    modified_by=modified_by
                )
                
                db.session.add(impact_history)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"记录更新日志时出错: {e}")
            # 即使日志记录失败，也继续执行
        
        return {
            'code': 200,
            'message': '里程碑记录更新成功'
        }
    except Exception as e:
        db.session.rollback()
        print(f"更新SysProjectMilestone记录时出错: {e}")
        return {
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }