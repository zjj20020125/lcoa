"""
为现有项目添加里程碑数据的脚本
每个项目添加2-3个关键节点
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import app, db, SysProject, SysProjectMilestone

def add_milestone_data():
    """为现有项目添加里程碑数据"""
    with app.app_context():
        # 获取所有现有项目
        projects = SysProject.query.all()
        
        if not projects:
            print("没有找到任何项目，请先创建项目数据")
            return
        
        # 清除现有的里程碑数据
        SysProjectMilestone.query.delete()
        db.session.commit()
        
        print(f"找到 {len(projects)} 个项目，开始添加里程碑数据...")
        
        # 为每个项目添加2-3个里程碑
        for project in projects:
            print(f"为项目 '{project.project_name}' 添加里程碑...")
            
            # 根据项目名称确定里程碑数据
            if "智能管理系统" in project.project_name:
                milestones_data = [
                    {
                        'milestone': '需求分析',
                        'responsible_department': '产品部',
                        'planned_start_time': '2025-12-01',
                        'planned_end_time': '2025-12-15',
                        'actual_completion_time': '2025-12-14',
                        'responsible_person': '张三',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': '按时完成'
                    },
                    {
                        'milestone': '系统设计',
                        'responsible_department': '研发部',
                        'planned_start_time': '2025-12-16',
                        'planned_end_time': '2025-12-30',
                        'actual_completion_time': '',
                        'responsible_person': '李四',
                        'exception_type': '需求变更',
                        'impact_cycle': '3',
                        'response_measures': '增加设计评审环节',
                        'modification_log': '因需求变更延期3天'
                    },
                    {
                        'milestone': '编码实现',
                        'responsible_department': '研发部',
                        'planned_start_time': '2025-12-31',
                        'planned_end_time': '2026-02-15',
                        'actual_completion_time': '',
                        'responsible_person': '王五',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    }
                ]
            elif "电商" in project.project_name:
                milestones_data = [
                    {
                        'milestone': '合同签署',
                        'responsible_department': '销售部',
                        'planned_start_time': '2025-11-20',
                        'planned_end_time': '2025-11-25',
                        'actual_completion_time': '2025-11-25',
                        'responsible_person': '赵六',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': '按时完成'
                    },
                    {
                        'milestone': '需求调研',
                        'responsible_department': '产品部',
                        'planned_start_time': '2025-11-26',
                        'planned_end_time': '2025-12-10',
                        'actual_completion_time': '',
                        'responsible_person': '孙七',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    }
                ]
            elif "数据分析" in project.project_name:
                milestones_data = [
                    {
                        'milestone': '需求收集',
                        'responsible_department': '产品部',
                        'planned_start_time': '2025-06-01',
                        'planned_end_time': '2025-06-15',
                        'actual_completion_time': '2025-06-15',
                        'responsible_person': '周八',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': '按时完成'
                    },
                    {
                        'milestone': '架构设计',
                        'responsible_department': '技术部',
                        'planned_start_time': '2025-06-16',
                        'planned_end_time': '2025-06-30',
                        'actual_completion_time': '2025-06-28',
                        'responsible_person': '吴九',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': '提前2天完成'
                    },
                    {
                        'milestone': '开发实施',
                        'responsible_department': '研发部',
                        'planned_start_time': '2025-07-01',
                        'planned_end_time': '2025-10-30',
                        'actual_completion_time': '2025-10-25',
                        'responsible_person': '郑十',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': '提前5天完成'
                    }
                ]
            elif "移动应用" in project.project_name:
                milestones_data = [
                    {
                        'milestone': 'UI设计',
                        'responsible_department': '设计部',
                        'planned_start_time': '2025-12-10',
                        'planned_end_time': '2025-12-25',
                        'actual_completion_time': '',
                        'responsible_person': '钱一',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    },
                    {
                        'milestone': '前端开发',
                        'responsible_department': '移动开发部',
                        'planned_start_time': '2025-12-26',
                        'planned_end_time': '2026-01-30',
                        'actual_completion_time': '',
                        'responsible_person': '孙二',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    }
                ]
            elif "云服务" in project.project_name:
                milestones_data = [
                    {
                        'milestone': '方案设计',
                        'responsible_department': '架构部',
                        'planned_start_time': '2025-10-01',
                        'planned_end_time': '2025-10-20',
                        'actual_completion_time': '2025-10-18',
                        'responsible_person': '李四',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': '提前2天完成'
                    },
                    {
                        'milestone': '服务器采购',
                        'responsible_department': '运维部',
                        'planned_start_time': '2025-10-21',
                        'planned_end_time': '2025-10-30',
                        'actual_completion_time': '',
                        'responsible_person': '周五',
                        'exception_type': '供应链问题',
                        'impact_cycle': '5',
                        'response_measures': '联系备用供应商',
                        'modification_log': '延期5天'
                    },
                    {
                        'milestone': '环境部署',
                        'responsible_department': '运维部',
                        'planned_start_time': '2025-10-31',
                        'planned_end_time': '2025-11-15',
                        'actual_completion_time': '',
                        'responsible_person': '吴六',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    }
                ]
            else:
                # 默认里程碑数据
                milestones_data = [
                    {
                        'milestone': '启动阶段',
                        'responsible_department': '项目管理部',
                        'planned_start_time': '2025-12-01',
                        'planned_end_time': '2025-12-10',
                        'actual_completion_time': '',
                        'responsible_person': '项目经理',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    },
                    {
                        'milestone': '执行阶段',
                        'responsible_department': '执行团队',
                        'planned_start_time': '2025-12-11',
                        'planned_end_time': '2026-01-10',
                        'actual_completion_time': '',
                        'responsible_person': '执行经理',
                        'exception_type': '',
                        'impact_cycle': '',
                        'response_measures': '',
                        'modification_log': ''
                    }
                ]
            
            # 创建里程碑记录
            milestones = []
            for md in milestones_data:
                milestone = SysProjectMilestone(
                    project_id=project.id,
                    milestone=md['milestone'],
                    responsible_department=md['responsible_department'],
                    planned_start_time=md['planned_start_time'],
                    planned_end_time=md['planned_end_time'],
                    actual_completion_time=md['actual_completion_time'],
                    responsible_person=md['responsible_person'],
                    exception_type=md['exception_type'],
                    impact_cycle=md['impact_cycle'],
                    response_measures=md['response_measures'],
                    modification_log=md['modification_log']
                )
                milestones.append(milestone)
            
            # 添加到数据库
            for milestone in milestones:
                db.session.add(milestone)
            
            print(f"  -> 添加了 {len(milestones)} 个里程碑")
        
        try:
            db.session.commit()
            print(f"\n成功为 {len(projects)} 个项目添加了里程碑数据")
        except Exception as e:
            db.session.rollback()
            print(f"插入数据时出错: {e}")

if __name__ == '__main__':
    add_milestone_data()