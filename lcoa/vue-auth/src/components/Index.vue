<template>
  <div class="index-page">
    <div class="hero-section">
      <h1>欢迎使用项目管理系统</h1>
      <p>高效管理您的项目和团队协作</p>
      <div class="cta-buttons">
        <button @click="goToLogin" class="btn primary">立即登录</button>
        <button @click="goToRegister" class="btn secondary">注册账号</button>
      </div>
    </div>
    
    <div class="features-section">
      <div class="feature">
        <div class="feature-icon">📊</div>
        <h3>数据看板</h3>
        <p>实时监控项目进展和关键指标</p>
      </div>
      <div class="feature">
        <div class="feature-icon">📁</div>
        <h3>项目管理</h3>
        <p>全面管理项目生命周期和里程碑</p>
      </div>
      <div class="feature">
        <div class="feature-icon">👥</div>
        <h3>团队协作</h3>
        <p>清晰的成员分工和权限控制</p>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'IndexPage',
  setup() {
    const router = useRouter()
    
    const goToLogin = () => {
      router.push('/Login')
    }
    
    const goToRegister = () => {
      router.push('/Register')
    }
    
    return {
      goToLogin,
      goToRegister
    }
  }
}
</script>

<style scoped>
.index-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.hero-section {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.hero-section p {
  font-size: 1.2rem;
  margin-bottom: 30px;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.btn {
  padding: 12px 30px;
  border: none;
  border-radius: 30px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn.primary {
  background-color: #4A90E2;
  color: white;
}

.btn.primary:hover {
  background-color: #357AE8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn.secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn.secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.features-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.feature {
  text-align: center;
  padding: 30px;
  border-radius: 8px;
  background: #f8f9fa;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.feature:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature h3 {
  margin-bottom: 15px;
  color: #333;
}

.feature p {
  color: #666;
  line-height: 1.6;
}
</style>