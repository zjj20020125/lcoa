"""
贝尔格莱德项目变压器风机试制计划数据导入程序
功能：读取Excel模板文件，将数据显示在控制台上（不存储到数据库）
支持：数据清洗和展示
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Tuple, List, Dict

# ==============================
# 配置参数（请根据实际环境修改）
# ==============================
CONFIG = {
    "excel_file_path": r"D:\desktop\project_manage\试制推进计划-贝尔格莱德项目变压器风机TLTF3.6F-I离心风机83319B000000-S01-2025-11-11.xls",  # Excel文件路径
}

# ==============================
# Excel数据处理类
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
            df = pd.read_excel(self.file_path, sheet_name='试制计划1', header=1)
            print(f"✅ 成功读取Excel文件，数据行数：{len(df)}")
            return df
        except Exception as e:
            print(f"❌ 读取Excel文件失败：{e}")
            raise

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据清洗"""
        # 1. 重命名列名（根据Excel结构）
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

        # 2. 去除完全空的行
        df_clean = df.dropna(how='all').copy()

        # 3. 过滤掉表头行和非数据行
        # 判断是否包含表头关键字，避免将表头作为数据处理
        header_keywords = ['项目名称', '产品名称', '关键里程碑节点', '计划开始时间', '计划结束时间']
        header_filter = pd.Series([False] * len(df_clean))
        
        for keyword in header_keywords:
            header_filter |= df_clean.astype(str).apply(lambda row: row.str.contains(keyword, case=False, na=False)).any(axis=1)
            
        df_clean = df_clean[~header_filter]

        # 过滤掉编制、会签等非数据行
        df_clean = df_clean[~df_clean['序号'].astype(str).str.contains('编制|会签', na=False)]
        df_clean = df_clean[df_clean['关键里程碑节点'].notna()]  # 只保留有关键节点的行

        # 4. 向下填充项目基础信息（项目名称、产品名称等）
        base_fields = ['项目名称', '产品名称', '产品示意图', '客户名称及订单情况']
        for field in base_fields:
            df_clean[field] = df_clean[field].fillna(method='ffill')

        # 5. 处理日期格式
        date_fields = ['计划开始时间', '计划结束时间', '实际完成时间']
        for field in date_fields:
            df_clean[field] = self._process_date(df_clean[field])

        # 6. 处理影响周期（转换为数字）
        df_clean['影响周期（天）'] = pd.to_numeric(df_clean['影响周期（天）'], errors='coerce')

        # 7. 去除空格和无效字符
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace('nan', None)
                df_clean[col] = df_clean[col].replace('/', None)

        print(f"✅ 数据清洗完成，有效数据行数：{len(df_clean)}")
        return df_clean

    def _process_date(self, date_series: pd.Series) -> pd.Series:
        """处理日期格式"""
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
        """分离主表和从表数据"""
        # 提取主表数据（去重）
        main_data = df_clean[['项目名称', '产品名称', '产品示意图', '客户名称及订单情况']].drop_duplicates()
        self.main_data_list = main_data.to_dict('records')
        print(f"✅ 提取主表数据：{len(self.main_data_list)} 条")

        # 提取从表数据
        slave_data = df_clean[['项目名称', '关键里程碑节点', '责任部门', '计划开始时间',
                               '计划结束时间', '实际完成时间', '负责人', '异常类别',
                               '影响周期（天）', '应对措施']].copy()

        # 重命名从表字段以便展示
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
# 主程序
# ==============================
def main():
    print("="*60)
    print("📋 贝尔格莱德项目数据打印程序")
    print("="*60)

    try:
        # 1. 初始化Excel处理器
        excel_processor = ExcelDataProcessor(CONFIG["excel_file_path"])
        main_data, slave_data = excel_processor.process()

        # 2. 打印主表数据
        print("\n📥 主表数据（项目基础信息）:")
        print("-"*60)
        for i, data in enumerate(main_data, 1):
            print(f"{i}. 项目名称: {data.get('项目名称', '')}")
            print(f"   产品名称: {data.get('产品名称', '')}")
            print(f"   产品示意图: {data.get('产品示意图', '')}")
            print(f"   客户名称及订单情况: {data.get('客户名称及订单情况', '')}")
            print()

        # 3. 打印从表数据
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

        print("\n" + "="*60)
        print("🎉 数据打印完成！")
        print(f"📊 打印统计：")
        print(f"   - 主表：{len(main_data)} 条项目基础信息")
        print(f"   - 从表：{len(slave_data)} 条关键节点信息")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 程序执行失败：{e}")

if __name__ == "__main__":
    main()