#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目数据导入脚本
用于从Excel文件导入项目和里程碑数据到数据库
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def import_projects_from_excel_cli():
    """命令行版本的项目导入功能"""
    try:
        # 导入必要的模块
        from datedeal.import_projects import batch_import_projects_from_directory
        
        # 获取目录参数
        if len(sys.argv) < 2:
            print("使用方法: python run_import_projects.py <excel文件目录>")
            return
        
        directory_path = sys.argv[1]
        if not os.path.exists(directory_path):
            print(f"错误: 目录 '{directory_path}' 不存在")
            return
        
        print(f"开始从目录 '{directory_path}' 导入项目数据...")
        result = batch_import_projects_from_directory(directory_path)
        
        if result['success']:
            print(f"导入成功: {result['message']}")
            if 'details' in result:
                for detail in result['details']:
                    print(f"  文件: {detail.get('file_name', 'unknown')}")
                    if detail.get('success'):
                        print(f"    成功导入 {len(detail.get('imported_projects', []))} 个项目")
                    else:
                        print(f"    导入失败: {detail.get('message')}")
        else:
            print(f"导入失败: {result['message']}")
            
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_projects_from_excel_cli()