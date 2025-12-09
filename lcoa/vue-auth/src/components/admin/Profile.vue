<template>
    <div class="profile">
      <h1>个人信息</h1>
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar">
            <img src="https://via.placeholder.com/100" alt="用户头像">
          </div>
          <div class="profile-name">
            <h2>{{ username }}</h2>
            <p>{{ role === 'admin' ? '管理员' : '普通用户' }}</p>
          </div>
        </div>
        
        <form class="profile-form">
          <div class="form-group">
            <label>用户名</label>
            <input type="text" v-model="username" readonly>
          </div>
          <div class="form-group">
            <label>工号</label>
            <input type="text" v-model="employeeId" readonly>
          </div>
          <div class="form-group">
            <label>手机号码</label>
            <input type="tel" v-model="phone" readonly>
          </div>
          <div class="form-group">
            <label>注册时间</label>
            <input type="text" v-model="registerTime" readonly>
          </div>
          <div class="form-actions">
            <button type="button" class="btn-cancel">取消</button>
            <button type="button" class="btn-save" @click="saveProfile">保存修改</button>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  import { authAPI } from '../../services/api'
  
  export default {
    name: 'Profile',
    data() {
      return {
        username: '',
        employeeId: '',
        phone: '',
        registerTime: '',
        role: 'user'
      }
    },
    methods: {
      async loadProfile() {
        try {
          const response = await authAPI.getMe()
          if (response.code === 200) {
            const user = response.data
            this.username = user.username
            this.employeeId = user.employee_id || ''
            this.phone = user.phone || ''
            this.role = user.role
            if (user.created_at) {
              const date = new Date(user.created_at)
              this.registerTime = date.toLocaleString('zh-CN')
            }
          } else {
            console.error('获取用户信息失败:', response.message)
          }
        } catch (error) {
          console.error('获取用户信息出错:', error)
        }
      },
      saveProfile() {
        alert('个人信息已保存')
      }
    },
    mounted() {
      this.loadProfile()
    }
  }
  </script>
  
  <style scoped>
  .profile h1 {
    color: #333;
    margin-top: 0;
    margin-bottom: 25px;
  }
  
  .profile-card {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    overflow: hidden;
  }
  
  .profile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    display: flex;
    align-items: center;
    color: white;
  }
  
  .avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    overflow: hidden;
    border: 3px solid rgba(255, 255, 255, 0.3);
    margin-right: 20px;
  }
  
  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .profile-name h2 {
    margin: 0 0 5px;
    font-size: 22px;
  }
  
  .profile-name p {
    margin: 0;
    opacity: 0.9;
  }
  
  .profile-form {
    padding: 30px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #333;
  }
  
  .form-group input {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    box-sizing: border-box;
  }
  
  .form-group input:read-only {
    background-color: #f5f7fa;
    cursor: not-allowed;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 30px;
  }
  
  .btn-cancel {
    padding: 10px 20px;
    border: 1px solid #ddd;
    background-color: white;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .btn-cancel:hover {
    background-color: #f5f7fa;
  }
  
  .btn-save {
    padding: 10px 20px;
    background-color: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .btn-save:hover {
    background-color: #764ba2;
  }
  </style>