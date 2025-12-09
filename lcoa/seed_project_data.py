"""
种子数据脚本
向sys_project表中插入5组示例数据，方便后续开发使用
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import app, db, SysProject

def seed_project_data():
    """插入示例项目数据"""
    with app.app_context():
        # 检查是否已有数据
        existing_count = SysProject.query.count()
        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 条项目数据，跳过数据插入")
            return

        # 创建5组示例数据
        sample_projects = [
            {
                'project_name': '智能管理系统开发项目',
                'product_name': '企业管理平台V1.0',
                'product_image': 'https://example.com/images/project1.png',
                'customer_name': 'ABC科技有限公司',
                'order_status': '已签约',
                'milestone': '需求分析完成',
                'responsible_department': '研发部',
                'planned_start_time': '2025-12-01',
                'planned_end_time': '2026-05-30',
                'actual_completion_time': '',
                'responsible_person': '张三',
                'exception_type': '需求变更',
                'impact_cycle': '15',
                'response_measures': '增加开发人员，调整项目计划'
            },
            {
                'project_name': '电商平台优化项目',
                'product_name': '在线购物系统V2.5',
                'product_image': 'https://example.com/images/project2.png',
                'customer_name': 'XYZ电子商务公司',
                'order_status': '实施中',
                'milestone': '系统测试阶段',
                'responsible_department': '产品部',
                'planned_start_time': '2025-11-01',
                'planned_end_time': '2026-02-28',
                'actual_completion_time': '',
                'responsible_person': '李四',
                'exception_type': '',
                'impact_cycle': '',
                'response_measures': ''
            },
            {
                'project_name': '数据分析平台建设项目',
                'product_name': '大数据分析工具',
                'product_image': 'https://example.com/images/project3.png',
                'customer_name': 'DEF金融集团',
                'order_status': '已完成',
                'milestone': '项目验收',
                'responsible_department': '数据部',
                'planned_start_time': '2025-06-15',
                'planned_end_time': '2025-11-20',
                'actual_completion_time': '2025-11-18',
                'responsible_person': '王五',
                'exception_type': '技术难题',
                'impact_cycle': '10',
                'response_measures': '引入外部专家协助解决'
            },
            {
                'project_name': '移动应用开发项目',
                'product_name': '健康助手APP',
                'product_image': 'https://example.com/images/project4.png',
                'customer_name': 'GHI健康科技',
                'order_status': '已签约',
                'milestone': 'UI设计完成',
                'responsible_department': '移动开发部',
                'planned_start_time': '2025-12-10',
                'planned_end_time': '2026-04-30',
                'actual_completion_time': '',
                'responsible_person': '赵六',
                'exception_type': '',
                'impact_cycle': '',
                'response_measures': ''
            },
            {
                'project_name': '云服务部署项目',
                'product_name': '企业云平台',
                'product_image': 'https://example.com/images/project5.png',
                'customer_name': 'JKL制造有限公司',
                'order_status': '实施中',
                'milestone': '服务器部署',
                'responsible_department': '运维部',
                'planned_start_time': '2025-10-20',
                'planned_end_time': '2026-01-15',
                'actual_completion_time': '',
                'responsible_person': '孙七',
                'exception_type': '硬件延迟',
                'impact_cycle': '7',
                'response_measures': '寻找替代供应商'
            }
        ]

        # 插入数据
        for project_data in sample_projects:
            project = SysProject(**project_data)
            db.session.add(project)

        try:
            db.session.commit()
            print(f"成功插入 {len(sample_projects)} 条示例项目数据")
        except Exception as e:
            db.session.rollback()
            print(f"插入数据时出错: {e}")

if __name__ == '__main__':
    seed_project_data()