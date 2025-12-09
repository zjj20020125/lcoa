from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 在这里我们初始化db
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' 或 'admin'
    employee_id = db.Column(db.String(50), nullable=True)  # 工号
    phone = db.Column(db.String(20), nullable=True)  # 手机号码
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """设置用户密码（加密）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查用户密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'employee_id': self.employee_id,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

# 定义Lcoa模型（第一个表）
class Lcoa(db.Model):
    __tablename__ = 'lcoa'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 根据第一个表中读取的列名称定义字段
    extracted_date = db.Column(db.String(20), nullable=True)  # 从文件名提取的日期
    process_node_id = db.Column(db.String(100), nullable=True)  # 流程节点id
    process_id = db.Column(db.String(100), nullable=True)  # 流程id
    process_title = db.Column(db.String(200), nullable=True)  # 流程标题
    process_name = db.Column(db.String(200), nullable=True)  # 流程名称
    process_type = db.Column(db.String(100), nullable=True)  # 流程类型
    branch = db.Column(db.String(100), nullable=True)  # 所属分部
    department = db.Column(db.String(100), nullable=True)  # 所属部门
    node_operator = db.Column(db.String(100), nullable=True)  # 节点操作者
    node_operation_type = db.Column(db.String(100), nullable=True)  # 节点操作类型
    node_name = db.Column(db.String(100), nullable=True)  # 节点名称
    first_receive_time = db.Column(db.String(50), nullable=True)  # 最初接收时间
    last_process_time = db.Column(db.String(50), nullable=True)  # 最后处理时间
    total_duration = db.Column(db.String(50), nullable=True)  # 总计耗时
    total_timeout = db.Column(db.String(50), nullable=True)  # 总计超时

    def __repr__(self):
        return f'<Lcoa {self.id}>'

# 定义SysNodeal模型（第二个表）
class SysNodeal(db.Model):
    __tablename__ = 'sys_nodeal'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 根据第二个表中读取的列名称定义字段
    extracted_date = db.Column(db.String(20), nullable=True)  # 从文件名提取的日期
    process_node_id = db.Column(db.String(100), nullable=True)  # 流程节点id
    process_id = db.Column(db.String(100), nullable=True)  # 流程id
    process_title = db.Column(db.String(200), nullable=True)  # 流程标题
    process_name = db.Column(db.String(200), nullable=True)  # 流程名称
    process_type = db.Column(db.String(100), nullable=True)  # 流程类型
    branch = db.Column(db.String(100), nullable=True)  # 所属分部
    department = db.Column(db.String(100), nullable=True)  # 所属部门
    node_operator = db.Column(db.String(100), nullable=True)  # 节点操作者
    node_operation_type = db.Column(db.String(100), nullable=True)  # 节点操作类型
    node_name = db.Column(db.String(100), nullable=True)  # 节点名称
    first_receive_time = db.Column(db.String(50), nullable=True)  # 最初接收时间
    last_process_time = db.Column(db.String(50), nullable=True)  # 最后处理时间
    total_duration = db.Column(db.String(50), nullable=True)  # 总计耗时
    total_timeout = db.Column(db.String(50), nullable=True)  # 总计超时

    def __repr__(self):
        return f'<SysNodeal {self.id}>'

# 定义SysDeal模型（第二个表的另一种形式）
class SysDeal(db.Model):
    __tablename__ = 'sys_deal'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 根据API文档定义字段
    col1 = db.Column(db.String(200), nullable=True)
    col2 = db.Column(db.String(200), nullable=True)
    col3 = db.Column(db.String(200), nullable=True)
    col4 = db.Column(db.String(200), nullable=True)
    col5 = db.Column(db.String(200), nullable=True)
    col6 = db.Column(db.String(200), nullable=True)
    col7 = db.Column(db.String(200), nullable=True)
    col8 = db.Column(db.String(200), nullable=True)
    col9 = db.Column(db.String(200), nullable=True)
    col10 = db.Column(db.String(200), nullable=True)
    col11 = db.Column(db.String(200), nullable=True)
    col12 = db.Column(db.String(200), nullable=True)
    col13 = db.Column(db.String(200), nullable=True)
    col14 = db.Column(db.String(200), nullable=True)
    col15 = db.Column(db.String(200), nullable=True)
    col16 = db.Column(db.String(200), nullable=True)
    col17 = db.Column(db.String(200), nullable=True)
    col18 = db.Column(db.String(200), nullable=True)
    col19 = db.Column(db.String(200), nullable=True)
    col20 = db.Column(db.String(200), nullable=True)
    extracted_datetime = db.Column(db.String(50), nullable=True)
    filename = db.Column(db.String(200), nullable=True)
    import_time = db.Column(db.String(50), nullable=True)
    update_time = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<SysDeal {self.id}>'

# 定义SysPersonal模型（第三个表）
class SysPersonal(db.Model):
    __tablename__ = 'sys_personal'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 根据第三个表中读取的列名称定义字段
    extracted_date = db.Column(db.String(20), nullable=True)  # 从文件名提取的日期
    name = db.Column(db.String(100), nullable=True)  # 姓名
    department = db.Column(db.String(100), nullable=True)  # 所属部门
    quantity = db.Column(db.String(50), nullable=True)  # 数量

    def __repr__(self):
        return f'<SysPersonal {self.id}>'

# 定义SysXiangxi模型（第四个表）
class SysXiangxi(db.Model):
    __tablename__ = 'sys_xiangxi'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 根据第四个表中读取的列名称定义字段
    extracted_date = db.Column(db.String(20), nullable=True)  # 从文件名提取的日期
    node_operator = db.Column(db.String(100), nullable=True)  # 节点操作者
    department = db.Column(db.String(100), nullable=True)  # 所属部门
    node_operation_type = db.Column(db.String(100), nullable=True)  # 节点操作类型
    quantity = db.Column(db.String(50), nullable=True)  # 数量

    def __repr__(self):
        return f'<SysXiangxi {self.id}>'

# 定义SysClub模型（第五个表）
class SysClub(db.Model):
    __tablename__ = 'sys_club'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 根据第五个表中读取的列名称定义字段
    extracted_date = db.Column(db.String(20), nullable=True)  # 从文件名提取的日期
    department = db.Column(db.String(100), nullable=True)  # 部门（第一列）
    personnel_count = db.Column(db.String(50), nullable=True)  # 人员数量（第二列）
    timeout_count = db.Column(db.String(50), nullable=True)  # 超时记录总数（第三列）

    def __repr__(self):
        return f'<SysClub {self.id}>'

# 定义SysProject模型（项目主表）
class SysProject(db.Model):
    __tablename__ = 'sys_project'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 项目名称
    project_name = db.Column(db.String(200), nullable=False)
    # 产品名称
    product_name = db.Column(db.String(200), nullable=False)
    # 产品示意图文件内容（Base64编码）
    product_image = db.Column(db.Text, nullable=True)
    # 客户名称
    customer_name = db.Column(db.String(100), nullable=True)
    # 订单情况
    order_status = db.Column(db.String(100), nullable=True)
    # 创建和更新时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联的里程碑节点
    milestones = db.relationship('SysProjectMilestone', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SysProject {self.project_name}>'

# 定义SysProjectMilestone模型（项目里程碑从表）
class SysProjectMilestone(db.Model):
    __tablename__ = 'sys_project_milestone'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联到项目主表
    project_id = db.Column(db.Integer, db.ForeignKey('sys_project.id'), nullable=False)
    # 关键节点
    milestone = db.Column(db.String(200), nullable=False)
    # 负责部门
    responsible_department = db.Column(db.String(100), nullable=True)
    # 计划开始时间
    planned_start_time = db.Column(db.String(50), nullable=True)
    # 计划结束时间
    planned_end_time = db.Column(db.String(50), nullable=True)
    # 实际完成时间
    actual_completion_time = db.Column(db.String(50), nullable=True)
    # 负责人
    responsible_person = db.Column(db.String(100), nullable=True)
    # 异常类别
    exception_type = db.Column(db.String(100), nullable=True)
    # 影响周期（天）
    impact_cycle = db.Column(db.String(50), nullable=True)
    # 应对措施
    response_measures = db.Column(db.Text, nullable=True)
    # 修改日志
    modification_log = db.Column(db.Text, nullable=True)
    # 创建和更新时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SysProjectMilestone {self.milestone}>'

# 定义SysProjectMilestoneImpactHistory模型（项目里程碑影响周期修改历史表）
class SysProjectMilestoneImpactHistory(db.Model):
    __tablename__ = 'sys_project_milestone_impact_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 外键关联到项目里程碑表
    milestone_id = db.Column(db.Integer, db.ForeignKey('sys_project_milestone.id'), nullable=False)
    # 项目ID（冗余字段，方便查询）
    project_id = db.Column(db.Integer, db.ForeignKey('sys_project.id'), nullable=False)
    # 修改前的影响周期
    old_impact_cycle = db.Column(db.Integer, nullable=False, default=0)
    # 修改后的影响周期
    new_impact_cycle = db.Column(db.Integer, nullable=False)
    # 修改人
    modified_by = db.Column(db.String(100), nullable=False)
    # 修改时间
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联的里程碑
    milestone = db.relationship('SysProjectMilestone', backref='impact_histories')
    # 关联的项目
    project = db.relationship('SysProject', backref='milestone_impact_histories')
    
    def __repr__(self):
        return f'<SysProjectMilestoneImpactHistory {self.id}: {self.old_impact_cycle} -> {self.new_impact_cycle}>'

# 定义ModificationLog模型（修改日志表）
class ModificationLog(db.Model):
    __tablename__ = 'modification_log'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 表名
    table_name = db.Column(db.String(100), nullable=False)
    # 记录ID
    record_id = db.Column(db.Integer, nullable=False)
    # 操作类型 (INSERT, UPDATE, DELETE)
    operation_type = db.Column(db.String(20), nullable=False)
    # 修改前的数据（JSON格式）
    old_data = db.Column(db.Text, nullable=True)
    # 修改后的数据（JSON格式）
    new_data = db.Column(db.Text, nullable=True)
    # 操作用户ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # 操作用户名称
    username = db.Column(db.String(50), nullable=True)
    # 操作时间
    operation_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ModificationLog {self.table_name}:{self.record_id}:{self.operation_type}>'
