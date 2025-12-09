import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"项目根目录: {project_root}")
print(f"Python路径: {sys.path}")

try:
    # 现在可以安全导入模块
    from lcoa.datedeal.main import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装所有依赖项:")
    print("pip install -r lcoa/vue-lcoa/backend/requirements.txt")
    sys.exit(1)