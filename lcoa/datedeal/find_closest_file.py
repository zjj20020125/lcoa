import os
import re
from datetime import datetime

def extract_date_from_filename(filename):
    """
    从文件名中提取日期信息

    Args:
        filename (str): 文件名

    Returns:
        datetime: 提取到的日期对象，如果未找到则返回None
    """
    # 尝试多种日期格式
    # 格式1: 2025-09-29
    match1 = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match1:
        try:
            return datetime.strptime(match1.group(1), '%Y-%m-%d')
        except ValueError:
            pass

    # 格式2: 2025年10月09日
    match2 = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', filename)
    if match2:
        try:
            return datetime.strptime(match2.group(1), '%Y年%m月%d日')
        except ValueError:
            pass

    # 格式3: 20250929
    match3 = re.search(r'(\d{8})', filename)
    if match3:
        try:
            return datetime.strptime(match3.group(1), '%Y%m%d')
        except ValueError:
            pass

    return None

def find_closest_file_to_current_date(directory_path):
    """
    在指定目录中查找最接近当前日期的文件

    Args:
        directory_path (str): 目录路径

    Returns:
        tuple: (最接近的文件名, 日期差值天数, 提取的日期)
    """
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return None, None, None

    # 获取当前日期
    current_date = datetime.now()
    
    closest_file = None
    closest_date = None
    min_diff_days = float('inf')

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 获取文件的完整路径
        file_path = os.path.join(directory_path, filename)
        
        # 只处理文件，跳过目录
        if os.path.isfile(file_path):
            print(f"正在处理文件: {filename}")
            
            # 从文件名提取日期
            file_date = extract_date_from_filename(filename)
            
            if file_date:
                # 计算与当前日期的差距（绝对值）
                diff_days = abs((current_date - file_date).days)
                
                print(f"提取的日期: {file_date.strftime('%Y-%m-%d')}, 与当前日期相差: {diff_days} 天")
                
                # 更新最接近的文件
                if diff_days < min_diff_days:
                    min_diff_days = diff_days
                    closest_file = filename
                    closest_date = file_date
            else:
                print(f"未能从文件名中提取日期信息")

    if closest_file:
        return closest_file, min_diff_days, closest_date
    else:
        return None, None, None

def list_all_files_with_dates(directory_path):
    """
    列出目录中所有文件及其提取的日期信息

    Args:
        directory_path (str): 目录路径

    Returns:
        list: 包含(文件名, 提取日期)元组的列表
    """
    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return []

    files_with_dates = []
    
    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 获取文件的完整路径
        file_path = os.path.join(directory_path, filename)
        
        # 只处理文件，跳过目录
        if os.path.isfile(file_path):
            # 从文件名提取日期
            file_date = extract_date_from_filename(filename)
            
            files_with_dates.append((filename, file_date))
            
    return files_with_dates

if __name__ == "__main__":
    # 指定要搜索的目录路径
    target_directory = r'C:\Users\Administrator\Documents\导出表格\结果'
    
    print("=" * 60)
    print("查找最接近当前日期的文件")
    print("=" * 60)
    
    # 列出所有文件及其日期
    print("\n目录中的所有文件及提取的日期:")
    print("-" * 40)
    files_with_dates = list_all_files_with_dates(target_directory)
    
    if files_with_dates:
        for filename, file_date in files_with_dates:
            if file_date:
                print(f"{filename} -> {file_date.strftime('%Y-%m-%d')}")
            else:
                print(f"{filename} -> 未提取到日期")
    else:
        print("目录中没有找到文件或无法访问目录")
    
    # 查找最接近当前日期的文件
    print("\n查找最接近当前日期的文件:")
    print("-" * 40)
    closest_file, diff_days, closest_date = find_closest_file_to_current_date(target_directory)
    
    if closest_file:
        print(f"最接近当前日期的文件: {closest_file}")
        print(f"提取的日期: {closest_date.strftime('%Y-%m-%d')}")
        print(f"与当前日期相差: {diff_days} 天")
    else:
        print("未找到包含日期信息的文件")