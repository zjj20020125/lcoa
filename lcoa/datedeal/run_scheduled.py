"""
计划任务运行脚本
用于在后台定时运行数据处理脚本
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 设置日志
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'scheduled_task.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """主函数，用于计划任务调用"""
    try:
        logging.info("开始执行定时任务")
        print(f"[{datetime.now()}] 开始执行定时任务")
        
        # 导入并运行主要的数据处理函数
        from lcoa.datedeal.main import main as process_data
        result = process_data()
        
        logging.info(f"定时任务执行完成，处理了 {len(result) if result else 0} 条数据")
        print(f"[{datetime.now()}] 定时任务执行完成")
        
    except Exception as e:
        error_msg = f"执行定时任务时发生错误: {str(e)}"
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        print(f"[{datetime.now()}] {error_msg}")

if __name__ == "__main__":
    import traceback
    main()