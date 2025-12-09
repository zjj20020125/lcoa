#!/bin/bash
# 项目部署脚本

echo "开始部署项目..."

# 检查是否安装了 Python
if ! command -v python3 &> /dev/null
then
    echo "未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查是否安装了 Node.js
if ! command -v node &> /dev/null
then
    echo "未找到 Node.js，请先安装 Node.js"
    exit 1
fi

# 检查是否安装了 MySQL
if ! command -v mysql &> /dev/null
then
    echo "未找到 MySQL，请先安装 MySQL"
    exit 1
fi

# 创建虚拟环境
echo "创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装 Python 依赖
echo "安装 Python 依赖..."
pip install -r production_requirements.txt

# 安装前端依赖
echo "安装前端依赖..."
cd lcoa/vue-auth
npm install

# 返回上级目录
cd ../..

# 数据库配置提示
echo "请确保已创建数据库并配置好数据库连接信息"
echo "创建数据库命令示例:"
echo "mysql -u root -p -e \"CREATE DATABASE lcoa;\""

# 构建前端项目
echo "构建前端项目..."
cd lcoa/vue-auth
npm run build
cd ../..

echo "部署完成！"
echo ""
echo "启动服务步骤："
echo "1. 启动后端服务: python lcoa/app.py"
echo "2. 启动前端服务: cd lcoa/vue-auth && npm run dev"