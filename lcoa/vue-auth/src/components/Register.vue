<template>
  <div class="register-container">
    <div class="register-form">
      <div class="form-header">
        <h2>用户注册</h2>
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">姓名:</label>
          <input 
            id="username" 
            v-model="registerForm.username" 
            type="text" 
            required 
            placeholder="请输入姓名"
          />
        </div>
        <div class="form-group">
          <label for="employee_id">工号:</label>
          <input 
            id="employee_id" 
            v-model="registerForm.employee_id" 
            type="text" 
            required 
            placeholder="请输入工号"
          />
        </div>
        <div class="form-group">
          <label for="phone">手机号:</label>
          <input 
            id="phone" 
            v-model="registerForm.phone" 
            type="text" 
            placeholder="请输入手机号"
          />
        </div>
        <div class="form-group">
          <label for="password">密码:</label>
          <input 
            id="password" 
            v-model="registerForm.password" 
            type="password" 
            required 
            placeholder="请输入密码"
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认密码:</label>
          <input 
            id="confirmPassword" 
            v-model="registerForm.confirmPassword" 
            type="password" 
            required 
            placeholder="请再次输入密码"
          />
        </div>
        <div class="form-actions">
          <button type="submit" class="register-btn">注册</button>
        </div>
      </form>
      <div class="form-footer">
        <p>已有账号？<router-link to="/Login">立即登录</router-link></p>
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
  name: 'Register',
  data() {
    return {
      registerForm: {
        username: '',
        employee_id: '',
        phone: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  setup() {
    const router = useRouter()
    return { router }
  },
  methods: {
    async handleRegister() {
      // 检查两次输入的密码是否一致
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        ElMessage.error('两次输入的密码不一致')
        return
      }

      try {
        const res = await authAPI.register({
          username: this.registerForm.username,
          employee_id: this.registerForm.employee_id,
          phone: this.registerForm.phone,
          password: this.registerForm.password
        })

        if (res.code === 200) {
          // 注册成功，显示成功消息并跳转到登录页面
          ElMessage.success('注册成功')
          this.router.push('/Login')
        } else {
          // 注册失败，显示错误消息
          ElMessage.error(res.message || '注册失败')
        }
      } catch (error) {
        console.error('注册出错:', error)
        ElMessage.error('注册过程中出现错误')
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: url('../image/all.jpg') center/auto no-repeat;
  background-size: contain;
  padding: 20px;
}

.register-form {
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

.register-btn {
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

.register-btn:hover {
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