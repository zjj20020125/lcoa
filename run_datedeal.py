#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DateDeal运行脚本
用于解决模块导入路径问题，确保正确加载所有依赖模块
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"已添加项目根目录到Python路径: {project_root}")

print(f"当前Python路径: {sys.path}")

try:
    # 导入并运行datedeal主程序
    from lcoa.datedeal.main import main
    
    if __name__ == "__main__":
        print("开始运行DateDeal数据处理程序...")
        result = main()
        print("DateDeal数据处理程序运行完成")
        
except ImportError as e:
    print(f"导入模块时发生错误: {e}")
    print("请检查以下几点:")
    print("1. 确保已安装所有依赖项:")
    print("   pip install -r lcoa/requirement.txt")
    print("2. 确保项目结构完整且未损坏")
    print("3. 确保数据库连接配置正确")
    sys.exit(1)
except Exception as e:
    print(f"运行程序时发生错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)