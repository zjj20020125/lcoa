"""
重置并填充项目数据脚本
清空sys_project表和sys_project_milestone表中的所有数据，
然后插入8-10个新项目，每个项目包含3-4个里程碑节点
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import app, db, SysProject, SysProjectMilestone

def reset_and_seed_project_data():
    """清空并重新填充项目和里程碑数据"""
    with app.app_context():
        # 删除现有数据（需要先删除从表再删除主表）
        milestones_deleted = SysProjectMilestone.query.delete()
        projects_deleted = SysProject.query.delete()
        db.session.commit()
        
        print(f"已清空 {projects_deleted} 个项目和 {milestones_deleted} 个里程碑数据")

        # 创建8-10个示例项目
        sample_projects = [
            {
                'project_name': '智能制造MES系统开发项目',
                'product_name': '制造执行系统V3.0',
                'product_image': 'https://example.com/images/project1.png',
                'customer_name': '华东重工集团',
                'order_status': '实施中'
            },
            {
                'project_name': '智慧校园综合管理平台',
                'product_name': '教育信息化解决方案',
                'product_image': 'https://example.com/images/project2.png',
                'customer_name': '华南理工大学',
                'order_status': '已签约'
            },
            {
                'project_name': '金融风控大数据分析系统',
                'product_name': '风险预警平台',
                'product_image': 'https://example.com/images/project3.png',
                'customer_name': '中信银行',
                'order_status': '实施中'
            },
            {
                'project_name': '智慧医疗远程诊疗平台',
                'product_name': '远程医疗系统',
                'product_image': 'https://example.com/images/project4.png',
                'customer_name': '华西医院',
                'order_status': '已完成'
            },
            {
                'project_name': '新能源汽车充电桩网络建设',
                'product_name': '充电运营管理系统',
                'product_image': 'https://example.com/images/project5.png',
                'customer_name': '比亚迪汽车',
                'order_status': '实施中'
            },
            {
                'project_name': '跨境电商物流跟踪系统',
                'product_name': '全球物流可视化平台',
                'product_image': 'https://example.com/images/project6.png',
                'customer_name': '阿里巴巴国际站',
                'order_status': '已签约'
            },
            {
                'project_name': '智慧城市交通信号控制系统',
                'product_name': '智能交通管理平台',
                'product_image': 'https://example.com/images/project7.png',
                'customer_name': '深圳市交警支队',
                'order_status': '实施中'
            },
            {
                'project_name': '企业人力资源管理系统升级',
                'product_name': 'HR一体化平台V5.0',
                'product_image': 'https://example.com/images/project8.png',
                'customer_name': '华为技术有限公司',
                'order_status': '已签约'
            },
            {
                'project_name': '在线教育直播互动平台',
                'product_name': '云端课堂系统',
                'product_image': 'https://example.com/images/project9.png',
                'customer_name': '网易有道',
                'order_status': '实施中'
            },
            {
                'project_name': '区块链数字存证平台',
                'product_name': '电子证据保全系统',
                'product_image': 'https://example.com/images/project10.png',
                'customer_name': '杭州互联网法院',
                'order_status': '已签约'
            }
        ]

        # 插入项目数据并收集项目对象
        projects = []
        for project_data in sample_projects:
            project = SysProject(**project_data)
            db.session.add(project)
            projects.append(project)
        
        # 提交以获取项目ID
        db.session.flush()
        
        # 为每个项目创建3-4个里程碑
        milestone_templates = [
            {
                'milestone': '需求调研与分析',
                'responsible_department': '产品部',
                'duration_days': 15,
                'responsible_person': '产品经理'
            },
            {
                'milestone': '系统架构设计',
                'responsible_department': '技术部',
                'duration_days': 10,
                'responsible_person': '架构师'
            },
            {
                'milestone': '核心功能开发',
                'responsible_department': '研发部',
                'duration_days': 30,
                'responsible_person': '开发经理'
            },
            {
                'milestone': '系统测试与验收',
                'responsible_department': '测试部',
                'duration_days': 20,
                'responsible_person': '测试主管'
            }
        ]
        
        # 存储所有创建的里程碑
        all_milestones = []
        
        # 为每个项目创建里程碑
        base_date = datetime.now()
        for i, project in enumerate(projects):
            start_date = base_date + timedelta(days=i * 5)  # 每个项目间隔5天开始
            
            # 为每个项目创建3-4个里程碑（最后一个项目只创建3个）
            num_milestones = 3 if i == len(projects) - 1 else 4
            
            for j in range(num_milestones):
                template = milestone_templates[j]
                milestone_start = start_date + timedelta(days=j * 10)  # 每个里程碑间隔10天
                milestone_end = milestone_start + timedelta(days=template['duration_days'])
                
                # 对于已完成的项目，设置实际完成时间为计划完成时间
                actual_completion = milestone_end.strftime('%Y-%m-%d') if project.order_status == '已完成' and j < 3 else ''
                
                milestone = SysProjectMilestone(
                    project_id=project.id,
                    milestone=template['milestone'],
                    responsible_department=template['responsible_department'],
                    planned_start_time=milestone_start.strftime('%Y-%m-%d'),
                    planned_end_time=milestone_end.strftime('%Y-%m-%d'),
                    actual_completion_time=actual_completion,
                    responsible_person=template['responsible_person'] + str(i+1),  # 添加编号区分
                    exception_type='' if j != 1 else '需求变更',  # 第二个里程碑有异常
                    impact_cycle='' if j != 1 else '5',  # 第二个里程碑有影响周期
                    response_measures='' if j != 1 else '增加设计评审会议',
                    modification_log='正常进行' if j < 3 else ''
                )
                
                all_milestones.append(milestone)
                db.session.add(milestone)

        try:
            db.session.commit()
            print(f"成功插入 {len(projects)} 个项目和 {len(all_milestones)} 个里程碑数据")
            print("\n项目列表:")
            for project in projects:
                milestone_count = len([m for m in all_milestones if m.project_id == project.id])
                print(f"- {project.project_name} ({project.order_status}) - {milestone_count}个里程碑")
        except Exception as e:
            db.session.rollback()
            print(f"插入数据时出错: {e}")

if __name__ == '__main__':
    reset_and_seed_project_data()