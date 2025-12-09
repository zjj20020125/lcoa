from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import os
import pymysql
import sqlalchemy
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
import sys

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'zjj520111314')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_NAME = os.environ.get('DB_NAME', 'lcoa')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JWT_EXPIRATION_DELTA'] = 3600  # 1小时有效期

# 导入本地模块
from models import db, User, Lcoa, SysNodeal, SysDeal, SysPersonal, SysXiangxi, SysClub, SysProject, SysProjectMilestone, SysProjectMilestoneImpactHistory, ModificationLog
from services.data_service import (
    save_to_lcoa_table,
    save_to_sys_nodeal_table_with_comparison,
    save_to_sys_xiangxi_table,
    save_to_sys_club_table,
    save_to_sys_club_table_with_comparison,
    save_to_sys_nodeal_table_with_comparison,
    save_to_sys_xiangxi_table_with_comparison
)
from utils import generate_token, verify_token

# 初始化
db.init_app(app)
CORS(app, supports_credentials=True, origins="*")

# 创建所有表
def create_tables():
    """创建所有表"""
    with app.app_context():
        # 首先尝试创建所有表（包括新添加的字段）
        db.create_all()
        print("所有表创建成功")
        
        # 检查是否需要添加新列到现有表
        inspector = sqlalchemy.inspect(db.engine)
        if 'users' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'employee_id' not in columns or 'phone' not in columns:
                print("警告: users表缺少新列，可能需要手动更新数据库结构")
        
        # 检查modification_log表是否存在
        if 'modification_log' not in inspector.get_table_names():
            print("警告: modification_log表不存在，可能需要手动创建")
        
        # 创建默认管理员用户（如果不存在）
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', employee_id='ADMIN001', role='admin')
            admin_user.set_password('123456')
            db.session.add(admin_user)
            db.session.commit()
            print("默认管理员用户创建成功，用户名: admin, 工号: ADMIN001, 密码: 123456")

# API路由
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        data = request.get_json()
        username = data.get('username')  # 真实姓名
        password = data.get('password')
        employee_id = data.get('employee_id', '')  # 工号
        phone = data.get('phone', '')  # 手机号
        
        # 检查参数
        if not username or not employee_id or not password:
            return jsonify({
                'code': 400,
                'message': '姓名、工号和密码不能为空'
            }), 400
        
        # 检查工号是否已存在
        existing_user = User.query.filter_by(employee_id=employee_id).first()
        if existing_user:
            return jsonify({
                'code': 400,
                'message': '工号已存在'
            }), 400
        
        # 创建新用户
        new_user = User(
            username=username, 
            role='user',
            employee_id=employee_id,
            phone=phone
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': new_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'注册失败: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        username = data.get('username')  # 真实姓名
        employee_id = data.get('employee_id')  # 工号
        password = data.get('password')
        role = data.get('role', 'user')  # 默认为普通用户
        
        # 检查参数
        if not username or not password:
            return jsonify({
                'code': 400,
                'message': '姓名和密码不能为空'
            }), 400
        
        # 查找用户（通过真实姓名，工号可选）
        if employee_id:
            # 如果提供了工号，则同时匹配姓名和工号
            user = User.query.filter_by(username=username, employee_id=employee_id).first()
        else:
            # 如果没有提供工号，则仅通过姓名查找
            user = User.query.filter_by(username=username).first()
            
        if not user or not user.check_password(password):
            return jsonify({
                'code': 401,
                'message': '姓名、工号或密码错误'
            }), 401
        
        # 检查角色权限
        if role == 'admin' and user.role != 'admin':
            return jsonify({
                'code': 403,
                'message': '权限不足，无法以管理员身份登录'
            }), 403
        
        # 生成token
        token = generate_token(app.config['SECRET_KEY'], user.id, user.username, user.role)
        
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': token,
                'username': user.username,
                'employee_id': user.employee_id,
                'role': user.role
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}'
        }), 500

@app.route('/api/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息"""
    try:
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'code': 401,
                'message': '未提供认证信息'
            }), 401
        
        # 解析token
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
        payload = verify_token(app.config['SECRET_KEY'], token)
        
        if not payload:
            return jsonify({
                'code': 401,
                'message': '无效或过期的token'
            }), 401
        
        # 获取用户信息
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取用户信息成功',
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

# API路由
@app.route('/api/lcoa', methods=['GET'])
def api_get_lcoa_data():
    """获取LCOA表所有数据的API接口"""
    try:
        # 查询所有记录
        lcoa_records = Lcoa.query.all()
        
        # 将记录转换为字典列表
        result = []
        # 获取最新的记录ID
        latest_record = Lcoa.query.order_by(Lcoa.id.desc()).first()
        record_id = latest_record.id if latest_record else None
        
        for record in lcoa_records:
            result.append({
                'id': record_id,
                'process_id': record.process_id,
                'processNode': record.process_node_id,
                'Title': record.process_title,
                'processType': record.process_type,
                'Department': record.department,
                'Club': record.branch,
                'name_process': record.process_name,
                'user_Name': record.node_operator,
                'Status': record.node_operation_type,
                'Process_Name': record.process_name,
                'start_time': record.first_receive_time,
                'final_time': record.last_process_time,
                'inter_time': record.total_duration,
                'import_date': record.extracted_date,
                'created_at': record.first_receive_time,
                'updated_at': record.last_process_time
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/lcoa/count', methods=['GET'])
def api_get_lcoa_count():
    """获取LCOA表数据总条数的API接口"""
    try:
        # 查询总条数
        count = Lcoa.query.count()
        
        return jsonify({
            'code': 200,
            'message': '统计成功',
            'data': {
                'total': count
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'统计失败: {str(e)}',
            'data': {
                'total': 0
            }
        })

@app.route('/api/lcoa/max-id', methods=['GET'])
def api_get_lcoa_max_id():
    """获取LCOA表最大ID值的API接口"""
    try:
        # 导入获取最大ID的函数
        from lcoa.api.lcoa_api import get_max_lcoa_id
        
        # 获取最大ID值
        max_id = get_max_lcoa_id()
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': {
                'max_id': max_id
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': {
                'max_id': 0
            }
        })

@app.route('/api/sys_nodeal', methods=['GET'])
def api_get_sys_nodeal_data():
    """获取SysNodeal表所有数据的API接口，按ID倒序排列"""
    try:
        # 查询所有记录，按ID倒序排列
        sys_nodeal_records = SysNodeal.query.order_by(SysNodeal.id.desc()).all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_nodeal_records:
            result.append({
                'id': record.id,
                'extracted_date': record.extracted_date,
                'process_node_id': record.process_node_id,
                'process_id': record.process_id,
                'process_title': record.process_title,
                'process_name': record.process_name,
                'process_type': record.process_type,
                'branch': record.branch,
                'department': record.department,
                'node_operator': record.node_operator,
                'node_operation_type': record.node_operation_type,
                'node_name': record.node_name,
                'first_receive_time': record.first_receive_time,
                'last_process_time': record.last_process_time,
                'total_duration': record.total_duration,
                'total_timeout': record.total_timeout
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_nodeal/count', methods=['GET'])
def api_get_sys_nodeal_count():
    """获取SysNodeal表数据总条数的API接口"""
    try:
        # 查询总条数
        count = SysNodeal.query.count()
        
        return jsonify({
            'code': 200,
            'message': '统计成功',
            'data': {
                'total': count
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'统计失败: {str(e)}',
            'data': {
                'total': 0
            }
        })

@app.route('/api/sys_deal', methods=['GET'])
def api_get_sys_deal_data():
    """获取SysDeal表所有数据的API接口"""
    try:
        # 查询所有记录
        sys_deal_records = SysDeal.query.all()
        
        # 将记录转换为字典列表
        result = []
        for record in sys_deal_records:
            result.append({
                'id': record.id,
                'col1': record.col1,
                'col2': record.col2,
                'col3': record.col3,
                'col4': record.col4,
                'col5': record.col5,
                'col6': record.col6,
                'col7': record.col7,
                'col8': record.col8,
                'col9': record.col9,
                'col10': record.col10,
                'col11': record.col11,
                'col12': record.col12,
                'col13': record.col13,
                'col14': record.col14,
                'col15': record.col15,
                'col16': record.col16,
                'col17': record.col17,
                'col18': record.col18,
                'col19': record.col19,
                'col20': record.col20,
                'extracted_datetime': record.extracted_datetime,
                'filename': record.filename,
                'import_time': record.import_time,
                'update_time': record.update_time
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_deal/count', methods=['GET'])
def api_get_sys_deal_count():
    """获取SysDeal表数据总条数的API接口"""
    try:
        # 查询总条数
        count = SysDeal.query.count()
        
        return jsonify({
            'code': 200,
            'message': '统计成功',
            'data': {
                'total': count
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'统计失败: {str(e)}',
            'data': {
                'total': 0
            }
        })

@app.route('/api/sys_xiangxi', methods=['GET'])
def api_get_sys_xiangxi_data():
    """获取SysXiangxi表所有数据的API接口"""
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
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_club', methods=['GET'])
def api_get_sys_club_data():
    """获取SysClub表所有数据的API接口"""
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
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_club/latest', methods=['GET'])
def api_get_sys_club_latest():
    """获取SysClub表最新数据的API接口"""
    try:
        # 获取最新日期的记录
        # 先获取所有不同的日期
        distinct_dates = db.session.query(SysClub.extracted_date).distinct().all()
        if not distinct_dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': []
            })
        
        # 将日期列表转换为普通列表并排序
        dates = [date[0] for date in distinct_dates if date[0] is not None]
        if not dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': []
            })
        
        # 排序并获取最新的日期
        dates.sort(reverse=True)
        latest_date = dates[0]
        
        # 获取指定日期的所有记录
        latest_records = SysClub.query.filter_by(extracted_date=latest_date).all()
        
        # 将记录转换为字典列表
        result = []
        for record in latest_records:
            result.append({
                'id': record.id,
                'extracted_date': record.extracted_date,
                'department': record.department,
                'personnel_count': record.personnel_count,
                'timeout_count': record.timeout_count
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_xiangxi/latest', methods=['GET'])
def api_get_sys_xiangxi_latest():
    """获取SysXiangxi表最新数据的API接口"""
    try:
        # 获取最新日期的记录
        # 先获取所有不同的日期
        distinct_dates = db.session.query(SysXiangxi.extracted_date).distinct().all()
        if not distinct_dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': []
            })
        
        # 将日期列表转换为普通列表并排序
        dates = [date[0] for date in distinct_dates if date[0] is not None]
        if not dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': []
            })
        
        # 排序并获取最新的日期
        dates.sort(reverse=True)
        latest_date = dates[0]
        
        # 获取指定日期的所有记录
        latest_records = SysXiangxi.query.filter_by(extracted_date=latest_date).all()
        
        # 将记录转换为字典列表
        result = []
        for record in latest_records:
            result.append({
                'id': record.id,
                '时间': record.extracted_date,
                '姓名': record.node_operator,
                '部门': record.department,
                '流程状态': record.node_operation_type,
                '数量': record.quantity
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_personal/latest', methods=['GET'])
def api_get_sys_personal_latest():
    """获取SysPersonal表最新数据的API接口"""
    try:
        # 获取最新日期的记录
        # 先获取所有不同的日期
        distinct_dates = db.session.query(SysPersonal.extracted_date).distinct().all()
        if not distinct_dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': []
            })
        
        # 将日期列表转换为普通列表并排序
        dates = [date[0] for date in distinct_dates if date[0] is not None]
        if not dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': []
            })
        
        # 排序并获取最新的日期
        dates.sort(reverse=True)
        latest_date = dates[0]
        
        # 获取指定日期的所有记录
        latest_records = SysPersonal.query.filter_by(extracted_date=latest_date).all()
        
        # 将记录转换为字典列表
        result = []
        for record in latest_records:
            result.append({
                'id': record.id,
                'extracted_date': record.extracted_date,
                'name': record.name,
                'department': record.department,
                'quantity': record.quantity
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/sys_club/latest_date', methods=['GET'])
def api_get_sys_club_latest_date():
    """获取SysClub表最接近当前时间的日期（月日格式）的API接口"""
    try:
        # 导入获取最新日期的函数
        from lcoa.api.sys_club_api import get_latest_club_date
        
        # 获取最新日期
        latest_date = get_latest_club_date()
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': {
                'latest_date': latest_date
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': {
                'latest_date': ''
            }
        })

@app.route('/api/sys_xiangxi/latest_date', methods=['GET'])
def api_get_sys_xiangxi_latest_date():
    """获取SysXiangxi表最接近当前时间的日期（月日格式）的API接口"""
    try:
        # 获取所有不同的日期
        distinct_dates = db.session.query(SysXiangxi.extracted_date).distinct().all()
        if not distinct_dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': {
                    'latest_date': ''
                }
            })
        
        # 将日期列表转换为普通列表并排序
        dates = [date[0] for date in distinct_dates if date[0] is not None]
        if not dates:
            return jsonify({
                'code': 200,
                'message': '查询成功',
                'data': {
                    'latest_date': ''
                }
            })
        
        # 排序并获取最新的日期
        dates.sort(reverse=True)
        latest_date = dates[0]
        
        # 格式化为月日格式
        from datetime import datetime
        try:
            date_obj = datetime.strptime(latest_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%m月%d日')
        except ValueError:
            formatted_date = latest_date  # 如果解析失败，使用原始日期
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': {
                'latest_date': formatted_date
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': {
                'latest_date': ''
            }
        })

# 新增用户管理API
@app.route('/api/users', methods=['GET'])
def api_get_all_users():
    """获取所有用户信息"""
    try:
        # 检查用户权限
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'code': 401,
                'message': '未提供认证信息'
            }), 401
        
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
        payload = verify_token(app.config['SECRET_KEY'], token)
        
        if not payload:
            return jsonify({
                'code': 401,
                'message': '无效的认证信息'
            }), 401
        
        # 查询所有用户
        users = User.query.all()
        
        # 将用户转换为字典列表
        result = [user.to_dict() for user in users]
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })

@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
def api_update_user_role(user_id):
    """更新用户角色"""
    try:
        # 检查用户权限
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'code': 401,
                'message': '未提供认证信息'
            }), 401
        
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
        payload = verify_token(app.config['SECRET_KEY'], token)
        
        if not payload or payload.get('role') != 'admin':
            return jsonify({
                'code': 403,
                'message': '权限不足'
            }), 403
        
        # 获取请求数据
        data = request.get_json()
        new_role = data.get('role')
        
        # 验证角色值
        if new_role not in ['user', 'admin']:
            return jsonify({
                'code': 400,
                'message': '无效的角色值'
            }), 400
        
        # 查找用户
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 防止修改初始管理员账户的角色
        if user.username == 'admin' and new_role != 'admin':
            return jsonify({
                'code': 400,
                'message': '不能修改初始管理员账户的角色'
            }), 400
        
        # 更新用户角色
        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '角色更新成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500

@app.route('/api/sys_xiangxi/daily_stats', methods=['GET'])
def api_get_sys_xiangxi_daily_stats():
    """获取SysXiangxi表每日数据统计的API接口"""
    try:
        # 查询所有记录并按日期分组统计
        from sqlalchemy import func, desc
        daily_stats = db.session.query(
            SysXiangxi.extracted_date,
            func.count(SysXiangxi.id).label('count')
        ).group_by(SysXiangxi.extracted_date).order_by(desc(SysXiangxi.extracted_date)).limit(7).all()
        
        # 将结果转换为字典列表
        result = []
        for stat in daily_stats:
            result.append({
                'date': stat.extracted_date,
                'count': stat.count
            })
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })


@app.route('/api/sys_project', methods=['GET'])
def api_get_sys_project_data():
    """获取SysProject表所有数据的API接口，包含关联的里程碑信息"""
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
        
        return jsonify({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}',
            'data': []
        })


@app.route('/api/sys_project', methods=['POST'])
def api_create_sys_project():
    """创建新的SysProject记录的API接口"""
    try:
        from lcoa.api.sys_project_api import create_sys_project
        
        # 检查是否有文件上传
        files = None
        if 'product_image' in request.files:
            files = {'product_image': request.files['product_image']}
        
        # 获取表单数据
        form_data = {
            'project_name': request.form.get('project_name', ''),
            'product_name': request.form.get('product_name', ''),
            'customer_name': request.form.get('customer_name', ''),
            'order_status': request.form.get('order_status', '')
        }
        
        result = create_sys_project(form_data, files)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'创建失败: {str(e)}'
        }), 500

@app.route('/api/sys_project/<int:project_id>', methods=['PUT'])
def api_update_sys_project(project_id):
    """更新SysProject表指定记录的API接口"""
    try:
        print(f"=== 开始处理项目更新请求 ===")
        print(f"项目ID: {project_id}")
        print(f"请求方法: {request.method}")
        print(f"内容类型: {request.content_type}")
        print(f"请求URL: {request.url}")
        print(f"请求数据: {request.data}")
        print(f"表单数据: {request.form}")
        print(f"文件数据: {request.files}")
        
        # 使用绝对导入
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from api.sys_project_api import update_sys_project
        # 检查是否有文件上传
        files = None
        if 'product_image' in request.files:
            files = {'product_image': request.files['product_image']}
            print(f"接收到文件: {request.files['product_image'].filename}")
        
        # 获取表单数据 - 支持FormData和JSON数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理FormData
            form_data = {
                'project_name': request.form.get('project_name', ''),
                'product_name': request.form.get('product_name', ''),
                'customer_name': request.form.get('customer_name', ''),
                'order_status': request.form.get('order_status', ''),
                'product_image': request.form.get('product_image', '')
            }
            print("使用FormData数据")
        else:
            # 处理JSON数据
            json_data = request.get_json() or {}
            form_data = {
                'project_name': json_data.get('project_name', ''),
                'product_name': json_data.get('product_name', ''),
                'customer_name': json_data.get('customer_name', ''),
                'order_status': json_data.get('order_status', ''),
                'product_image': json_data.get('product_image', '')
            }
            print("使用JSON数据")
        
        print(f"处理后的表单数据: {form_data}")
        
        result = update_sys_project(project_id, form_data, files)
        print(f"更新结果: {result}")
        print("=== 项目更新请求处理完成 ===")
        return jsonify(result)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"=== 更新项目时发生严重错误 ===")
        print(f"错误信息: {str(e)}")
        print(f"详细错误信息:\n{error_details}")
        print("=== 错误详情结束 ===")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500

@app.route('/api/sys_project/<int:project_id>', methods=['DELETE'])
def api_delete_sys_project(project_id):
    """删除项目记录"""
    try:
        # 查找项目记录
        project = SysProject.query.get(project_id)
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}'
        }), 500


@app.route('/api/sys_project/<int:project_id>', methods=['GET'])
def api_get_sys_project_by_id(project_id):
    """根据ID获取单个SysProject记录的API接口，包含关联的里程碑信息"""
    try:
        from api.sys_project_api import get_sys_project_by_id
        result = get_sys_project_by_id(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'查询失败: {str(e)}'
        }), 500


@app.route('/api/sys_project_milestone/<int:milestone_id>', methods=['PUT'])
def api_update_sys_project_milestone(milestone_id):
    """更新SysProjectMilestone表指定记录的API接口"""
    try:
        # 使用绝对导入
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from api.sys_project_milestone_api import update_sys_project_milestone
        data = request.get_json()
        result = update_sys_project_milestone(milestone_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500


@app.route('/api/sys_project/<int:project_id>/milestones', methods=['POST'])
def api_create_sys_project_milestone(project_id):
    """为指定项目创建新的里程碑记录的API接口"""
    try:
        from api.sys_project_api import create_sys_project_milestone
        data = request.get_json()
        result = create_sys_project_milestone(project_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'创建失败: {str(e)}'
        }), 500


@app.route('/api/sys_project_milestone/<int:milestone_id>', methods=['DELETE'])
def api_delete_sys_project_milestone(milestone_id):
    """删除指定的里程碑记录的API接口"""
    try:
        from api.sys_project_api import delete_sys_project_milestone
        result = delete_sys_project_milestone(milestone_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}'
        }), 500


@app.route('/api/import_projects', methods=['POST'])
def import_projects():
    """从Excel文件导入项目数据的API接口"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '未选择文件'
            }), 400
        
        # 检查文件类型
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({
                'code': 400,
                'message': '只支持Excel文件 (.xlsx, .xls)'
            }), 400
        
        # 保存临时文件
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
        file.save(temp_path)
        
        # 导入项目数据
        # 使用更可靠的导入方式
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 动态导入模块
        try:
            from datedeal.import_projects import import_projects_from_excel
        except ImportError:
            # 尝试其他导入方式
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "import_projects", 
                os.path.join(project_root, "datedeal", "import_projects.py")
            )
            import_projects_module = importlib.util.module_from_spec(spec)
            sys.modules["import_projects"] = import_projects_module
            spec.loader.exec_module(import_projects_module)
            import_projects_from_excel = import_projects_module.import_projects_from_excel
        
        result = import_projects_from_excel(temp_path)
        
        # 删除临时文件
        os.remove(temp_path)
        
        if result['success']:
            return jsonify({
                'code': 200,
                'message': result['message'],
                'data': result
            })
        else:
            return jsonify({
                'code': 400,
                'message': result['message']
            }), 400
            
    except Exception as e:
        # 记录详细的错误信息
        import traceback
        error_details = traceback.format_exc()
        print(f"导入项目时发生错误: {str(e)}")
        print(f"详细错误信息:\n{error_details}")
        
        return jsonify({
            'code': 500,
            'message': f'导入失败: {str(e)}'
        }), 500


# 添加静态文件访问路由
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)