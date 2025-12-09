<template>
  <div class="user-home">
    <div class="welcome-section">
      <h1>用户中心首页</h1>
      <p>欢迎{{ username }}来到结构件数据管理平台</p>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <h3>我的项目</h3>
        <p class="stat-number">5</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <h3>待办任务</h3>
        <p class="stat-number">3</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <h3>近期截止</h3>
        <p class="stat-number">2</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <h3>已完成</h3>
        <p class="stat-number">12</p>
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
  name: 'UserHome',
  props: {
    username: {
      type: String,
      default: '用户'
    }
  },
  data() {
    return {
      recentActivities: [
        {
          id: 1,
          icon: '📝',
          title: '任务更新',
          description: '您有一个新任务"完成项目文档"',
          time: '1小时前'
        },
        {
          id: 2,
          icon: '📅',
          title: '截止提醒',
          description: '项目"B系统升级"将在明天截止',
          time: '3小时前'
        },
        {
          id: 3,
          icon: '✅',
          title: '任务完成',
          description: '您已完成"数据分析报告"任务',
          time: '1天前'
        },
        {
          id: 4,
          icon: '📁',
          title: '项目更新',
          description: '项目"A系统开发"进度已更新至75%',
          time: '2天前'
        }
      ]
    }
  }
}
</script>

<style scoped>
.user-home {
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