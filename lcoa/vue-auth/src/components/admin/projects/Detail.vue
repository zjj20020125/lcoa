<template>
  <div class="project-detail">
    <div class="header">
      <button class="btn btn-secondary" @click="goBack">← 返回项目列表</button>
      <h2>项目详情 - {{ project.project_name }}</h2>
    </div>
    
    <div class="project-info">
      <div class="info-card">
        <h3>基本信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>项目名称:</label>
            <span>{{ project.project_name }}</span>
          </div>
          <div class="info-item">
            <label>产品名称:</label>
            <span>{{ project.product_name }}</span>
          </div>
          <div class="info-item">
            <label>客户名称:</label>
            <span>{{ project.customer_name }}</span>
          </div>
          <div class="info-item">
            <label>订单状态:</label>
            <span :class="getStatusClass(project.order_status)">{{ project.order_status || '无数据' }}</span>
          </div>
          <div class="info-item">
            <label>创建时间:</label>
            <span>{{ project.created_at || '未知' }}</span>
          </div>
          <div class="info-item">
            <label>更新时间:</label>
            <span>{{ project.updated_at || '未知' }}</span>
          </div>
        </div>
      </div>
      
      <div class="info-card">
        <h3>产品示意图</h3>
        <div class="image-container">
          <img
            v-if="project.product_image && isValidImageUrl(project.product_image)"
            :src="getImageUrl(project.product_image)"
            :alt="'产品示意图-' + project.project_name"
            class="product-image"
            @load="onImageLoad"
            @error="onImageError"
            :class="{ 'image-loading': imageLoading, 'image-error': imageError }"
          />
          <div v-else-if="project.product_image && isBase64Image(project.product_image)" class="image-placeholder">
            Base64图像
          </div>
          <div v-else-if="imageError" class="image-error-placeholder">
            图片加载失败
          </div>
          <div v-else class="no-image-placeholder">
            无图片
          </div>
          <div v-if="imageLoading" class="image-loading-indicator">
            加载中...
          </div>
        </div>
      </div>
    </div>
    
    <div class="milestones-section">
      <div class="section-header">
        <h3>关键里程碑节点</h3>
        <button class="btn btn-primary" @click="showAddMilestoneForm">新增里程碑</button>
      </div>
      
      <div v-if="project.milestones && project.milestones.length > 0" class="milestones-table">
        <table>
          <thead>
            <tr>
              <th>里程碑节点</th>
              <th>负责部门</th>
              <th>计划开始时间</th>
              <th>计划结束时间</th>
              <th>节点进度</th>
              <th>实际完成时间</th>
              <th>负责人</th>
              <th class="exception-column">异常类别</th>
              <th>影响周期(天)</th>
              <th>应对措施</th>
              <th>修改日志</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(milestone, index) in project.milestones" :key="milestone.id">
              <td>{{ milestone.milestone }}</td>
              <td>{{ milestone.responsible_department || '未指定' }}</td>
              <td>{{ milestone.planned_start_time || '未指定' }}</td>
              <td>{{ milestone.planned_end_time || '未指定' }}</td>
              <td>
                <div class="progress-container">
                  <div 
                    class="progress-bar" 
                    :class="getProgressColorClass(milestone)"
                    :style="{ width: getProgressPercentage(milestone) + '%' }"
                  >
                    {{ isSameDayTask(milestone) ? '当天完成' : Math.round(getProgressPercentage(milestone)) + '%' }}
                  </div>
                </div>
              </td>
              <td>{{ milestone.actual_completion_time || '未完成' }}</td>
              <td>{{ milestone.responsible_person || '未指定' }}</td>
              <td>{{ milestone.exception_type || '无' }}</td>
              <td>{{ milestone.impact_cycle || '无' }}</td>
              <td>{{ milestone.response_measures || '无' }}</td>
              <td>{{ milestone.modification_log || '无' }}</td>
              <td>
                <button class="action-btn" @click="editMilestone(milestone)">编辑</button>
                <button class="action-btn delete-btn" @click="confirmDeleteMilestone(milestone)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="no-milestones">
        <p>暂无里程碑信息</p>
      </div>
    </div>
    
    <!-- 新增里程碑模态框 -->
    <div class="modal" v-if="showAddMilestoneModal">
      <div class="modal-content">
        <span class="close" @click="closeAddMilestoneModal">&times;</span>
        <h3>新增里程碑</h3>
        <form @submit.prevent="addMilestone">
          <div class="form-group">
            <label>关键节点:</label>
            <input v-model="newMilestone.milestone" type="text" required />
          </div>
          <div class="form-group">
            <label>负责部门:</label>
            <input v-model="newMilestone.responsible_department" type="text" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>计划开始时间:</label>
              <input v-model="newMilestone.planned_start_time" type="date" />
            </div>
            <div class="form-group">
              <label>计划结束时间:</label>
              <input v-model="newMilestone.planned_end_time" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>实际完成时间:</label>
            <input v-model="newMilestone.actual_completion_time" type="date" />
          </div>
          <div class="form-group">
            <label>负责人:</label>
            <input v-model="newMilestone.responsible_person" type="text" />
          </div>
          <div class="form-group">
            <label>异常类别:</label>
            <input v-model="newMilestone.exception_type" type="text" />
          </div>
          <div class="form-group">
            <label>影响周期(天):</label>
            <input v-model="newMilestone.impact_cycle" type="number" />
          </div>
          <div class="form-group">
            <label>应对措施:</label>
            <textarea v-model="newMilestone.response_measures" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeAddMilestoneModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">添加</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 编辑里程碑模态框 -->
    <div class="modal" v-if="showEditMilestoneModal">
      <div class="modal-content">
        <span class="close" @click="closeEditMilestoneModal">&times;</span>
        <h3>编辑里程碑</h3>
        <form @submit.prevent="updateMilestone">
          <div class="form-group">
            <label>关键节点:</label>
            <input v-model="editingMilestone.milestone" type="text" required />
          </div>
          <div class="form-group">
            <label>负责部门:</label>
            <input v-model="editingMilestone.responsible_department" type="text" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>计划开始时间:</label>
              <input v-model="editingMilestone.planned_start_time" type="date" />
            </div>
            <div class="form-group">
              <label>计划结束时间:</label>
              <input v-model="editingMilestone.planned_end_time" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>实际完成时间:</label>
            <input v-model="editingMilestone.actual_completion_time" type="date" />
          </div>
          <div class="form-group">
            <label>负责人:</label>
            <input v-model="editingMilestone.responsible_person" type="text" />
          </div>
          <div class="form-group">
            <label>异常类别:</label>
            <input v-model="editingMilestone.exception_type" type="text" />
          </div>
          <div class="form-group">
            <label>影响周期(天):</label>
            <input v-model="editingMilestone.impact_cycle" type="number" />
          </div>
          <div class="form-group">
            <label>应对措施:</label>
            <textarea v-model="editingMilestone.response_measures" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>修改日志:</label>
            <textarea v-model="editingMilestone.modification_log" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeEditMilestoneModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ProjectDetail',
  data() {
    return {
      project: {},
      imageLoading: false,
      imageError: false,
      showAddMilestoneModal: false,
      showEditMilestoneModal: false,
      newMilestone: {
        milestone: '',
        responsible_department: '',
        planned_start_time: '',
        planned_end_time: '',
        actual_completion_time: '',
        responsible_person: '',
        exception_type: '',
        impact_cycle: '',
        response_measures: ''
      },
      editingMilestone: {}
    }
  },
  mounted() {
    this.fetchProjectDetail()
  },
  methods: {
    async fetchProjectDetail() {
      try {
        const projectId = this.$route.params.id
        const response = await axios.get(`/api/sys_project/${projectId}`)
        if (response.data.code === 200) {
          this.project = response.data.data
        } else {
          console.error('获取项目详情失败:', response.data.message)
          alert('获取项目详情失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('获取项目详情失败:', error)
        alert('获取项目详情时发生错误')
      }
    },
    
    goBack() {
      // 跳转到新制项目管理下的项目列表界面
      this.$router.push('/admin?menu=projects-list');
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
      if (!imagePath) return '';
      
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      
      if (imagePath.startsWith('/')) {
        return 'http://localhost:5000' + imagePath;
      }
      
      return imagePath;
    },
    
    isValidImageUrl(url) {
      if (!url) return false;
      return !url.startsWith('data:image');
    },
    
    isBase64Image(data) {
      if (!data) return false;
      return data.startsWith('data:image');
    },
    
    onImageLoad() {
      this.imageLoading = false;
      this.imageError = false;
    },
    
    onImageError() {
      this.imageLoading = false;
      this.imageError = true;
    },
    
    showAddMilestoneForm() {
      this.showAddMilestoneModal = true
      this.newMilestone = {
        milestone: '',
        responsible_department: '',
        planned_start_time: '',
        planned_end_time: '',
        actual_completion_time: '',
        responsible_person: '',
        exception_type: '',
        impact_cycle: '',
        response_measures: ''
      }
    },
    
    closeAddMilestoneModal() {
      this.showAddMilestoneModal = false
    },
    
    closeEditMilestoneModal() {
      this.showEditMilestoneModal = false
    },
    
    async addMilestone() {
      try {
        const projectId = this.$route.params.id
        const response = await axios.post(`/api/sys_project/${projectId}/milestones`, this.newMilestone)
        
        if (response.data.code === 200) {
          this.closeAddMilestoneModal()
          this.fetchProjectDetail() // 重新加载数据
          alert('里程碑添加成功!')
        } else {
          alert('添加失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('添加里程碑失败:', error)
        alert('添加里程碑时发生错误')
      }
    },
    
    editMilestone(milestone) {
      // 深拷贝里程碑数据，避免直接修改原始数据
      this.editingMilestone = JSON.parse(JSON.stringify(milestone));
      this.showEditMilestoneModal = true
    },
    
    // 判断是否为同一天任务
    isSameDayTask(milestone) {
      // 检查必要字段是否存在
      if (!milestone.planned_start_time || !milestone.planned_end_time) {
        return false;
      }

      const startDate = new Date(milestone.planned_start_time);
      const endDate = new Date(milestone.planned_end_time);
      
      // 将日期设置为同一天，只比较日期部分
      const startDay = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      const endDay = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      
      // 如果开始日期和结束日期是同一天，则返回true
      return startDay.getTime() === endDay.getTime();
    },
    
    async updateMilestone() {
      try {
        // 获取原始里程碑数据
        const originalMilestone = this.project.milestones.find(m => m.id === this.editingMilestone.id);
        
        // 处理影响周期对计划结束时间的影响
        if (originalMilestone && this.editingMilestone.impact_cycle !== originalMilestone.impact_cycle) {
          // 获取原始计划结束时间
          const originalPlannedEnd = new Date(originalMilestone.planned_end_time);
          
          if (originalMilestone.impact_cycle) {
            // 如果原来有影响周期，计算差值
            const originalImpact = parseInt(originalMilestone.impact_cycle) || 0;
            const newImpact = parseInt(this.editingMilestone.impact_cycle) || 0;
            const diffDays = newImpact - originalImpact;
            
            // 更新计划结束时间
            originalPlannedEnd.setDate(originalPlannedEnd.getDate() + diffDays);
          } else {
            // 如果原来没有影响周期，直接加上新的影响天数
            const newImpact = parseInt(this.editingMilestone.impact_cycle) || 0;
            originalPlannedEnd.setDate(originalPlannedEnd.getDate() + newImpact);
          }
          
          // 更新编辑数据中的计划结束时间
          this.editingMilestone.planned_end_time = originalPlannedEnd.toISOString().split('T')[0];
        }
        
        // 构造修改日志
        const modificationLog = this.generateModificationLog(this.editingMilestone);
        
        // 将修改日志添加到编辑数据中
        const milestoneData = {
          ...this.editingMilestone,
          modification_log: modificationLog,
          modified_by: localStorage.getItem('username') || 'Unknown'
        };
        
        // 确保日期字段格式正确
        if (milestoneData.planned_start_time) {
          milestoneData.planned_start_time = milestoneData.planned_start_time.split('T')[0];
        }
        if (milestoneData.planned_end_time) {
          milestoneData.planned_end_time = milestoneData.planned_end_time.split('T')[0];
        }
        if (milestoneData.actual_completion_time) {
          milestoneData.actual_completion_time = milestoneData.actual_completion_time.split('T')[0];
        }
        
        const response = await axios.put(
          `/api/sys_project_milestone/${this.editingMilestone.id}`,
          milestoneData
        )
        
        if (response.data.code === 200) {
          this.closeEditMilestoneModal()
          this.fetchProjectDetail() // 重新加载数据
          alert('里程碑更新成功!')
        } else {
          alert('更新失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('更新里程碑失败:', error)
        alert('更新里程碑时发生错误: ' + (error.response?.data?.message || error.message))
      }
    },
    
    // 生成修改日志
    generateModificationLog(editedMilestone) {
      // 获取原始里程碑数据
      const originalMilestone = this.project.milestones.find(m => m.id === editedMilestone.id);
      if (!originalMilestone) return '';
      
      const changes = [];
      const fieldMapping = {
        'milestone': '里程碑节点',
        'responsible_department': '负责部门',
        'planned_start_time': '计划开始时间',
        'planned_end_time': '计划结束时间',
        'actual_completion_time': '实际完成时间',
        'responsible_person': '负责人',
        'exception_type': '异常类别',
        'impact_cycle': '影响周期',
        'response_measures': '应对措施'
      };
      
      // 对比各个字段
      Object.keys(fieldMapping).forEach(key => {
        const oldValue = originalMilestone[key] || '';
        const newValue = editedMilestone[key] || '';
        
        // 只有当值真正改变时才记录
        if (oldValue !== newValue) {
          changes.push(`${fieldMapping[key]}: 从"${oldValue}"修改为"${newValue}"`);
        }
      });
      
      // 如果没有任何变化，则不记录日志
      if (changes.length === 0) return originalMilestone.modification_log || '';
      
      const currentTime = new Date().toLocaleString('zh-CN');
      const username = localStorage.getItem('username') || '用户';
      const newLogEntry = `${username} 于 ${currentTime} 修改了 ${changes.join(', ')}`;
      
      // 如果原有日志存在，则新增日志而不是替换
      if (originalMilestone.modification_log) {
        return `${originalMilestone.modification_log}\n${newLogEntry}`;
      } else {
        return newLogEntry;
      }
    },
    
    confirmDeleteMilestone(milestone) {
      if (confirm(`确定要删除里程碑 "${milestone.milestone}" 吗？此操作不可恢复。`)) {
        this.deleteMilestone(milestone.id)
      }
    },
    
    async deleteMilestone(milestoneId) {
      try {
        const response = await axios.delete(`/api/sys_project_milestone/${milestoneId}`)
        
        if (response.data.code === 200) {
          this.fetchProjectDetail() // 重新加载数据
          alert('里程碑删除成功!')
        } else {
          alert('删除失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('删除里程碑失败:', error)
        alert('删除里程碑时发生错误')
      }
    },

    // 计算里程碑进度百分比
    getProgressPercentage(milestone) {
      // 检查必要字段是否存在
      if (!milestone.planned_start_time || !milestone.planned_end_time) {
        return 0;
      }

      const startDate = new Date(milestone.planned_start_time);
      const endDate = new Date(milestone.planned_end_time);
      const currentDate = new Date();
      
      // 将日期设置为同一天，只比较日期部分
      const startDay = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      const endDay = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      const currentDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());

      // 如果开始时间晚于结束时间，则返回0
      if (startDate > endDate) {
        return 0;
      }
      
      // 如果开始日期和结束日期是同一天，则特殊处理
      if (startDay.getTime() === endDay.getTime()) {
        // 如果是当天完成的任务，返回100
        return 100;
      }

      // 如果当前时间早于开始时间，则返回0
      if (currentDay < startDay) {
        return 0;
      }

      // 如果当前时间晚于结束时间，则返回100
      if (currentDay > endDay) {
        return 100;
      }

      // 计算总时间间隔和已过时间间隔（毫秒）
      const totalTime = endDay - startDay;
      const elapsedTime = currentDay - startDay;

      // 计算并返回百分比
      return (elapsedTime / totalTime) * 100;
    },

    // 根据进度百分比获取颜色类
    getProgressColorClass(milestone) {
      // 检查必要字段是否存在
      if (!milestone.planned_start_time || !milestone.planned_end_time) {
        return 'progress-green';
      }

      const startDate = new Date(milestone.planned_start_time);
      const endDate = new Date(milestone.planned_end_time);
      
      // 将日期设置为同一天，只比较日期部分
      const startDay = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      const endDay = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      
      // 如果开始日期和结束日期是同一天，则显示黄色
      if (startDay.getTime() === endDay.getTime()) {
        return 'progress-yellow';
      }
      
      const percentage = this.getProgressPercentage(milestone);
      
      if (percentage < 30) {
        return 'progress-green';
      } else if (percentage < 80) {
        return 'progress-yellow';
      } else {
        return 'progress-red';
      }
    }
  }
}
</script>

<style scoped>
.project-detail {
  padding: 20px;
  background-color: #f5f7fa;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0 0 0 15px;
  color: #333;
}

.project-info {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.info-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #666;
}

.info-item span {
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.image-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.product-image {
  max-width: 100%;
  max-height: 300px;
}

.image-placeholder,
.no-image-placeholder,
.image-error-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  background-color: #f5f5f5;
  border: 1px dashed #ccc;
  border-radius: 4px;
  font-size: 14px;
  color: #999;
}

.image-loading-indicator {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  color: #333;
}

.milestones-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
}

.milestones-table table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed; /* 固定表格布局，允许控制列宽 */
}

.milestones-table th,
.milestones-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.exception-column {
  width: 80px; /* 设置异常类别列的固定宽度，约等于四个汉字的宽度 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.milestones-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.no-milestones {
  background: white;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.no-milestones p {
  margin: 0;
  color: #999;
  font-size: 16px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #4A90E2;
  color: white;
}

.btn-primary:hover {
  background-color: #357AE8;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.delete-btn {
  background-color: #e74c3c;
  margin-left: 5px;
}

.delete-btn:hover {
  background-color: #c0392b;
}

.action-btn {
  background-color: #4A90E2;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 5px;
}

.action-btn:hover {
  background-color: #357AE8;
}

.modal {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  overflow-y: auto;
}

.modal-content {
  background-color: #fefefe;
  margin: 5% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
  max-width: 600px;
  border-radius: 8px;
  position: relative;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
  position: absolute;
  right: 20px;
  top: 10px;
  cursor: pointer;
}

.close:hover,
.close:focus {
  color: black;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.status-orange {
  color: orange;
  font-weight: bold;
}

.status-yellow {
  color: #ffc107;
  font-weight: bold;
}

.status-green {
  color: green;
  font-weight: bold;
}

.status-red {
  color: red;
  font-weight: bold;
}

/* 进度条样式 */
.progress-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 4px;
  height: 20px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  transition: width 0.3s ease;
}

.progress-green {
  background-color: #4CAF50;
}

.progress-yellow {
  background-color: #FFEB3B;
  color: #333;
}

.progress-red {
  background-color: #F44336;
}

@media (max-width: 768px) {
  .project-info {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>