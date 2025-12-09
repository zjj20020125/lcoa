import os
import re
import sys
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==============================
# Excel数据处理类（参考tableprint.py实现）
# ==============================
class ExcelDataProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.main_data_list = []  # 主表数据列表
        self.slave_data_list = []  # 从表数据列表

    def read_excel(self) -> pd.DataFrame:
        """读取Excel文件"""
        try:
            # 读取Excel文件，使用第二行作为列名
            df = pd.read_excel(self.file_path, sheet_name=0, header=1)  # 读取第一个工作表
            print(f"✅ 成功读取Excel文件，数据行数：{len(df)}")
            return df
        except Exception as e:
            print(f"❌ 读取Excel文件失败：{e}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗（参考tableprint.py实现）"""
        # 重命名列名（根据Excel结构）
        # 注意：这里的列名映射可能需要根据实际Excel结构调整
        column_mapping = {
            'XXX新产品试制专项计划': '序号',
            'Unnamed: 1': '项目名称',
            'Unnamed: 2': '产品名称',
            'Unnamed: 3': '产品示意图',
            'Unnamed: 4': '客户名称及订单情况',
            'Unnamed: 5': '关键里程碑节点',
            'Unnamed: 6': '责任部门',
            'Unnamed: 7': '计划开始时间',
            'Unnamed: 8': '计划结束时间',
            'Unnamed: 9': '实际完成时间',
            'Unnamed: 10': '负责人',
            'Unnamed: 11': '异常类别',
            'Unnamed: 12': '影响周期（天）',
            'Unnamed: 13': '应对措施'
        }
        df = df.rename(columns=column_mapping)

        # 去除完全空的行
        df_clean = df.dropna(how='all').copy()

        # 过滤掉表头行和非数据行
        # 判断是否包含表头关键字，避免将表头作为数据处理
        header_keywords = ['项目名称', '产品名称', '关键里程碑节点', '计划开始时间', '计划结束时间']
        header_filter = pd.Series([False] * len(df_clean))
        
        for keyword in header_keywords:
            header_filter |= df_clean.astype(str).apply(lambda row: row.str.contains(keyword, case=False, na=False)).any(axis=1)
            
        df_clean = df_clean[~header_filter]

        # 过滤掉编制、会签等非数据行
        df_clean = df_clean[~df_clean['序号'].astype(str).str.contains('编制|会签', na=False)]
        df_clean = df_clean[df_clean['关键里程碑节点'].notna()]  # 只保留有关键节点的行

        # 向下填充项目基础信息（项目名称、产品名称等）
        base_fields = ['项目名称', '产品名称', '产品示意图', '客户名称及订单情况']
        for field in base_fields:
            df_clean[field] = df_clean[field].fillna(method='ffill')

        # 处理日期格式
        date_fields = ['计划开始时间', '计划结束时间', '实际完成时间']
        for field in date_fields:
            df_clean[field] = self._process_date(df_clean[field])

        # 处理影响周期（转换为数字）
        df_clean['影响周期（天）'] = pd.to_numeric(df_clean['影响周期（天）'], errors='coerce')

        # 去除空格和无效字符
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace('nan', None)
                df_clean[col] = df_clean[col].replace('/', None)

        print(f"✅ 数据清洗完成，有效数据行数：{len(df_clean)}")
        return df_clean

    def _process_date(self, date_series: pd.Series) -> pd.Series:
        """处理日期格式（参考tableprint.py实现）"""
        def parse_date(date_val):
            if pd.isna(date_val) or date_val == '/' or str(date_val).strip() == '':
                return None
            try:
                # 处理Excel日期格式和字符串格式
                if isinstance(date_val, (int, float)):
                    # Excel日期序列号转换
                    return pd.to_datetime('1900-01-01') + pd.Timedelta(days=date_val - 2)
                else:
                    # 字符串日期转换
                    return pd.to_datetime(str(date_val).strip(), errors='coerce').date()
            except Exception:
                return None

        return date_series.apply(parse_date)

    def split_main_slave_data(self, df_clean: pd.DataFrame) -> None:
        """分离主表和从表数据（参考tableprint.py实现）"""
        # 提取主表数据（去重）
        main_data = df_clean[['项目名称', '产品名称', '产品示意图', '客户名称及订单情况']].drop_duplicates()
        self.main_data_list = main_data.to_dict('records')
        print(f"✅ 提取主表数据：{len(self.main_data_list)} 条")

        # 提取从表数据
        slave_data = df_clean[['项目名称', '关键里程碑节点', '责任部门', '计划开始时间',
                               '计划结束时间', '实际完成时间', '负责人', '异常类别',
                               '影响周期（天）', '应对措施']].copy()

        # 重命名从表字段以便处理
        slave_data.rename(columns={
            '关键里程碑节点': 'milestone_name',
            '责任部门': 'responsible_department',
            '计划开始时间': 'plan_start_date',
            '计划结束时间': 'plan_end_date',
            '实际完成时间': 'actual_finish_date',
            '负责人': 'responsible_person',
            '异常类别': 'exception_type',
            '影响周期（天）': 'impact_days',
            '应对措施': 'response_measures'
        }, inplace=True)

        self.slave_data_list = slave_data.to_dict('records')
        print(f"✅ 提取从表数据：{len(self.slave_data_list)} 条")

    def process(self) -> Tuple[List[Dict], List[Dict]]:
        """完整数据处理流程"""
        print("📊 开始Excel数据处理...")
        df = self.read_excel()
        df_clean = self.clean_data(df)
        self.split_main_slave_data(df_clean)
        print("✅ Excel数据处理完成")
        return self.main_data_list, self.slave_data_list


# ==============================
# 数据库存储类
# ==============================
class DatabaseStorage:
    def __init__(self):
        # 初始化Flask应用和数据库连接
        from lcoa.app import app, db, SysProject, SysProjectMilestone
        self.app = app
        self.db = db
        self.SysProject = SysProject
        self.SysProjectMilestone = SysProjectMilestone

    def save_data(self, main_data: List[Dict], slave_data: List[Dict]):
        """将数据存储到数据库"""
        with self.app.app_context():
            try:
                # 存储主表数据到SysProject表
                project_map = {}  # 用于存储项目名称到项目对象的映射
                for item in main_data:
                    # 检查项目是否已存在
                    existing_project = self.SysProject.query.filter_by(
                        project_name=item.get('项目名称', '')
                    ).first()
                    
                    if existing_project:
                        # 更新现有项目
                        existing_project.product_name = item.get('产品名称', '')
                        existing_project.product_image = item.get('产品示意图', '')
                        # 分离客户名称和订单情况
                        customer_info = item.get('客户名称及订单情况', '')
                        if customer_info:
                            parts = customer_info.split(',', 1)
                            existing_project.customer_name = parts[0]
                            existing_project.order_status = parts[1] if len(parts) > 1 else ''
                        else:
                            existing_project.customer_name = ''
                            existing_project.order_status = ''
                        existing_project.updated_at = datetime.utcnow()
                        project_map[item.get('项目名称', '')] = existing_project
                    else:
                        # 创建新项目
                        # 分离客户名称和订单情况
                        customer_info = item.get('客户名称及订单情况', '')
                        customer_name = ''
                        order_status = ''
                        if customer_info:
                            parts = customer_info.split(',', 1)
                            customer_name = parts[0]
                            order_status = parts[1] if len(parts) > 1 else ''
                        
                        project = self.SysProject(
                            project_name=item.get('项目名称', ''),
                            product_name=item.get('产品名称', ''),
                            product_image=item.get('产品示意图', ''),
                            customer_name=customer_name,
                            order_status=order_status
                        )
                        self.db.session.add(project)
                        self.db.session.flush()  # 获取项目ID但不提交
                        project_map[item.get('项目名称', '')] = project
                
                # 删除该项目下所有现有的里程碑节点（避免重复）
                for project_name, project in project_map.items():
                    self.SysProjectMilestone.query.filter_by(project_id=project.id).delete()
                
                # 存储从表数据到SysProjectMilestone表
                for item in slave_data:
                    project_name = item.get('项目名称', '')
                    if project_name in project_map:
                        project = project_map[project_name]
                        milestone = self.SysProjectMilestone(
                            project_id=project.id,
                            milestone=item.get('milestone_name', ''),
                            responsible_department=item.get('responsible_department', ''),
                            planned_start_time=item.get('plan_start_date', ''),
                            planned_end_time=item.get('plan_end_date', ''),
                            actual_completion_time=item.get('actual_finish_date', ''),
                            responsible_person=item.get('responsible_person', ''),
                            exception_type=item.get('exception_type', ''),
                            impact_cycle=str(item.get('impact_days', '')) if item.get('impact_days') is not None else '',
                            response_measures=item.get('response_measures', '')
                        )
                        self.db.session.add(milestone)
                
                # 提交事务
                self.db.session.commit()
                print(f"✅ 成功存储 {len(main_data)} 个项目和 {len(slave_data)} 个里程碑节点到数据库")
                
            except Exception as e:
                self.db.session.rollback()
                print(f"❌ 存储数据到数据库时出错：{e}")
                raise


def process_and_store_excel_data(file_path):
    """
    处理并存储Excel数据到数据库
    
    Args:
        file_path (str): Excel文件路径
    """
    try:
        # 初始化Excel处理器
        processor = ExcelDataProcessor(file_path)
        main_data, slave_data = processor.process()
        
        # 打印主表数据
        print("\n📥 主表数据（项目基础信息）:")
        print("-"*60)
        for i, data in enumerate(main_data, 1):
            print(f"{i}. 项目名称: {data.get('项目名称', '')}")
            print(f"   产品名称: {data.get('产品名称', '')}")
            print(f"   产品示意图: {data.get('产品示意图', '')}")
            print(f"   客户名称及订单情况: {data.get('客户名称及订单情况', '')}")
            print()

        # 打印从表数据
        print("\n📥 从表数据（关键节点信息）:")
        print("-"*60)
        for i, data in enumerate(slave_data, 1):
            print(f"{i}. 项目名称: {data.get('项目名称', '')}")
            print(f"   关键里程碑节点: {data.get('milestone_name', '')}")
            print(f"   责任部门: {data.get('responsible_department', '')}")
            print(f"   计划开始时间: {data.get('plan_start_date', '')}")
            print(f"   计划结束时间: {data.get('plan_end_date', '')}")
            print(f"   实际完成时间: {data.get('actual_finish_date', '')}")
            print(f"   负责人: {data.get('responsible_person', '')}")
            print(f"   异常类别: {data.get('exception_type', '')}")
            print(f"   影响周期（天）: {data.get('impact_days', '')}")
            print(f"   应对措施: {data.get('response_measures', '')}")
            print()

        # 存储数据到数据库
        storage = DatabaseStorage()
        storage.save_data(main_data, slave_data)
        
        print("\n" + "="*60)
        print("🎉 数据处理和存储完成！")
        print(f"📊 处理统计：")
        print(f"   - 主表：{len(main_data)} 条项目基础信息")
        print(f"   - 从表：{len(slave_data)} 条关键节点信息")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 程序执行失败：{e}")
        import traceback
        traceback.print_exc()


def read_filenames_from_directory(directory_path):
    """
    读取指定目录下所有文件的文件名

    Args:
        directory_path (str): 目录路径

    Returns:
        list: 包含所有文件名的列表
    """
    try:
        # 获取目录下的所有文件和文件夹
        entries = os.listdir(directory_path)

        # 筛选出文件（而不是文件夹）
        filenames = [entry for entry in entries if os.path.isfile(os.path.join(directory_path, entry))]

        return filenames
    except FileNotFoundError:
        print(f"错误：找不到指定的目录 {directory_path}")
        return []
    except PermissionError:
        print(f"错误：没有权限访问目录 {directory_path}")
        return []
    except Exception as e:
        print(f"发生错误：{e}")
        return []

def read_all_entries_from_directory(directory_path):
    """
    读取指定目录下所有的文件和文件夹名称

    Args:
        directory_path (str): 目录路径

    Returns:
        list: 包含所有条目名称的列表
    """
    try:
        entries = os.listdir(directory_path)
        return entries
    except FileNotFoundError:
        print(f"错误：找不到指定的目录 {directory_path}")
        return []
    except PermissionError:
        print(f"错误：没有权限访问目录 {directory_path}")
        return []
    except Exception as e:
        print(f"发生错误：{e}")
        return []

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

    # 获取目录下的所有文件
    filenames = read_filenames_from_directory(directory_path)
    
    # 遍历所有文件
    for filename in filenames:
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
            print(f"未能从文件名中提取日期信息: {filename}")

    if closest_file:
        return closest_file, min_diff_days, closest_date
    else:
        return None, None, None

def read_all_sheets_from_closest_file(directory_path):
    """
    读取最接近当前日期的文件中每个表中的所有数据
    
    Args:
        directory_path (str): 目录路径
        
    Returns:
        list: 包含5个数组的列表，每个数组存储对应工作表的所有数据行
    """
    # 查找最接近当前日期的文件
    closest_file, diff_days, closest_date = find_closest_file_to_current_date(directory_path)
    
    if not closest_file:
        print("未找到包含日期信息的文件")
        return [None] * 5
    
    file_path = os.path.join(directory_path, closest_file)
    print(f"\n正在读取文件: {closest_file}")
    
    # 检查是否为Excel文件
    if not closest_file.endswith(('.xlsx', '.xls')) or closest_file.startswith('~$'):
        print(f"文件 {closest_file} 不是有效的Excel文件")
        return [None] * 5
    
    # 获取从文件名提取的日期字符串
    extracted_date_str = closest_date.strftime('%Y-%m-%d') if closest_date else ''
    
    # 存储5个工作表的数据
    sheet_arrays = [[] for _ in range(5)]
    
    try:
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"文件包含 {len(sheet_names)} 个工作表: {sheet_names}")
        
        # 确保至少有5个工作表
        if len(sheet_names) < 5:
            print(f"警告: 文件 {closest_file} 只有 {len(sheet_names)} 个工作表，少于预期的5个")
            # 只处理存在的工作表
            max_sheets = len(sheet_names)
        else:
            max_sheets = 5
            
        # 读取每个工作表的数据
        for i in range(max_sheets):
            print(f"\n正在处理第 {i+1} 个工作表: {sheet_names[i]}")
            try:
                # 读取第i个工作表
                df = pd.read_excel(file_path, sheet_name=i)
                
                # 如果DataFrame为空，添加空数组
                if df.empty:
                    print(f"工作表 {sheet_names[i]} 是空的")
                    sheet_arrays[i] = []
                    continue
                
                # 将每行数据添加到对应的数组中
                for index, row in df.iterrows():
                    # 将行数据转换为列表，处理NaN值，并在第一列添加提取的日期
                    row_data = [extracted_date_str] + [str(val) if pd.notna(val) else '' for val in row]
                    sheet_arrays[i].append(row_data)
                
                print(f"从工作表 {sheet_names[i]} 读取了 {len(sheet_arrays[i])} 行数据")
                    
            except Exception as e:
                print(f"读取工作表 {sheet_names[i]} 时出错: {e}")
                sheet_arrays[i] = []
                
    except Exception as e:
        print(f"读取文件 {closest_file} 时出错: {e}")
        return [None] * 5
    
    return sheet_arrays

if __name__ == "__main__":
    # 指定要读取的目录路径
    target_directory = r'C:\Users\Administrator\Documents\导出表格\结果'

    print(f"正在读取目录: {target_directory}")

    # 只获取文件名
    filenames = read_filenames_from_directory(target_directory)
    print("\n仅文件名:")
    print("-" * 50)
    if filenames:
        for i, filename in enumerate(filenames, 1):
            print(f"{i}. {filename}")
    else:
        print("没有找到文件或无法访问目录")

    # 获取所有条目（包括文件和文件夹）
    all_entries = read_all_entries_from_directory(target_directory)
    print("\n\n所有条目:")
    print("-" * 50)
    if all_entries:
        for i, entry in enumerate(all_entries, 1):
            print(f"{i}. {entry}")
    else:
        print("没有找到条目或无法访问目录")

    # 查找最接近当前日期的文件
    print("\n\n查找最接近当前日期的文件:")
    print("-" * 50)
    closest_file, diff_days, closest_date = find_closest_file_to_current_date(target_directory)
    
    if closest_file:
        print(f"最接近当前日期的文件: {closest_file}")
        print(f"提取的日期: {closest_date.strftime('%Y-%m-%d')}")
        print(f"与当前日期相差: {diff_days} 天")
        
        # 处理并存储Excel数据
        file_path = os.path.join(target_directory, closest_file)
        process_and_store_excel_data(file_path)
    else:
        print("未找到包含日期信息的文件")
        
    # 读取最接近当前日期的文件中每个表中的所有数据
    print("\n\n读取最接近当前日期的文件中每个表的数据:")
    print("-" * 50)
    sheet_arrays = read_all_sheets_from_closest_file(target_directory)
    
    for i, sheet_data in enumerate(sheet_arrays):
        if sheet_data is None:
            print(f"第 {i+1} 个工作表: 无法读取")
        elif len(sheet_data) == 0:
            print(f"第 {i+1} 个工作表: 空工作表")
        else:
            print(f"第 {i+1} 个工作表: 包含 {len(sheet_data)} 行数据")
            # 显示前几行作为示例
            for j, row in enumerate(sheet_data[:3]):  # 只显示前3行
                print(f"  行 {j+1}: {row}")
            if len(sheet_data) > 3:
                print(f"  ... 还有 {len(sheet_data) - 3} 行数据")