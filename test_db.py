import pymysql
import os

# 数据库配置
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'zjj520111314')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '3306')
DB_NAME = os.environ.get('DB_NAME', 'lcoa')

print(f"连接信息: host={DB_HOST}, user={DB_USER}, password={DB_PASSWORD}, database={DB_NAME}")

try:
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT)
    )
    print("数据库连接成功")
    
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")
        
    # 检查lcoa表结构
    cursor.execute("DESCRIBE lcoa")
    columns = cursor.fetchall()
    print("\nlcoa表结构:")
    for column in columns:
        print(f"  - {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
    connection.close()
except Exception as e:
    print(f"数据库连接失败: {e}")