"""
用户表迁移脚本
向users表添加employee_id和phone字段
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import pymysql

# 初始化Flask应用和数据库
app = Flask(__name__)

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

# 初始化数据库
db = SQLAlchemy(app)

def add_missing_columns():
    """向users表添加缺失的列"""
    with app.app_context():
        try:
            # 检查表结构
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            # 添加employee_id列（如果不存在）
            if 'employee_id' not in columns:
                db.session.execute(db.text('ALTER TABLE users ADD COLUMN employee_id VARCHAR(50) NULL'))
                print("已添加employee_id列")
            
            # 添加phone列（如果不存在）
            if 'phone' not in columns:
                db.session.execute(db.text('ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL'))
                print("已添加phone列")
            
            # 提交更改
            db.session.commit()
            print("数据库迁移完成")
            
        except Exception as e:
            db.session.rollback()
            print(f"迁移过程中出错: {e}")
            raise

if __name__ == '__main__':
    add_missing_columns()