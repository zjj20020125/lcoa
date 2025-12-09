# LCOA系统API接口文档

## 1. 概述

本文档详细描述了LCOA系统的RESTful API接口，包括用户认证接口和数据查询接口。所有接口均返回JSON格式数据，包含状态码、消息和数据三个字段。

## 2. 基础响应格式

所有API接口都返回统一的JSON格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 2.1 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 3. 用户认证接口

### 3.1 用户注册

**URL**: `/api/register`  
**方法**: POST  
**描述**: 注册新用户  
**请求参数**:

```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "role": "user",
    "created_at": "2025-11-06T00:27:21",
    "updated_at": "2025-11-06T00:27:21"
  }
}
```

### 3.2 用户登录

**URL**: `/api/login`  
**方法**: POST  
**描述**: 用户登录并获取访问令牌  
**请求参数**:

```json
{
  "username": "用户名",
  "password": "密码",
  "role": "user"  // 可选，'user' 或 'admin'
}
```

**响应示例**:

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "testuser",
    "role": "user"
  }
}
```

### 3.3 获取当前用户信息

**URL**: `/api/me`  
**方法**: GET  
**描述**: 获取当前登录用户的信息  
**请求头**:

```
Authorization: Bearer <token>
```

**响应示例**:

```json
{
  "code": 200,
  "message": "获取用户信息成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "role": "user",
    "created_at": "2025-11-06T00:27:21",
    "updated_at": "2025-11-06T00:27:21"
  }
}
```

## 4. 数据查询接口

### 4.1 获取LCOA表所有数据

**URL**: `/api/lcoa`  
**方法**: GET  
**描述**: 获取LCOA表中的所有数据  
**响应示例**:

```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": "记录ID",
      "processNode": "流程节点",
      "Title": "标题",
      "processType": "流程类型",
      "Department": "部门",
      "Club": "俱乐部",
      "name_process": "流程名称",
      "user_Name": "用户名",
      "Status": "状态",
      "Process_Name": "流程名称",
      "start_time": "开始时间",
      "final_time": "结束时间",
      "inter_time": "中间时间",
      "import_date": "导入日期",
      "created_at": "创建时间",
      "updated_at": "更新时间"
    }
  ]
}
```

### 4.2 获取SysNodeal表所有数据

**URL**: `/api/sys_nodeal`  
**方法**: GET  
**描述**: 获取SysNodeal表中的所有数据  
**响应示例**:

```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "extracted_date": "2025-10-01",
      "process_node_id": "NODE001",
      "process_id": "PROC001",
      "process_title": "流程标题",
      "process_name": "流程名称",
      "process_type": "流程类型",
      "branch": "所属分部",
      "department": "所属部门",
      "node_operator": "节点操作者",
      "node_operation_type": "节点操作类型",
      "node_name": "节点名称",
      "first_receive_time": "2025-10-01 09:00:00",
      "last_process_time": "2025-10-01 17:00:00",
      "total_duration": "8小时",
      "total_timeout": "0"
    }
  ]
}
```

### 4.3 获取SysXiangxi表所有数据

**URL**: `/api/sys_xiangxi`  
**方法**: GET  
**描述**: 获取SysXiangxi表中的所有数据  
**响应示例**:

```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "extracted_date": "2025-10-01",
      "node_operator": "节点操作者",
      "department": "所属部门",
      "node_operation_type": "节点操作类型",
      "quantity": "10"
    }
  ]
}
```

### 4.4 获取SysClub表所有数据

**URL**: `/api/sys_club`  
**方法**: GET  
**描述**: 获取SysClub表中的所有数据  
**响应示例**:

```json
{
  "code": 200,
  "message": "查询成功",
  "data": [
    {
      "id": 1,
      "extracted_date": "2025-10-01",
      "department": "部门名称",
      "personnel_count": "20",
      "timeout_count": "2"
    }
  ]
}
```

## 5. 错误处理

所有接口在发生错误时都会返回相应的错误码和错误信息。例如：

```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": []
}
```

## 6. 认证说明

除用户注册接口外，其他数据查询接口都需要在请求头中携带认证信息：

```
Authorization: Bearer <token>
```

其中 `<token>` 是用户登录时返回的JWT令牌。