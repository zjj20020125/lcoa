"""
SysProject表数据接口
提供读取SysProject表全部数据的功能
"""
from flask import jsonify
# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import SysProject, SysProjectMilestone, db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback

def get_all_sys_project_data():
    """
    获取SysProject表中的所有数据，包含关联的里程碑信息
    
    Returns:
        list: 包含所有SysProject记录的列表
    """
    try:
        # 查询所有记录，预加载里程碑数据
        sys_project_records = SysProject.query.all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_project_records:
            # 获取关联的里程碑数据
            milestones = []
            for milestone in record.milestones:
                milestones.append({
                    'id': milestone.id,
                    'milestone': milestone.milestone,
                    'responsible_department': milestone.responsible_department,
                    'planned_start_time': milestone.planned_start_time,
                    'planned_end_time': milestone.planned_end_time,
                    'actual_completion_time': milestone.actual_completion_time,
                    'responsible_person': milestone.responsible_person,
                    'exception_type': milestone.exception_type,
                    'impact_cycle': milestone.impact_cycle,
                    'response_measures': milestone.response_measures,
                    'modification_log': milestone.modification_log,
                    'created_at': milestone.created_at.isoformat() if milestone.created_at else None,
                    'updated_at': milestone.updated_at.isoformat() if milestone.updated_at else None
                })
            
            result.append({
                'id': record.id,
                'project_name': record.project_name,
                'product_name': record.product_name,
                'product_image': record.product_image,
                'customer_name': record.customer_name,
                'order_status': record.order_status,
                'milestones': milestones,
                'created_at': record.created_at.isoformat() if record.created_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None
            })
        
        return result
    except Exception as e:
        print(f"获取SysProject数据时出错: {e}")
        return []


def create_sys_project(data, files=None):
    """
    创建新的SysProject记录
    
    Args:
        data (dict): 项目数据
        files (dict): 上传的文件
        
    Returns:
        dict: 创建结果
    """
    try:
        # 处理上传的图片文件，直接保存为Base64编码
        product_image_data = None
        if files and 'product_image' in files:
            file = files['product_image']
            if file and file.filename != '':
                # 将图片文件转换为Base64编码
                import base64
                file_content = file.read()
                # 获取文件的MIME类型
                import mimetypes
                mime_type = mimetypes.guess_type(file.filename)[0] or 'image/jpeg'
                # 生成Base64数据URL
                encoded_content = base64.b64encode(file_content).decode('utf-8')
                product_image_data = f"data:{mime_type};base64,{encoded_content}"
        
        # 创建项目记录
        project = SysProject(
            project_name=data.get('project_name', ''),
            product_name=data.get('product_name', ''),
            product_image=product_image_data,
            customer_name=data.get('customer_name', ''),
            order_status=data.get('order_status', '')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return {
            'code': 200,
            'message': '项目创建成功',
            'data': {
                'id': project.id,
                'product_image': product_image_data
            }
        }
    except Exception as e:
        db.session.rollback()
        print(f"创建SysProject记录时出错: {e}")
        return {
            'code': 500,
            'message': f'创建失败: {str(e)}'
        }


def update_sys_project(project_id, data, files=None):
    """
    更新SysProject表中的指定记录
    
    Args:
        project_id (int): 项目记录的ID
        data (dict): 包含要更新字段的字典
        files (dict): 上传的文件
        
    Returns:
        dict: 更新结果
    """
    try:
        print(f"开始更新项目，ID: {project_id}")
        print(f"收到的数据: {data}")
        print(f"收到的文件: {files}")
        
        # 查找指定的项目记录
        project = SysProject.query.get(project_id)
        if not project:
            print(f"项目未找到，ID: {project_id}")
            return {
                'code': 404,
                'message': '项目记录不存在'
            }
        
        # 保存更新前的数据
        old_data = {
            'project_name': project.project_name,
            'product_name': project.product_name,
            'product_image': project.product_image,
            'customer_name': project.customer_name,
            'order_status': project.order_status
        }
        print(f"更新前的数据: {old_data}")
        
        # 处理上传的图片文件，直接保存为Base64编码
        product_image_data = data.get('product_image', project.product_image)
        if files and 'product_image' in files:
            file = files['product_image']
            print(f"处理上传的文件: {file.filename if file else 'None'}")
            if file and file.filename != '':
                try:
                    # 将图片文件转换为Base64编码
                    import base64
                    file_content = file.read()
                    print(f"文件大小: {len(file_content)} bytes")
                    
                    # 获取文件的MIME类型
                    import mimetypes
                    mime_type = mimetypes.guess_type(file.filename)[0] or 'image/jpeg'
                    print(f"检测到的MIME类型: {mime_type}")
                    
                    # 生成Base64数据URL
                    encoded_content = base64.b64encode(file_content).decode('utf-8')
                    product_image_data = f"data:{mime_type};base64,{encoded_content}"
                    print("文件成功转换为Base64")
                except Exception as e:
                    print(f"处理图片文件时出错: {e}")
                    traceback.print_exc()
            else:
                print("没有有效的文件上传")
        else:
            print("没有文件需要处理")
        
        # 更新记录字段，确保不会覆盖其他字段
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'product_name' in data:
            project.product_name = data['product_name']
        if 'product_image' in data or product_image_data != project.product_image:
            project.product_image = product_image_data
        if 'customer_name' in data:
            project.customer_name = data['customer_name']
        if 'order_status' in data:
            project.order_status = data['order_status']
        
        print(f"准备更新的数据: project_name={project.project_name}, product_name={project.product_name}, customer_name={project.customer_name}, order_status={project.order_status}")
        
        # 提交更改
        db.session.commit()
        print("数据库提交成功")
        
        # 记录修改日志
        new_data = {
            'project_name': project.project_name,
            'product_name': project.product_name,
            'product_image': project.product_image,
            'customer_name': project.customer_name,
            'order_status': project.order_status
        }
        
        try:
            # 修复导入方式
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from utils.modification_logger import log_update
            log_update('sys_project', project_id, old_data, new_data)
            print("日志记录完成")
        except Exception as e:
            print(f"记录日志时出错: {e}")
            traceback.print_exc()
            # 即使日志记录失败，也不影响主要功能
        
        return {
            'code': 200,
            'message': '项目记录更新成功'
        }
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        print(f"更新SysProject记录时出错: {e}")
        print(f"详细错误信息:\n{error_details}")
        return {
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }


def get_sys_project_by_id(project_id):
    """
    根据ID获取单个SysProject记录，包含关联的里程碑信息
    
    Args:
        project_id (int): 项目记录的ID
        
    Returns:
        dict: 项目详情
    """
    try:
        # 查询指定ID的记录，预加载里程碑数据
        project = SysProject.query.get(project_id)
        
        if not project:
            return {
                'code': 404,
                'message': '项目记录不存在'
            }
        
        # 获取关联的里程碑数据
        milestones = []
        for milestone in project.milestones:
            milestones.append({
                'id': milestone.id,
                'milestone': milestone.milestone,
                'responsible_department': milestone.responsible_department,
                'planned_start_time': milestone.planned_start_time,
                'planned_end_time': milestone.planned_end_time,
                'actual_completion_time': milestone.actual_completion_time,
                'responsible_person': milestone.responsible_person,
                'exception_type': milestone.exception_type,
                'impact_cycle': milestone.impact_cycle,
                'response_measures': milestone.response_measures,
                'modification_log': milestone.modification_log,
                'created_at': milestone.created_at.isoformat() if milestone.created_at else None,
                'updated_at': milestone.updated_at.isoformat() if milestone.updated_at else None
            })
        
        result = {
            'id': project.id,
            'project_name': project.project_name,
            'product_name': project.product_name,
            'product_image': project.product_image,
            'customer_name': project.customer_name,
            'order_status': project.order_status,
            'milestones': milestones,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None
        }
        
        return {
            'code': 200,
            'message': '获取成功',
            'data': result
        }
    except Exception as e:
        print(f"获取SysProject数据时出错: {e}")
        return {
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }


def create_sys_project_milestone(project_id, data):
    """
    为指定项目创建新的里程碑
    
    Args:
        project_id (int): 项目ID
        data (dict): 里程碑数据
        
    Returns:
        dict: 创建结果
    """
    try:
        # 检查项目是否存在
        project = SysProject.query.get(project_id)
        if not project:
            return {
                'code': 404,
                'message': '项目不存在'
            }
        
        # 创建里程碑记录
        milestone = SysProjectMilestone(
            project_id=project_id,
            milestone=data.get('milestone', ''),
            responsible_department=data.get('responsible_department', ''),
            planned_start_time=data.get('planned_start_time'),
            planned_end_time=data.get('planned_end_time'),
            actual_completion_time=data.get('actual_completion_time'),
            responsible_person=data.get('responsible_person', ''),
            exception_type=data.get('exception_type', ''),
            impact_cycle=data.get('impact_cycle'),
            response_measures=data.get('response_measures', '')
        )
        
        db.session.add(milestone)
        db.session.commit()
        
        return {
            'code': 200,
            'message': '里程碑创建成功',
            'data': {
                'id': milestone.id
            }
        }
    except Exception as e:
        db.session.rollback()
        print(f"创建SysProjectMilestone记录时出错: {e}")
        return {
            'code': 500,
            'message': f'创建失败: {str(e)}'
        }


def delete_sys_project_milestone(milestone_id):
    """
    删除指定的里程碑记录
    
    Args:
        milestone_id (int): 里程碑ID
        
    Returns:
        dict: 删除结果
    """
    try:
        # 查找里程碑记录
        milestone = SysProjectMilestone.query.get(milestone_id)
        if not milestone:
            return {
                'code': 404,
                'message': '里程碑不存在'
            }
        
        db.session.delete(milestone)
        db.session.commit()
        
        return {
            'code': 200,
            'message': '里程碑删除成功'
        }
    except Exception as e:
        db.session.rollback()
        print(f"删除SysProjectMilestone记录时出错: {e}")
        return {
            'code': 500,
            'message': f'删除失败: {str(e)}'
        }
