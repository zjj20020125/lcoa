<template>
  <div class="home">
    <h2>欢迎回来，{{ username }}！</h2>
    <p>你的身份：{{ role === 'admin' ? '管理员' : '普通用户' }}</p>
    <p>注册时间：{{ createdAt }}</p>

    <div class="button-group">
      <button @click="toRolePage">进入{{ role === 'admin' ? '管理员' : '用户' }}页面</button>
      <button @click="logout">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../services/api'

const router = useRouter()
const username = ref('')
const role = ref('')
const createdAt = ref('')

// 获取用户信息
const getInfo = async () => {
  try {
    const res = await authAPI.getMe()
    if (res.code === 200) {
      username.value = res.data.username
      role.value = res.data.role
      createdAt.value = res.data.created_at
    }
  } catch (error) {
    console.error('获取信息失败', error)
  }
}

// 跳转到对应身份的页面
const toRolePage = () => {
  router.push(role.value === 'admin' ? '/admin' : '/user')
}

// 退出登录
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('role')
  router.push('/login')
}

onMounted(getInfo)
</script>

<style scoped>
.home {
  text-align: center;
  margin-top: 50px;
}
.button-group {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}
button {
  padding: 8px 16px;
  cursor: pointer;
}
</style>