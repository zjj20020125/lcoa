# 项目部署指南

## 依赖环境

### 后端依赖
- Python 3.7+
- MySQL 5.7+

### 前端依赖
- Node.js 14+
- npm 6+

## 生产环境部署步骤

### 1. 克隆代码
```bash
git clone https://github.com/zjj20020125/lcoa.git
cd lcoa
```

### 2. 安装依赖

#### Python 依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r production_requirements.txt
```

#### Node.js 依赖
```bash
cd lcoa/vue-auth
npm install
```

### 3. 数据库配置

1. 创建数据库：
```sql
CREATE DATABASE lcoa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 配置数据库连接信息（在 app.py 中修改）：
```python
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'lcoa'
```

### 4. 初始化数据
```bash
# 运行数据初始化脚本
python lcoa/reset_and_seed_projects.py
```

### 5. 构建前端
```bash
cd lcoa/vue-auth
npm run build
```

### 6. 启动服务

#### 开发环境
```bash
# 启动后端服务
python lcoa/app.py

# 启动前端服务（新终端窗口）
cd lcoa/vue-auth
npm run dev
```

#### 生产环境
推荐使用 Gunicorn 和 Nginx 部署：

1. 安装 Gunicorn：
```bash
pip install gunicorn
```

2. 启动后端服务：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. 配置 Nginx 提供前端静态文件服务和反向代理后端请求。

### 7. 访问应用
- 前端地址：http://localhost:5173
- 后端API地址：http://localhost:5000

## 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否启动
   - 检查数据库连接配置是否正确
   - 检查防火墙设置

2. **依赖安装失败**
   - 检查网络连接
   - 使用国内镜像源加速下载
   - 确保 Python 和 Node.js 版本符合要求

3. **端口占用**
   - 修改应用启动端口
   - 关闭占用端口的进程