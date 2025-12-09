<template>
  <div class="history-container">
    <h2>📝 操作历史</h2>
    <div class="history-list">
      <div class="history-item" v-for="item in historyItems" :key="item.id">
        <div class="history-item-header">
          <span class="history-action">{{ item.action }}</span>
          <span class="history-time">{{ item.time }}</span>
        </div>
        <div class="history-item-content">
          {{ item.description }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'History',
  data() {
    return {
      historyItems: [
        {
          id: 1,
          action: '登录',
          time: '2025-10-29 14:30:22',
          description: '用户 admin 成功登录系统'
        },
        {
          id: 2,
          action: '修改资料',
          time: '2025-10-29 14:25:17',
          description: '修改了用户名和邮箱地址'
        },
        {
          id: 3,
          action: '登录',
          time: '2025-10-29 09:15:44',
          description: '用户 admin 成功登录系统'
        },
        {
          id: 4,
          action: '上传文件',
          time: '2025-10-28 16:42:31',
          description: '上传了文件 report.pdf'
        },
        {
          id: 5,
          action: '修改密码',
          time: '2025-10-28 11:20:05',
          description: '成功修改了登录密码'
        }
      ]
    }
  }
}
</script>

<style scoped>
.history-container {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.history-container h2 {
  margin-top: 0;
  color: #333;
  font-size: 24px;
  margin-bottom: 25px;
}

.history-item {
  padding: 15px 20px;
  border-left: 4px solid #667eea;
  background-color: #f8f9fa;
  margin-bottom: 15px;
  border-radius: 0 6px 6px 0;
  transition: all 0.3s ease;
}

.history-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateX(2px);
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.history-action {
  font-weight: 600;
  color: #333;
}

.history-time {
  color: #666;
  font-size: 14px;
}

.history-item-content {
  color: #555;
  line-height: 1.5;
}
</style>