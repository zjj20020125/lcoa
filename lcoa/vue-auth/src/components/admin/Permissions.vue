<template>
  <div class="permissions-container">
    <h2>🔑 权限设置</h2>
    <div class="permissions-content">
      <div class="user-list-header">
        <h3>用户列表</h3>
        <button class="refresh-btn" @click="fetchUsers">刷新</button>
      </div>
      
      <div class="user-table-container">
        <table class="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>角色</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>
                <span :class="['role-badge', user.role]">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button 
                  v-if="user.role === 'user'" 
                  class="promote-btn" 
                  @click="promoteToAdmin(user)"
                >
                  设为管理员
                </button>
                <button 
                  v-else 
                  class="demote-btn" 
                  @click="demoteToUser(user)"
                  :disabled="user.username === 'admin'"
                >
                  设为用户
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        加载中...
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { userAPI } from '../../services/api'
import { useRouter } from 'vue-router'

export default {
  name: 'Permissions',
  setup() {
    const router = useRouter();
    return { router };
  },
  data() {
    return {
      users: [],
      loading: false,
      error: null
    }
  },
  methods: {
    // 获取所有用户
    async fetchUsers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await userAPI.getAllUsers()
        if (response.code === 200) {
          this.users = response.data
        } else {
          this.error = response.message || '获取用户列表失败'
        }
      } catch (err) {
        if (err.response && err.response.status === 401) {
          this.error = '认证已过期，请重新登录';
          // 清除本地存储的认证信息
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          localStorage.removeItem('role');
          localStorage.removeItem('currentUser');
          // 跳转到登录页
          this.router.push('/Login');
        } else {
          this.error = err.message || '获取用户列表失败'
        }
        console.error('获取用户列表失败:', err)
      } finally {
        this.loading = false
      }
    },
    
    // 提升用户为管理员
    async promoteToAdmin(user) {
      if (confirm(`确定要将用户 "${user.username}" 设置为管理员吗？`)) {
        try {
          const response = await userAPI.updateUserRole(user.id, 'admin')
          if (response.code === 200) {
            // 更新本地数据
            const index = this.users.findIndex(u => u.id === user.id)
            if (index !== -1) {
              this.users[index] = response.data
            }
            alert(`用户 "${user.username}" 已被设置为管理员`)
          } else {
            alert(response.message || '设置管理员失败')
          }
        } catch (err) {
          alert(err.message || '设置管理员失败')
          console.error('设置管理员失败:', err)
        }
      }
    },
    
    // 降级管理员为普通用户
    async demoteToUser(user) {
      if (user.username === 'admin') {
        alert('不能降级初始管理员账户！')
        return
      }
      
      if (confirm(`确定要将管理员 "${user.username}" 降级为普通用户吗？`)) {
        try {
          const response = await userAPI.updateUserRole(user.id, 'user')
          if (response.code === 200) {
            // 更新本地数据
            const index = this.users.findIndex(u => u.id === user.id)
            if (index !== -1) {
              this.users[index] = response.data
            }
            alert(`用户 "${user.username}" 已被降级为普通用户`)
          } else {
            alert(response.message || '降级用户失败')
          }
        } catch (err) {
          alert(err.message || '降级用户失败')
          console.error('降级用户失败:', err)
        }
      }
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
  },
  mounted() {
    // 组件挂载时获取用户列表
    this.fetchUsers()
  }
}
</script>

<style scoped>
.permissions-container {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.permissions-container h2 {
  margin-top: 0;
  color: #333;
  font-size: 24px;
  margin-bottom: 25px;
}

.user-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.user-list-header h3 {
  margin: 0;
  color: #333;
}

.refresh-btn {
  background-color: #667eea;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background-color: #5a6fd8;
  transform: translateY(-2px);
}

.user-table-container {
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.user-table th,
.user-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
}

.user-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.role-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background-color: #ffebee;
  color: #c62828;
}

.role-badge.user {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.promote-btn,
.demote-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.promote-btn {
  background-color: #1976d2;
  color: white;
}

.promote-btn:hover {
  background-color: #1565c0;
}

.demote-btn {
  background-color: #f57c00;
  color: white;
}

.demote-btn:hover:not(:disabled) {
  background-color: #ef6c00;
}

.demote-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.loading,
.error {
  text-align: center;
  padding: 20px;
  margin: 20px 0;
}

.loading {
  color: #666;
}

.error {
  color: #f44336;
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
}
</style>