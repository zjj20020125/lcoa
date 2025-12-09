<template>
  <div class="project-overview">
    <h2>📋 项目概览</h2>
    <div class="overview-content">
      <div class="stats-grid">
        <div class="stat-card">
          <h3>项目总数</h3>
          <p class="stat-number">{{ totalProjects }}</p>
        </div>
        <div class="stat-card">
          <h3>进行中项目</h3>
          <p class="stat-number">{{ inProgressProjects }}</p>
        </div>
        <div class="stat-card">
          <h3>已完成项目</h3>
          <p class="stat-number">{{ completedProjects }}</p>
        </div>
        <div class="stat-card">
          <h3>待开始项目</h3>
          <p class="stat-number">{{ notStartedProjects }}</p>
        </div>
      </div>
    </div>

    <!-- 添加项目成员内容 -->
    <div class="project-members-section">
      <h2 style="margin-top: 30px;">👥 项目成员</h2>
      <div class="members-content">
        <div class="table-container">
          <table class="members-table">
            <thead>
              <tr>
                <th>项目名称</th>
                <th>成员姓名</th>
                <th>所属部门</th>
                <th>角色</th>
                <th>来源</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="project in projects" :key="project.id">
                <!-- 项目负责人行 -->
                <tr>
                  <td :rowspan="getProjectMemberCount(project)" class="project-name">
                    {{ project.project_name }}
                  </td>
                  <td>{{ getProjectLeader(project) }}</td>
                  <td>{{ getProjectLeaderDepartment(project) }}</td>
                  <td>项目经理</td>
                  <td>项目主表</td>
                </tr>
                
                <!-- 里程碑负责人行 -->
                <tr v-for="milestone in project.milestones" :key="milestone.id">
                  <td>{{ milestone.responsible_person }}</td>
                  <td>{{ milestone.responsible_department }}</td>
                  <td>里程碑负责人</td>
                  <td>{{ milestone.milestone }}</td>
                </tr>
              </template>
              
              <!-- 如果没有项目数据 -->
              <tr v-if="!projects || projects.length === 0">
                <td colspan="5" class="no-data">暂无项目成员数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ProjectOverview',
  data() {
    return {
      totalProjects: 0,
      inProgressProjects: 0,
      completedProjects: 0,
      notStartedProjects: 0,
      projects: [],
      // 图片加载状态管理
      imageLoading: {},
      imageErrors: {},
      isUpdatingStatus: false, // 添加标志防止重复更新
      // 定时任务相关
      statusUpdateTimer: null
    }
  },
  async mounted() {
    await this.fetchProjectStats()
    await this.fetchProjects()
    // 设置定时任务，每天零点更新项目状态
    this.scheduleDailyStatusUpdate()
  },
  beforeDestroy() {
    // 组件销毁前清除定时器
    if (this.statusUpdateTimer) {
      clearInterval(this.statusUpdateTimer)
    }
  },
  methods: {
    async fetchProjectStats() {
      try {
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          // 只计算状态，不主动更新数据库
          const projects = response.data.data.map(project => ({
            ...project,
            order_status: this.calculateProjectStatus(project)
          }));
          
          // 总项目数
          this.totalProjects = projects.length
          
          // 根据项目状态分类统计
          this.inProgressProjects = projects.filter(
            project => project.order_status === '实施中'
          ).length
          
          this.completedProjects = projects.filter(
            project => project.order_status === '已完成'
          ).length
          
          this.notStartedProjects = projects.filter(
            project => project.order_status === '已签约'
          ).length
        }
      } catch (error) {
        console.error('获取项目统计数据失败:', error)
      }
    },
    async fetchProjects() {
      try {
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          // 只计算状态，不主动更新数据库
          const projectsWithStatus = response.data.data.map(project => ({
            ...project,
            order_status: this.calculateProjectStatus(project)
          }));
          
          this.projects = projectsWithStatus;
          // 初始化图片加载状态
          this.initializeImageStates(projectsWithStatus)
        }
      } catch (error) {
        console.error('获取项目数据失败:', error)
      }
    },
    
    // 设置每天零点的定时任务
    scheduleDailyStatusUpdate() {
      // 先清除已存在的定时器
      if (this.statusUpdateTimer) {
        clearInterval(this.statusUpdateTimer)
      }
      
      // 计算到下一个零点的时间间隔
      const now = new Date()
      const nextMidnight = new Date()
      nextMidnight.setDate(now.getDate() + 1)
      nextMidnight.setHours(0, 0, 0, 0)
      
      const timeUntilMidnight = nextMidnight.getTime() - now.getTime()
      
      // 设置定时器到下一个零点
      setTimeout(() => {
        this.updateAllProjectStatuses()
        // 之后每24小时执行一次
        this.statusUpdateTimer = setInterval(() => {
          this.updateAllProjectStatuses()
        }, 24 * 60 * 60 * 1000) // 24小时
      }, timeUntilMidnight)
      
      console.log(`定时任务已设置，将在 ${nextMidnight.toString()} 开始执行`)
    },
    
    // 更新所有项目的状态
    async updateAllProjectStatuses() {
      console.log('开始执行每日项目状态更新任务...')
      
      try {
        // 获取最新的项目数据
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          const projects = response.data.data
          let updatedCount = 0
          
          // 遍历所有项目，检查并更新状态
          for (const project of projects) {
            const calculatedStatus = this.calculateProjectStatus(project)
            
            // 如果计算出的状态与数据库中的状态不同，则更新数据库
            if (calculatedStatus !== project.order_status) {
              console.log(`项目 ${project.id} 状态将从 "${project.order_status}" 更新为 "${calculatedStatus}"`)
              const success = await this.updateProjectStatusInDatabase(project.id, calculatedStatus)
              if (success) {
                updatedCount++
              }
            }
          }
          
          console.log(`每日项目状态更新任务完成，共更新 ${updatedCount} 个项目`)
          
          // 更新完成后重新获取项目统计数据和列表
          await this.fetchProjectStats()
          await this.fetchProjects()
        }
      } catch (error) {
        console.error('执行每日项目状态更新任务时出错:', error)
      }
    },
    
    calculateProjectStatus(project) {
      // 获取今天的日期
      const today = new Date();
      today.setHours(0, 0, 0, 0); // 忽略时间部分，只比较日期
      
      // 如果没有里程碑，返回默认状态
      if (!project.milestones || project.milestones.length === 0) {
        return project.order_status || '已签约';
      }
      
      // 提取所有里程碑的计划开始时间和计划结束时间
      const milestoneDates = project.milestones
        .map(milestone => ({
          start: milestone.planned_start_time ? new Date(milestone.planned_start_time) : null,
          end: milestone.planned_end_time ? new Date(milestone.planned_end_time) : null
        }))
        .filter(date => date.start || date.end); // 过滤掉完全空的日期
      
      // 如果没有有效日期，返回默认状态
      if (milestoneDates.length === 0) {
        return project.order_status || '已签约';
      }
      
      // 检查是否所有里程碑都在未来（已签约）
      const allInFuture = milestoneDates.every(date => {
        const startDateValid = !date.start || date.start > today;
        const endDateValid = !date.end || date.end > today;
        return startDateValid && endDateValid;
      });
      
      if (allInFuture) {
        return '已签约';
      }
      
      // 检查是否至少有一个里程碑已经完成（已完成）
      const anyCompleted = milestoneDates.some(date => {
        const endDateValid = date.end && date.end < today;
        return endDateValid;
      });
      
      if (anyCompleted) {
        return '已完成';
      }
      
      // 检查是否在任何里程碑的执行期间（实施中）
      const anyInProgress = milestoneDates.some(date => {
        // 如果有开始和结束时间，检查今天是否在这两个时间之间
        if (date.start && date.end) {
          return date.start <= today && today <= date.end;
        }
        // 如果只有开始时间，检查今天是否在开始之后
        if (date.start) {
          return date.start <= today;
        }
        // 如果只有结束时间，检查今天是否在结束之前
        if (date.end) {
          return today <= date.end;
        }
        return false;
      });
      
      if (anyInProgress) {
        return '实施中';
      }
      
      // 默认返回原状态
      return project.order_status || '已签约';
    },
    
    async updateProjectStatusInDatabase(projectId, newStatus) {
      try {
        console.log(`准备更新项目 ${projectId} 的状态: ${newStatus}`);
        // 发送请求更新项目状态到数据库
        const response = await axios.put(`/api/sys_project/${projectId}`, {
          order_status: newStatus
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (response.data.code === 200) {
          console.log(`项目 ${projectId} 状态更新成功: ${newStatus}`);
          return true;
        } else {
          console.error(`项目 ${projectId} 状态更新失败:`, response.data.message);
          return false;
        }
      } catch (error) {
        console.error(`更新项目 ${projectId} 状态时出错:`, error);
        return false;
      }
    },
    
    initializeImageStates(projects) {
      // 初始化每个项目的图片加载状态
      projects.forEach(project => {
        this.imageLoading[project.id] = false;
        this.imageErrors[project.id] = false;
      })
    },
    
    getStatusClass(status) {
      switch (status) {
        case '已签约':
          return 'status-orange';
        case '实施中':
          return 'status-yellow';
        case '已完成':
          return 'status-green';
        case '已取消':
          return 'status-red';
        default:
          return '';
      }
    },
    
    getImageUrl(imagePath) {
      // 统一图片URL处理逻辑
      if (!imagePath) return '';
      
      // 如果是完整的URL，直接返回
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      
      // 如果是相对路径，添加基础URL
      if (imagePath.startsWith('/')) {
        return 'http://localhost:5000' + imagePath;
      }
      
      // 其他情况原样返回
      return imagePath;
    },
    
    isValidImageUrl(url) {
      // 检查是否为有效的图片URL（非Base64数据）
      if (!url) return false;
      return !url.startsWith('data:image');
    },
    
    isBase64Image(data) {
      // 检查是否为Base64编码的图片
      if (!data) return false;
      return data.startsWith('data:image');
    },
    
    onImageLoad(projectId) {
      // 图片加载成功回调
      this.imageLoading[projectId] = false;
      this.imageErrors[projectId] = false;
    },
    
    onImageError(projectId) {
      // 图片加载失败回调
      this.imageLoading[projectId] = false;
      this.imageErrors[projectId] = true;
    },
    getProjectLeader(project) {
      // 根据数据结构，我们可以从里程碑中获取项目负责人信息
      // 这里简单地返回第一个里程碑的负责人作为项目负责人
      if (project.milestones && project.milestones.length > 0) {
        return project.milestones[0].responsible_person || '未指定'
      }
      return '未指定'
    },
    
    getProjectLeaderDepartment(project) {
      // 返回项目负责人的部门
      if (project.milestones && project.milestones.length > 0) {
        return project.milestones[0].responsible_department || '未指定'
      }
      return '未指定'
    },
    
    getProjectMemberCount(project) {
      // 计算项目成员总数（项目负责人 + 里程碑负责人）
      let count = 1 // 至少有一个项目负责人
      if (project.milestones && project.milestones.length > 0) {
        count += project.milestones.length
      }
      return count
    }
  }
}
</script>

<style scoped>
.project-overview {
  padding: 20px;
  background-color: #f5f7fa;
}

.project-overview h2 {
  color: #333;
  margin-bottom: 20px;
}

.overview-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  border: 1px solid #eee;
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

/* 项目列表样式 */
.legend {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.legend h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  margin-right: 20px;
  margin-bottom: 10px;
}

.legend-item span {
  margin-left: 5px;
  font-size: 14px;
}

.list-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.project-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.product-image {
  max-width: 80px;
  max-height: 60px;
}

.order-status {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

/* 新增的选择状态样式 */
.status-indicator {
  display: inline-block;
  padding: 4px;
}

.status-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-orange .status-dot {
  background-color: orange;
}

.status-yellow .status-dot {
  background-color: yellow;
}

.status-red .status-dot {
  background-color: red;
}

.status-green .status-dot {
  background-color: green;
}

/* 图片容器和加载状态样式 */
.image-container {
  position: relative;
  display: inline-block;
}

.image-loading {
  opacity: 0.5;
}

.image-error {
  opacity: 0.3;
}

.image-placeholder,
.no-image-placeholder,
.image-error-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 60px;
  background-color: #f5f5f5;
  border: 1px dashed #ccc;
  border-radius: 4px;
  font-size: 12px;
  color: #999;
}

.image-loading-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.image-error-placeholder {
  color: #e74c3c;
}

/* 项目成员样式 */
.project-members-section {
  margin-top: 30px;
}

.members-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.table-container {
  overflow-x: auto;
}

.members-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.members-table th,
.members-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.members-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.members-table tbody tr:hover {
  background-color: #f5f7fa;
}

.project-name {
  font-weight: bold;
  color: #333;
}

.no-data {
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 40px 20px;
}
</style>