<template>
  <div class="settings-container">
    <h2>⚙️ 账户设置</h2>
    <div class="settings-form">
      <div class="form-group">
        <label>用户名</label>
        <input type="text" v-model="form.username" placeholder="请输入用户名">
      </div>
      
    
      <div class="form-group">
        <label>新密码</label>
        <input type="password" v-model="form.newPassword" placeholder="请输入新密码">
      </div>
      
      <div class="form-group">
        <label>确认密码</label>
        <input type="password" v-model="form.confirmPassword" placeholder="请再次输入新密码">
      </div>
      
      <button class="save-btn" @click="saveSettings">保存设置</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      form: {
        username: '',
        email: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    saveSettings() {
      // 这里应该是保存设置的逻辑
      alert('设置已保存');
    }
  }
}
</script>

<style scoped>
.settings-container {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.settings-container h2 {
  margin-top: 0;
  color: #333;
  font-size: 24px;
  margin-bottom: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.save-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
</style>