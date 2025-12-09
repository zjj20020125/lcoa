<template>
  <div class="login-container">
    <div class="login-form">
      <div class="form-header">
        <h2>用户登录</h2>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">姓名:</label>
          <input 
            id="username" 
            v-model="loginForm.username" 
            type="text" 
            required 
            placeholder="请输入姓名"
          />
        </div>
        <div class="form-group">
          <label for="employee_id">工号:</label>
          <input 
            id="employee_id" 
            v-model="loginForm.employee_id" 
            type="text" 
            placeholder="请输入工号（可选）"
          />
        </div>
        <div class="form-group">
          <label for="password">密码:</label>
          <input 
            id="password" 
            v-model="loginForm.password" 
            type="password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-actions">
          <button type="submit" class="login-btn">登录</button>
        </div>
      </form>
      <div class="form-footer">
        <p>还没有账号？<router-link to="/Register">立即注册</router-link></p>
        <p><router-link to="/">返回首页</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../services/api'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        employee_id: '',
        password: ''
      }
    }
  },
  setup() {
    const router = useRouter()
    return { router }
  },
  methods: {
    async handleLogin() {
      try {
        const requestData = {
          username: this.loginForm.username,
          password: this.loginForm.password
        };
        
        // 只有当工号不为空时才发送工号
        if (this.loginForm.employee_id && this.loginForm.employee_id.trim() !== '') {
          requestData.employee_id = this.loginForm.employee_id;
        }
        
        const res = await authAPI.login(requestData)
        
        if (res.code === 200) {
          // 登录成功，保存token和其他信息到localStorage
          localStorage.setItem('token', res.data.token)
          localStorage.setItem('username', res.data.username)
          localStorage.setItem('role', res.data.role)
          
          // 显示成功消息
          ElMessage.success('登录成功')
          
          // 根据角色跳转到不同页面
          if (res.data.role === 'admin') {
            this.router.push('/admin')
          } else {
            this.router.push('/user-center')
          }
        } else {
          // 登录失败，显示错误消息，但不跳转和刷新页面
          ElMessage.error(res.message || '登录失败')
        }
      } catch (error) {
        console.error('登录出错:', error)
        // 发生错误时只显示错误消息，不跳转和刷新页面
        ElMessage.error(error.response?.data?.message || '登录过程中出现错误')
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: url('../image/all.jpg') center/auto no-repeat;
  background-size: contain;
  padding: 20px;
}

.login-form {
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 450px;
  overflow: hidden;
}

.form-header {
  background: linear-gradient(90deg, #E0F7FF 0%, #B0E0E6 100%);
  padding: 25px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.form-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

form {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 16px;
  transition: all 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4A90E2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #87CEFA 0%, #6495ED 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.form-footer {
  text-align: center;
  padding: 20px 30px;
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
}

.form-footer p {
  margin: 10px 0;
  color: #666;
}

.form-footer a {
  color: #4A90E2;
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>