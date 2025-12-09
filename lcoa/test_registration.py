"""
测试注册功能，包括新的工号和手机号字段
"""

import requests
import json

# 测试数据
test_user = {
    "username": "testuser123",
    "password": "testpass123",
    "employee_id": "EMP001",
    "phone": "13812345678"
}

# 发送注册请求
response = requests.post(
    "http://127.0.0.1:5000/api/register",
    headers={"Content-Type": "application/json"},
    data=json.dumps(test_user)
)

print("注册响应:")
print(f"状态码: {response.status_code}")
print(f"响应内容: {response.json()}")