#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目与里程碑关系处理模块
用于处理一个项目对应多个关键里程碑节点的关系
"""

import pandas as pd
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

lcoa_path = os.path.join(project_root, 'lcoa')
if lcoa_path not in sys.path:
    sys.path.insert(0, lcoa_path)

# 导入数据库模型
try:
    from models import db, SysProject, SysProjectMilestone
except ImportError:
    try:
        from lcoa.models import db, SysProject, SysProjectMilestone
    except ImportError:
        try:
            from app import db, SysProject, SysProjectMilestone
        except ImportError:
            from ....app import db, SysProject, SysProjectMilestone


def process_project_milestones(df):
    """
    处理项目和里程碑的关系
    
    Args:
        df (pandas.DataFrame): 包含项目和里程碑数据的DataFrame
        
    Returns:
        dict: 处理结果
    """
    try:
        processed_projects = []
        processed_milestones = []
        
        # 按项目名称分组
        if '项目名称' in df.columns:
            grouped = df.groupby('项目名称')
        else:
            return {
                'success': False,
                'message': '数据中缺少项目名称列'
            }
        
        for project_name, group in grouped:
            # 处理项目信息
            project_data = group.iloc[0]  # 取第一条记录作为项目信息
            
            # 创建或更新项目
            project = SysProject(
                project_name=str(project_name) if pd.notna(project_name) else '',
                product_name=str(project_data.get('产品名称', '')) if pd.notna(project_data.get('产品名称', '')) else '',
                customer_name=str(project_data.get('客户名称', '')) if pd.notna(project_data.get('客户名称', '')) else '',
                order_status=str(project_data.get('订单情况', '')) if pd.notna(project_data.get('订单情况', '')) else ''
            )
            
            db.session.add(project)
            db.session.flush()  # 获取项目ID
            
            processed_projects.append({
                'id': project.id,
                'project_name': project.project_name
            })
            
            # 处理该项目的所有里程碑
            for index, row in group.iterrows():
                # 检查是否为里程碑数据（关键节点不为空）
                if pd.notna(row.get('关键里程碑节点')) and str(row.get('关键里程碑节点')).strip() != '':
                    milestone = SysProjectMilestone(
                        project_id=project.id,
                        milestone=str(row.get('关键里程碑节点', '')) if pd.notna(row.get('关键里程碑节点', '')) else '',
                        responsible_department=str(row.get('责任部门', '')) if pd.notna(row.get('责任部门', '')) else '',
                        planned_start_time=str(row.get('计划开始时间', '')) if pd.notna(row.get('计划开始时间', '')) else '',
                        planned_end_time=str(row.get('计划结束时间', '')) if pd.notna(row.get('计划结束时间', '')) else '',
                        actual_completion_time=str(row.get('实际完成时间', '')) if pd.notna(row.get('实际完成时间', '')) else '',
                        responsible_person=str(row.get('负责人', '')) if pd.notna(row.get('负责人', '')) else '',
                        exception_type=str(row.get('异常类别', '')) if pd.notna(row.get('异常类别', '')) else '',
                        impact_cycle=str(row.get('影响周期（天）', '')) if pd.notna(row.get('影响周期（天）', '')) else '',
                        response_measures=str(row.get('应对措施', '')) if pd.notna(row.get('应对措施', '')) else ''
                    )
                    
                    db.session.add(milestone)
                    processed_milestones.append({
                        'project_id': project.id,
                        'project_name': project.project_name,
                        'milestone': milestone.milestone
                    })
        
        # 打印即将存储的项目数据
        print("即将存储的项目数据:")
        for project in processed_projects:
            print(f"  - 项目ID: {project['id']}, 项目名称: {project['project_name']}")
        
        # 打印即将存储的里程碑数据
        print("即将存储的里程碑数据:")
        for milestone in processed_milestones:
            print(f"  - 项目ID: {milestone['project_id']}, 项目名称: {milestone['project_name']}, 里程碑: {milestone['milestone']}")
        
        # 提交事务
        print(f"正在提交 {len(processed_projects)} 个项目和 {len(processed_milestones)} 个里程碑到数据库...")
        db.session.commit()
        print(f"数据已成功提交到数据库")
        
        result = {
            'success': True,
            'message': f'成功处理 {len(processed_projects)} 个项目，{len(processed_milestones)} 个里程碑',
            'processed_projects': processed_projects,
            'processed_milestones': processed_milestones
        }
        
        # 打印已成功存储的数据
        print("已成功存储到数据库的数据:")
        print(f"成功存储 {len(processed_projects)} 个项目:")
        for project in processed_projects:
            print(f"  - 项目ID: {project['id']}, 项目名称: {project['project_name']}")
        
        print(f"成功存储 {len(processed_milestones)} 个里程碑:")
        for milestone in processed_milestones:
            print(f"  - 项目ID: {milestone['project_id']}, 项目名称: {milestone['project_name']}, 里程碑: {milestone['milestone']}")
        
        return result
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'处理项目和里程碑关系时出错: {str(e)}'
        }


def get_project_milestones_relationship(project_id=None):
    """
    获取项目和里程碑的关系数据
    
    Args:
        project_id (int, optional): 项目ID，如果提供则只返回该项目的关系数据
        
    Returns:
        dict: 项目和里程碑的关系数据
    """
    try:
        if project_id:
            # 获取特定项目及其里程碑
            project = SysProject.query.get(project_id)
            if not project:
                return {
                    'success': False,
                    'message': f'未找到ID为 {project_id} 的项目'
                }
            
            milestones = SysProjectMilestone.query.filter_by(project_id=project_id).all()
        else:
            # 获取所有项目及其里程碑
            projects = SysProject.query.all()
            result = []
            
            for project in projects:
                milestones = SysProjectMilestone.query.filter_by(project_id=project.id).all()
                milestone_data = []
                
                for milestone in milestones:
                    milestone_data.append({
                        'id': milestone.id,
                        'milestone': milestone.milestone,
                        'responsible_department': milestone.responsible_department,
                        'planned_start_time': milestone.planned_start_time,
                        'planned_end_time': milestone.planned_end_time,
                        'actual_completion_time': milestone.actual_completion_time,
                        'responsible_person': milestone.responsible_person,
                        'exception_type': milestone.exception_type,
                        'impact_cycle': milestone.impact_cycle,
                        'response_measures': milestone.response_measures
                    })
                
                result.append({
                    'id': project.id,
                    'project_name': project.project_name,
                    'product_name': project.product_name,
                    'milestones': milestone_data
                })
            
            return {
                'success': True,
                'data': result
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'获取项目和里程碑关系数据时出错: {str(e)}'
        }


def update_project_milestone_relationship(project_id, milestones_data):
    """
    更新项目和里程碑的关系
    
    Args:
        project_id (int): 项目ID
        milestones_data (list): 里程碑数据列表
        
    Returns:
        dict: 更新结果
    """
    try:
        # 检查项目是否存在
        project = SysProject.query.get(project_id)
        if not project:
            return {
                'success': False,
                'message': f'未找到ID为 {project_id} 的项目'
            }
        
        # 删除现有的里程碑数据
        SysProjectMilestone.query.filter_by(project_id=project_id).delete()
        
        # 添加新的里程碑数据
        for milestone_data in milestones_data:
            milestone = SysProjectMilestone(
                project_id=project_id,
                milestone=milestone_data.get('milestone', ''),
                responsible_department=milestone_data.get('responsible_department', ''),
                planned_start_time=milestone_data.get('planned_start_time', ''),
                planned_end_time=milestone_data.get('planned_end_time', ''),
                actual_completion_time=milestone_data.get('actual_completion_time', ''),
                responsible_person=milestone_data.get('responsible_person', ''),
                exception_type=milestone_data.get('exception_type', ''),
                impact_cycle=milestone_data.get('impact_cycle', ''),
                response_measures=milestone_data.get('response_measures', '')
            )
            db.session.add(milestone)
        
        # 提交事务
        print(f"正在提交项目 {project.project_name} 的里程碑更新到数据库...")
        db.session.commit()
        print(f"项目 {project.project_name} 的里程碑数据已成功提交到数据库")
        
        return {
            'success': True,
            'message': f'成功更新项目 {project.project_name} 的里程碑数据'
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'更新项目和里程碑关系时出错: {str(e)}'
        }