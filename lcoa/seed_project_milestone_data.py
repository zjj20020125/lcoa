"""
种子数据脚本
向sys_project和sys_project_milestone表中插入示例数据，演示主从表关系
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import app, db, SysProject, SysProjectMilestone

def seed_project_milestone_data():
    """插入示例项目和里程碑数据"""
    with app.app_context():
        # 删除现有数据
        SysProjectMilestone.query.delete()
        SysProject.query.delete()
        db.session.commit()
        
        print("已清空现有项目数据")

        # 创建示例项目
        project1 = SysProject(
            project_name='智能管理系统开发项目',
            product_name='企业管理平台V1.0',
            product_image='https://example.com/images/project1.png',
            customer_name='ABC科技有限公司',
            order_status='实施中'
        )
        
        project2 = SysProject(
            project_name='电商平台优化项目',
            product_name='在线购物系统V2.5',
            product_image='https://example.com/images/project2.png',
            customer_name='XYZ电子商务公司',
            order_status='已签约'
        )
        
        db.session.add(project1)
        db.session.add(project2)
        db.session.flush()  # 获取项目ID但不提交
        
        # 为项目1创建里程碑
        milestones1 = [
            SysProjectMilestone(
                project_id=project1.id,
                milestone='需求分析',
                responsible_department='产品部',
                planned_start_time='2025-12-01',
                planned_end_time='2025-12-15',
                actual_completion_time='2025-12-14',
                responsible_person='张三',
                exception_type='',
                impact_cycle='',
                response_measures='',
                modification_log='按时完成'
            ),
            SysProjectMilestone(
                project_id=project1.id,
                milestone='系统设计',
                responsible_department='研发部',
                planned_start_time='2025-12-16',
                planned_end_time='2025-12-30',
                actual_completion_time='',
                responsible_person='李四',
                exception_type='需求变更',
                impact_cycle='3',
                response_measures='增加设计评审环节',
                modification_log='因需求变更延期3天'
            ),
            SysProjectMilestone(
                project_id=project1.id,
                milestone='编码实现',
                responsible_department='研发部',
                planned_start_time='2025-12-31',
                planned_end_time='2026-02-15',
                actual_completion_time='',
                responsible_person='王五',
                exception_type='',
                impact_cycle='',
                response_measures='',
                modification_log=''
            )
        ]
        
        # 为项目2创建里程碑
        milestones2 = [
            SysProjectMilestone(
                project_id=project2.id,
                milestone='合同签署',
                responsible_department='销售部',
                planned_start_time='2025-11-20',
                planned_end_time='2025-11-25',
                actual_completion_time='2025-11-25',
                responsible_person='赵六',
                exception_type='',
                impact_cycle='',
                response_measures='',
                modification_log='按时完成'
            ),
            SysProjectMilestone(
                project_id=project2.id,
                milestone='需求调研',
                responsible_department='产品部',
                planned_start_time='2025-11-26',
                planned_end_time='2025-12-10',
                actual_completion_time='',
                responsible_person='孙七',
                exception_type='',
                impact_cycle='',
                response_measures='',
                modification_log=''
            )
        ]
        
        # 添加所有里程碑
        for milestone in milestones1 + milestones2:
            db.session.add(milestone)

        try:
            db.session.commit()
            print(f"成功插入2个项目和{len(milestones1 + milestones2)}个里程碑数据")
        except Exception as e:
            db.session.rollback()
            print(f"插入数据时出错: {e}")

if __name__ == '__main__':
    seed_project_milestone_data()