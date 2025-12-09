<template>
  <div class="admin-home">
    <div class="welcome-section">
      <h1>管理中心首页</h1>
      <p>欢迎{{ username }}来到结构件数据管理平台</p>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <h3>系统状态</h3>
        <p class="stat-number">运行正常</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <h3>今日访问</h3>
        <p class="stat-number">128</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📁</div>
        <h3>项目总数</h3>
        <p class="stat-number">24</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <h3>用户总数</h3>
        <p class="stat-number">15</p>
      </div>
    </div>
    
    <div class="recent-activity">
      <h2>最近活动</h2>
      <div class="activity-list">
        <div class="activity-item" v-for="item in recentActivities" :key="item.id">
          <div class="activity-icon">{{ item.icon }}</div>
          <div class="activity-content">
            <h4>{{ item.title }}</h4>
            <p>{{ item.description }}</p>
            <span class="activity-time">{{ item.time }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminHome',
  props: {
    username: {
      type: String,
      default: '管理员'
    }
  },
  data() {
    return {
      recentActivities: [
        {
          id: 1,
          icon: '📝',
          title: '项目更新',
          description: '项目"A系统的开发"已完成50%进度',
          time: '2小时前'
        },
        {
          id: 2,
          icon: '👤',
          title: '新用户注册',
          description: '新用户"张三"已加入系统',
          time: '5小时前'
        },
        {
          id: 3,
          icon: '⚙️',
          title: '系统维护',
          description: '系统已完成例行维护',
          time: '1天前'
        },
        {
          id: 4,
          icon: '📋',
          title: '任务分配',
          description: '为"李四"分配了新的开发任务',
          time: '2天前'
        }
      ]
    }
  }
}
</script>

<style scoped>
.admin-home {
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
}

.welcome-section h1 {
  font-size: 2rem;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 16px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #4A90E2;
  margin: 0;
}

.recent-activity h2 {
  margin-bottom: 20px;
  color: #333;
}

.activity-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #eee;
}

.activity-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 1.5rem;
  margin-right: 15px;
  padding-top: 5px;
}

.activity-content h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.activity-content p {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 0.9rem;
}

.activity-time {
  font-size: 0.8rem;
  color: #999;
}
</style>