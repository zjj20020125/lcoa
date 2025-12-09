#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库备份脚本
"""

import os
import sys
from datetime import datetime
import subprocess

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(project_root)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def backup_database():
    """备份数据库"""
    try:
        # 从配置中获取数据库信息
        from app import app
        
        with app.app_context():
            # 获取数据库配置
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"数据库URI: {db_uri}")
            
            # 解析数据库配置
            # 示例: mysql+pymysql://root:password@localhost:3306/lcoa
            if 'mysql' in db_uri:
                # 提取数据库信息
                import re
                match = re.match(r'mysql\+pymysql://(.*?):(.*?)@(.*?):(.*?)/(.*?)$', db_uri)
                if match:
                    user, password, host, port, database = match.groups()
                    
                    # 构造备份文件名
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_file = f'{database}_backup_{timestamp}.sql'
                    
                    # 尝试使用 mysqldump 备份
                    try:
                        # 尝试几种常见的 mysqldump 路径
                        mysqldump_paths = [
                            'mysqldump',
                            'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe',
                            'C:\\Program Files\\MySQL\\MySQL Server 5.7\\bin\\mysqldump.exe',
                            'C:\\xampp\\mysql\\bin\\mysqldump.exe'
                        ]
                        
                        success = False
                        for mysqldump_path in mysqldump_paths:
                            try:
                                cmd = [
                                    mysqldump_path,
                                    f'--host={host}',
                                    f'--port={port}',
                                    f'--user={user}',
                                    f'--password={password}',
                                    database
                                ]
                                
                                with open(backup_file, 'w', encoding='utf-8') as f:
                                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                                    
                                if result.returncode == 0:
                                    print(f"数据库备份成功: {backup_file}")
                                    success = True
                                    break
                                else:
                                    print(f"使用 {mysqldump_path} 备份失败: {result.stderr}")
                            except FileNotFoundError:
                                print(f"找不到 {mysqldump_path}")
                            except Exception as e:
                                print(f"使用 {mysqldump_path} 备份时出错: {e}")
                        
                        if not success:
                            print("所有 mysqldump 路径都不可用，尝试其他备份方法...")
                            # 可以在这里添加其他备份方法
                            
                    except Exception as e:
                        print(f"备份过程中出错: {e}")
                else:
                    print("无法解析数据库配置")
            else:
                print("当前仅支持 MySQL 数据库备份")
                
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保在正确的环境中运行此脚本")
    except Exception as e:
        print(f"备份过程中出现错误: {e}")

if __name__ == "__main__":
    backup_database()