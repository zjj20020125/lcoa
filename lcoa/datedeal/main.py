import os
import sys
import pandas as pd
import re
from datetime import datetime

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 修复导入问题 - 确保可以导入所需的模块
lcoa_path = os.path.join(project_root, 'lcoa')
if lcoa_path not in sys.path:
    sys.path.insert(0, lcoa_path)

# 延迟导入，确保路径设置完成后再导入
try:
    from lcoa.app import save_to_lcoa_table, save_to_sys_club_table_with_comparison, save_to_sys_nodeal_table_with_comparison, save_to_sys_xiangxi_table_with_comparison
    print("✓ 成功导入所有必需函数")
except ImportError as e:
    print(f"导入错误: {e}")
    print("尝试使用动态导入方式...")
    
    # 动态导入lcoa.app模块中的函数
    try:
        import importlib.util
        app_module_path = os.path.join(project_root, 'lcoa', 'app.py')
        spec = importlib.util.spec_from_file_location("lcoa_app", app_module_path)
        app_module = importlib.util.module_from_spec(spec)
        sys.modules["lcoa_app"] = app_module
        spec.loader.exec_module(app_module)
        
        # 获取需要的函数
        save_to_lcoa_table = getattr(app_module, 'save_to_lcoa_table')
        save_to_sys_club_table_with_comparison = getattr(app_module, 'save_to_sys_club_table_with_comparison')
        save_to_sys_nodeal_table_with_comparison = getattr(app_module, 'save_to_sys_nodeal_table_with_comparison')
        save_to_sys_xiangxi_table_with_comparison = getattr(app_module, 'save_to_sys_xiangxi_table_with_comparison')
        
        print("✓ 动态导入成功")
    except Exception as dynamic_error:
        print(f"动态导入也失败了: {dynamic_error}")
        print("请确保已安装所有依赖项并正确设置PYTHONPATH")
        sys.exit(1)

def extract_date_from_filename(filename):
    """
    从文件名中提取日期信息

    Args:
        filename (str): 文件名

    Returns:
        str: 提取到的日期，如果未找到则返回空字符串
    """
    # 尝试多种日期格式
    # 格式1: 2025-09-29
    match1 = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match1:
        return match1.group(1)

    # 格式2: 2025年10月09日
    match2 = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', filename)
    if match2:
        date_str = match2.group(1)
        try:
            # 转换为标准格式
            date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass

    return ''

def read_excel_fifth_sheets(directory_path):
    """
    从指定目录下所有Excel文件的第五个工作表中提取数据

    Args:
        directory_path (str): Excel文件所在的目录路径

    Returns:
        list: 包含所有数据行的数组，每行数据格式为[extracted_datetime, filename, data_columns...]
    """
    # 存储所有数据的数组
    all_data = []

    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return all_data

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 检查是否为Excel文件
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            file_path = os.path.join(directory_path, filename)
            print(f"正在处理文件: {filename}")

            # 从文件名提取日期
            extracted_datetime = extract_date_from_filename(filename)
            print(f"从文件名提取的日期: {extracted_datetime}")

            try:
                # 读取Excel文件的第五个工作表（索引为4）
                df = pd.read_excel(file_path, sheet_name=4)  # 第五个工作表

                # 如果DataFrame为空，跳过此文件
                if df.empty:
                    print(f"文件 {filename} 的第五个工作表是空的，跳过")
                    continue

                # 打印调试信息
                print(f"文件 {filename} 的第五个工作表列名: {list(df.columns)}")
                print(f"文件 {filename} 的第五个工作表前两行数据:")
                print(df.head(2))

                # 读取所有行的数据
                for index, row in df.iterrows():
                    # 创建一行数据，包含提取的时间、文件名和所有数据列
                    row_data = [extracted_datetime, filename]  # 前两个元素是时间信息和文件名
                    for val in row:
                        # 处理NaN值
                        row_data.append(str(val) if pd.notna(val) else '')

                    all_data.append(row_data)

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                import traceback
                traceback.print_exc()

    return all_data

def save_data_to_file(data, output_file='fifth_sheet_data.txt'):
    """
    将第五个表的数据保存到文件

    Args:
        data (list): 要保存的数据
        output_file (str): 输出文件名
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, row in enumerate(data):
            f.write(f"Row {i+1}: 提取的日期: {row[0]} | 文件名: {row[1]} | 数据: {row[2:]}\n")
    print(f"第五个表数据已保存到 {output_file}")

def extract_second_sheet_data(directory_path):
    """
    从指定目录下所有Excel文件的第二个工作表中提取指定列的数据

    Args:
        directory_path (str): Excel文件所在的目录路径

    Returns:
        list: 包含所有数据行的数组，每行是一个包含15个元素的数组（日期列+14个原有列）
    """
    # 存储所有数据的数组
    all_data = []

    # 定义需要读取的列名
    column_names = [
        '流程节点id', '流程id', '流程标题', '流程名称', '流程类型',
        '所属分部', '所属部门', '节点操作者', '节点操作类型', '节点名称',
        '最初接收时间', '最后处理时间', '总计耗时', '总计超时'
    ]

    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return all_data

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 检查是否为Excel文件
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            file_path = os.path.join(directory_path, filename)
            print(f"正在处理文件: {filename}")

            # 从文件名提取日期
            file_date = extract_date_from_filename(filename)
            print(f"从文件名提取的日期: {file_date}")

            try:
                # 读取Excel文件的第二个工作表（索引为1）
                df = pd.read_excel(file_path, sheet_name=1)

                # 如果DataFrame为空，跳过此文件
                if df.empty:
                    print(f"文件 {filename} 的第二个工作表是空的，跳过")
                    continue

                # 打印调试信息
                print(f"文件 {filename} 的第二个工作表列名: {list(df.columns)}")
                print(f"文件 {filename} 的第二个工作表前两行数据:")
                print(df.head(2))

                # 获取列名
                header_cols = list(df.columns)

                # 创建列索引映射（模糊匹配）
                col_index_mapping = {}
                for i, col_name in enumerate(header_cols):
                    # 清理列名（去除空格等）
                    clean_col_name = col_name.strip()
                    # 检查是否在我们需要的列名中
                    for target_col in column_names:
                        # 去除空格后比较
                        if clean_col_name == target_col.strip():
                            col_index_mapping[target_col] = i
                            break

                print(f"列索引映射: {col_index_mapping}")

                # 读取所有行的数据
                for index, row in df.iterrows():
                    # 先添加从文件名提取的日期作为第一列
                    row_data = [file_date]

                    # 根据列索引映射获取对应列的数据并添加到row_data中
                    for col_name in column_names:
                        if col_name in col_index_mapping:
                            col_idx = col_index_mapping[col_name]
                            # 确保不会越界访问
                            if col_idx < len(row):
                                # 处理NaN值
                                val = row.iloc[col_idx]
                                row_data.append(str(val) if pd.notna(val) else '')
                            else:
                                row_data.append('')
                        else:
                            row_data.append('')

                    all_data.append(row_data)

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                import traceback
                traceback.print_exc()

    return all_data

def extract_fourth_sheet_data(directory_path):
    """
    从指定目录下所有Excel文件的第四个工作表中提取指定列的数据

    Args:
        directory_path (str): Excel文件所在的目录路径

    Returns:
        list: 包含所有数据行的数组，每行是一个包含5个元素的数组（日期列+4个原有列）
    """
    # 存储所有数据的数组
    all_data = []

    # 定义需要读取的列名
    column_names = [
        '节点操作者', '所属部门', '节点操作类型', '数量'
    ]

    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return all_data

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 检查是否为Excel文件
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            file_path = os.path.join(directory_path, filename)
            print(f"正在处理文件: {filename}")

            # 从文件名提取日期
            file_date = extract_date_from_filename(filename)
            print(f"从文件名提取的日期: {file_date}")

            try:
                # 读取Excel文件的第四个工作表（索引为3）
                df = pd.read_excel(file_path, sheet_name=3)

                # 如果DataFrame为空，跳过此文件
                if df.empty:
                    print(f"文件 {filename} 的第四个工作表是空的，跳过")
                    continue

                # 打印调试信息
                print(f"文件 {filename} 的第四个工作表列名: {list(df.columns)}")
                print(f"文件 {filename} 的第四个工作表前两行数据:")
                print(df.head(2))

                # 获取列名
                header_cols = list(df.columns)

                # 创建列索引映射（模糊匹配）
                col_index_mapping = {}
                for i, col_name in enumerate(header_cols):
                    # 清理列名（去除空格等）
                    clean_col_name = col_name.strip()
                    # 检查是否在我们需要的列名中
                    for target_col in column_names:
                        # 去除空格后比较
                        if clean_col_name == target_col.strip():
                            col_index_mapping[target_col] = i
                            break

                print(f"列索引映射: {col_index_mapping}")

                # 读取所有行的数据
                for index, row in df.iterrows():
                    # 先添加从文件名提取的日期作为第一列
                    row_data = [file_date]

                    # 根据列索引映射获取对应列的数据并添加到row_data中
                    for col_name in column_names:
                        if col_name in col_index_mapping:
                            col_idx = col_index_mapping[col_name]
                            # 确保不会越界访问
                            if col_idx < len(row):
                                # 处理NaN值
                                val = row.iloc[col_idx]
                                row_data.append(str(val) if pd.notna(val) else '')
                            else:
                                row_data.append('')
                        else:
                            row_data.append('')

                    all_data.append(row_data)

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                import traceback
                traceback.print_exc()

    return all_data

def extract_process_data(directory_path):
    """
    从指定目录下所有Excel文件的第一个工作表中提取流程相关数据

    Args:
        directory_path (str): Excel文件所在的目录路径

    Returns:
        list: 包含所有数据行的数组，每行是一个包含15个元素的数组（日期列+14个原有列）
    """
    # 存储所有数据的数组
    all_data = []

    # 定义需要读取的列名
    column_names = [
        '流程节点id', '流程id', '流程标题', '流程名称', '流程类型',
        '所属分部', '所属部门', '节点操作者', '节点操作类型', '节点名称',
        '最初接收时间', '最后处理时间', '总计耗时', '总计超时'
    ]

    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return all_data

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 检查是否为Excel文件
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            file_path = os.path.join(directory_path, filename)
            print(f"正在处理文件: {filename}")

            # 从文件名提取日期
            file_date = extract_date_from_filename(filename)
            print(f"从文件名提取的日期: {file_date}")

            try:
                # 读取Excel文件的第一个工作表
                df = pd.read_excel(file_path, sheet_name=0)

                # 如果DataFrame为空，跳过此文件
                if df.empty:
                    print(f"文件 {filename} 是空的，跳过")
                    continue

                # 打印调试信息
                print(f"文件 {filename} 的列名: {list(df.columns)}")
                print(f"文件 {filename} 的前两行数据:")
                print(df.head(2))

                # 获取列名
                header_cols = list(df.columns)

                # 创建列索引映射（模糊匹配）
                col_index_mapping = {}
                for i, col_name in enumerate(header_cols):
                    # 清理列名（去除空格等）
                    clean_col_name = col_name.strip()
                    # 检查是否在我们需要的列名中
                    for target_col in column_names:
                        # 去除空格后比较
                        if clean_col_name == target_col.strip():
                            col_index_mapping[target_col] = i
                            break

                print(f"列索引映射: {col_index_mapping}")

                # 读取所有行的数据
                for index, row in df.iterrows():
                    # 先添加从文件名提取的日期作为第一列
                    row_data = [file_date]

                    # 根据列索引映射获取对应列的数据并添加到row_data中
                    for col_name in column_names:
                        if col_name in col_index_mapping:
                            col_idx = col_index_mapping[col_name]
                            # 确保不会越界访问
                            if col_idx < len(row):
                                # 处理NaN值
                                val = row.iloc[col_idx]
                                row_data.append(str(val) if pd.notna(val) else '')
                            else:
                                row_data.append('')
                        else:
                            row_data.append('')

                    all_data.append(row_data)

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                import traceback
                traceback.print_exc()

    return all_data

def extract_fifth_sheet_data_for_sys_club(directory_path):
    """
    从指定目录下所有Excel文件的第五个工作表中提取用于sys_club表的数据

    Args:
        directory_path (str): Excel文件所在的目录路径

    Returns:
        list: 包含所有数据行的数组，每行是一个包含4个元素的数组（日期列+3个原有列）
    """
    # 存储所有数据的数组
    all_data = []

    # 检查目录是否存在
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return all_data

    # 遍历目录中的所有文件
    for filename in os.listdir(directory_path):
        # 检查是否为Excel文件
        if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('~$'):
            file_path = os.path.join(directory_path, filename)
            print(f"正在处理文件: {filename}")

            # 从文件名提取日期
            file_date = extract_date_from_filename(filename)
            print(f"从文件名提取的日期: {file_date}")

            try:
                # 读取Excel文件的第五个工作表（索引为4）
                df = pd.read_excel(file_path, sheet_name=4)

                # 如果DataFrame为空，跳过此文件
                if df.empty:
                    print(f"文件 {filename} 的第五个工作表是空的，跳过")
                    continue

                # 打印调试信息
                print(f"文件 {filename} 的第五个工作表列名: {list(df.columns)}")
                print(f"文件 {filename} 的第五个工作表前两行数据:")
                print(df.head(2))

                # 读取所有行的数据，只取前3列加上日期列
                for index, row in df.iterrows():
                    # 创建一行数据，包含提取的时间和前三列数据
                    row_data = [file_date]  # 从文件名提取的日期
                    
                    # 只取前三列数据
                    for i in range(min(3, len(row))):
                        val = row.iloc[i]
                        row_data.append(str(val) if pd.notna(val) else '')

                    all_data.append(row_data)

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                import traceback
                traceback.print_exc()

    return all_data

def remove_duplicates(data):
    """
    根据第二列和第三列的数据进行去重，保留后面的记录

    Args:
        data (list): 包含所有数据行的数组

    Returns:
        list: 去重后的数据
    """
    if not data:
        return []

    # 使用字典来存储唯一的记录，键为第二列和第三列的组合
    unique_dict = {}

    for row in data:
        # 确保行数据至少有3列
        if len(row) >= 3:
            # 使用第二列和第三列组合作为键
            key = (row[1], row[2])  # 第二列和第三列（索引从0开始）
            # 后面的记录会覆盖前面的记录
            unique_dict[key] = row
        else:
            # 如果行数据不足3列，直接添加
            unique_dict[len(unique_dict)] = row

    # 将字典中的值转换为列表
    unique_data = list(unique_dict.values())

    print(f"去重前数据条数: {len(data)}")
    print(f"去重后数据条数: {len(unique_data)}")
    print(f"删除重复数据条数: {len(data) - len(unique_data)}")

    return unique_data

def save_data_as_arrays(data, output_file='process_data_arrays.txt'):
    """
    将提取的数据保存为数组格式

    Args:
        data (list): 提取的数据
        output_file (str): 输出文件名
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("[\n")
        for i, row in enumerate(data):
            f.write(f"    {row}")
            if i < len(data) - 1:  # 不是最后一行
                f.write(",\n")
            else:
                f.write("\n")
        f.write("]\n")
    print(f"数据已保存到 {output_file}")

def print_array_data(data, title="数组数据"):
    """
    打印数组数据
    
    Args:
        data (list): 要打印的数据
        title (str): 数据标题
    """
    print(f"\n{title}:")
    print(f"总共 {len(data)} 行数据")
    for i, row in enumerate(data):
        print(f"Row {i+1}: {row}")

def main():
    """
    主程序，提取流程数据
    """
    # 指定Excel文件所在的目录路径
    directory_path = r"C:\Users\Administrator\Documents\导出表格\结果"

    print("开始处理所有文件的第一个表...")

    # 读取数据
    extracted_data = extract_process_data(directory_path)

    # 打印统计信息
    print(f"总共提取了 {len(extracted_data)} 行数据")

    # 如果没有提取到数据，给出提示
    if len(extracted_data) == 0:
        print("警告：未提取到任何数据，请检查文件路径和文件格式")
        return []

    # 根据第二列和第三列进行去重，保留后面的记录
    unique_data = remove_duplicates(extracted_data)

    # 保存数据到文件
    save_data_as_arrays(unique_data, 'first—date.txt')
    
    # 将去重后的数据保存到lcoa表中
    # 修复函数调用 - 需要传递db和Lcoa参数
    from lcoa.app import app, db, Lcoa
    with app.app_context():
        save_to_lcoa_table(db, Lcoa, unique_data)

    # 显示前5行数据示例
    print("\n前5行数据示例:")
    for i, row in enumerate(unique_data[:5]):
        print(f"Row {i+1}: {row}")

    # 新增功能：读取所有文件中第二个表的数据
    print("\n开始处理所有文件的第二个表...")
    second_sheet_data = extract_second_sheet_data(directory_path)
    
    # 对第二个表的数据进行去重
    unique_second_sheet_data = remove_duplicates(second_sheet_data)
    
    # 将第二个表去重后的数据保存到sys_nodeal表中（使用比对更新逻辑）
    from lcoa.app import save_to_sys_nodeal_table_with_comparison, SysNodeal
    with app.app_context():
        save_to_sys_nodeal_table_with_comparison(db, SysNodeal, unique_second_sheet_data)
    
    print_array_data(unique_second_sheet_data, "第二个表去重后的数据")
    
    # 新增功能：读取所有文件中第四个表的数据
    print("\n开始处理所有文件的第四个表...")
    fourth_sheet_data = extract_fourth_sheet_data(directory_path)
    
    # 将第四个表的数据保存到sys_xiangxi表中（使用比对更新逻辑）
    from lcoa.app import save_to_sys_xiangxi_table_with_comparison, SysXiangxi
    with app.app_context():
        save_to_sys_xiangxi_table_with_comparison(db, SysXiangxi, fourth_sheet_data)
    
    # 第四个表的数据不需要去重，直接打印
    print_array_data(fourth_sheet_data, "第四个表的数据（未去重）")
    
    # 新增功能：读取所有文件中第五个表的数据
    print("\n开始处理所有文件的第五个表...")
    fifth_sheet_data = extract_fifth_sheet_data_for_sys_club(directory_path)
    
    # 将第五个表的数据保存到sys_club表中（使用比对更新逻辑）
    from lcoa.app import save_to_sys_club_table_with_comparison, SysClub
    with app.app_context():
        save_to_sys_club_table_with_comparison(db, SysClub, fifth_sheet_data)
    
    # 第五个表的数据不需要去重，直接打印
    print_array_data(fifth_sheet_data, "第五个表的数据（未去重）")

    return unique_data

def main_silent():
    """
    静默模式主程序，用于定时任务运行，不输出详细信息到控制台
    """
    try:
        # 指定Excel文件所在的目录路径
        directory_path = r"C:\Users\Administrator\Documents\导出表格\结果"

        # 读取数据
        extracted_data = extract_process_data(directory_path)

        # 如果没有提取到数据，给出提示
        if len(extracted_data) == 0:
            print("警告：未提取到任何数据，请检查文件路径和文件格式")
            return []

        # 根据第二列和第三列进行去重，保留后面的记录
        unique_data = remove_duplicates(extracted_data)

        # 将去重后的数据保存到lcoa表中
        from lcoa.app import app, db, Lcoa
        with app.app_context():
            save_to_lcoa_table(db, Lcoa, unique_data)

        # 新增功能：读取所有文件中第二个表的数据
        second_sheet_data = extract_second_sheet_data(directory_path)
        
        # 对第二个表的数据进行去重
        unique_second_sheet_data = remove_duplicates(second_sheet_data)
        
        # 将第二个表去重后的数据保存到sys_nodeal表中（使用比对更新逻辑）
        from lcoa.app import save_to_sys_nodeal_table_with_comparison, SysNodeal
        with app.app_context():
            save_to_sys_nodeal_table_with_comparison(db, SysNodeal, unique_second_sheet_data)
        
        # 新增功能：读取所有文件中第四个表的数据
        fourth_sheet_data = extract_fourth_sheet_data(directory_path)
        
        # 将第四个表的数据保存到sys_xiangxi表中（使用比对更新逻辑）
        from lcoa.app import save_to_sys_xiangxi_table_with_comparison, SysXiangxi
        with app.app_context():
            save_to_sys_xiangxi_table_with_comparison(db, SysXiangxi, fourth_sheet_data)
        
        # 新增功能：读取所有文件中第五个表的数据
        fifth_sheet_data = extract_fifth_sheet_data_for_sys_club(directory_path)
        
        # 将第五个表的数据保存到sys_club表中（使用比对更新逻辑）
        from lcoa.app import save_to_sys_club_table_with_comparison, SysClub
        with app.app_context():
            save_to_sys_club_table_with_comparison(db, SysClub, fifth_sheet_data)

        return unique_data
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    main()