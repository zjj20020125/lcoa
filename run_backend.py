import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
lcoa_backend_path = os.path.join(project_root, 'lcoa', 'vue-lcoa', 'backend')

# 将backend目录添加到Python路径中
if lcoa_backend_path not in sys.path:
    sys.path.insert(0, lcoa_backend_path)
    print(f"已添加路径到Python路径: {lcoa_backend_path}")

print(f"当前Python路径: {sys.path}")

try:
    # 直接执行app.py文件
    app_py_path = os.path.join(lcoa_backend_path, 'app.py')
    print(f"正在执行: {app_py_path}")
    
    # 设置当前工作目录
    os.chdir(lcoa_backend_path)
    print(f"已切换到目录: {lcoa_backend_path}")
    
    # 执行app.py
    exec(open('app.py').read())
        
except Exception as e:
    print(f"✗ 执行错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)