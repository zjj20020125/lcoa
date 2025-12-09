<template>
  <div class="modification-log">
    <h2>📝 修改日志</h2>
    <div class="filters">
      <div class="filter-group">
        <label>表名:</label>
        <select v-model="filter.tableName">
          <option value="">全部</option>
          <option value="sys_project">项目表</option>
          <option value="sys_project_milestone">项目里程碑表</option>
          <option value="lcoa">LCOA表</option>
          <option value="sys_nodeal">流程数据表</option>
        </select>
      </div>
      <div class="filter-group">
        <label>操作类型:</label>
        <select v-model="filter.operationType">
          <option value="">全部</option>
          <option value="INSERT">新增</option>
          <option value="UPDATE">更新</option>
          <option value="DELETE">删除</option>
        </select>
      </div>
      <div class="filter-group">
        <label>用户名:</label>
        <input type="text" v-model="filter.username" placeholder="输入用户名">
      </div>
      <button class="btn btn-primary" @click="fetchLogs">查询</button>
    </div>
    
    <div class="logs-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>表名</th>
            <th>记录ID</th>
            <th>操作类型</th>
            <th>用户</th>
            <th>操作时间</th>
            <th>操作详情</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in filteredLogs" :key="log.id">
            <td>{{ log.id }}</td>
            <td>{{ log.table_name }}</td>
            <td>{{ log.record_id }}</td>
            <td>
              <span :class="['operation-type', log.operation_type.toLowerCase()]">
                {{ getOperationTypeName(log.operation_type) }}
              </span>
            </td>
            <td>{{ log.username || '未知用户' }}</td>
            <td>{{ formatDate(log.operation_time) }}</td>
            <td>
              <button class="btn btn-small" @click="showLogDetail(log)">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 日志详情模态框 -->
    <div class="modal" v-if="showDetailModal">
      <div class="modal-content detail-modal">
        <span class="close" @click="closeDetailModal">&times;</span>
        <h3>修改详情</h3>
        <div class="detail-content" v-if="selectedLog">
          <div class="detail-row">
            <span class="detail-label">表名:</span>
            <span class="detail-value">{{ selectedLog.table_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">记录ID:</span>
            <span class="detail-value">{{ selectedLog.record_id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">操作类型:</span>
            <span class="detail-value">{{ getOperationTypeName(selectedLog.operation_type) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">操作用户:</span>
            <span class="detail-value">{{ selectedLog.username || '未知用户' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">操作时间:</span>
            <span class="detail-value">{{ formatDate(selectedLog.operation_time) }}</span>
          </div>
          
          <div class="data-diff" v-if="selectedLog.operation_type === 'UPDATE'">
            <h4>数据变更详情</h4>
            <div class="diff-content">
              <div v-for="(diff, key) in dataDifferences" :key="key" class="diff-row">
                <span class="diff-key">{{ key }}:</span>
                <span class="diff-old">{{ diff.old }}</span>
                <span class="diff-arrow">→</span>
                <span class="diff-new">{{ diff.new }}</span>
              </div>
            </div>
          </div>
          
          <div class="data-content" v-if="selectedLog.operation_type === 'INSERT'">
            <h4>新增数据</h4>
            <div class="json-content">
              <pre>{{ formatJson(selectedLog.new_data) }}</pre>
            </div>
          </div>
          
          <div class="data-content" v-if="selectedLog.operation_type === 'DELETE'">
            <h4>删除数据</h4>
            <div class="json-content">
              <pre>{{ formatJson(selectedLog.old_data) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ModificationLog',
  data() {
    return {
      logs: [],
      filter: {
        tableName: '',
        operationType: '',
        username: ''
      },
      showDetailModal: false,
      selectedLog: null
    }
  },
  computed: {
    filteredLogs() {
      return this.logs.filter(log => {
        return (
          (this.filter.tableName === '' || log.table_name === this.filter.tableName) &&
          (this.filter.operationType === '' || log.operation_type === this.filter.operationType) &&
          (this.filter.username === '' || (log.username && log.username.includes(this.filter.username)))
        )
      })
    },
    dataDifferences() {
      if (!this.selectedLog || this.selectedLog.operation_type !== 'UPDATE') {
        return {}
      }
      
      try {
        const oldData = JSON.parse(this.selectedLog.old_data)
        const newData = JSON.parse(this.selectedLog.new_data)
        const differences = {}
        
        for (const key in newData) {
          if (oldData[key] !== newData[key]) {
            differences[key] = {
              old: oldData[key],
              new: newData[key]
            }
          }
        }
        
        return differences
      } catch (e) {
        console.error('解析数据差异时出错:', e)
        return {}
      }
    }
  },
  mounted() {
    this.fetchLogs()
  },
  methods: {
    async fetchLogs() {
      try {
        const response = await axios.get('/api/modification_logs')
        if (response.data.code === 200) {
          this.logs = response.data.data
        }
      } catch (error) {
        console.error('获取修改日志失败:', error)
      }
    },
    getOperationTypeName(type) {
      const types = {
        'INSERT': '新增',
        'UPDATE': '更新',
        'DELETE': '删除'
      }
      return types[type] || type
    },
    formatDate(dateString) {
      if (!dateString) return '未知时间'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    showLogDetail(log) {
      this.selectedLog = log
      this.showDetailModal = true
    },
    closeDetailModal() {
      this.showDetailModal = false
      this.selectedLog = null
    },
    formatJson(jsonString) {
      try {
        const obj = JSON.parse(jsonString)
        return JSON.stringify(obj, null, 2)
      } catch (e) {
        return jsonString
      }
    }
  }
}
</script>

<style scoped>
.modification-log {
  padding: 20px;
}

.modification-log h2 {
  color: #333;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-weight: bold;
  margin-bottom: 5px;
}

.filter-group select,
.filter-group input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.logs-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
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

.operation-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.operation-type.insert {
  background-color: #d4edda;
  color: #155724;
}

.operation-type.update {
  background-color: #fff3cd;
  color: #856404;
}

.operation-type.delete {
  background-color: #f8d7da;
  color: #721c24;
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

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
}

/* 模态框样式 */
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
  max-width: 800px;
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

.detail-content {
  margin-top: 20px;
}

.detail-row {
  display: flex;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-label {
  font-weight: bold;
  width: 120px;
  flex-shrink: 0;
}

.detail-value {
  flex: 1;
}

.data-diff h4,
.data-content h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #333;
}

.diff-content {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
}

.diff-row {
  display: flex;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.diff-key {
  font-weight: bold;
  width: 150px;
  flex-shrink: 0;
}

.diff-old {
  text-decoration: line-through;
  color: #dc3545;
  width: 200px;
  flex-shrink: 0;
}

.diff-arrow {
  padding: 0 10px;
  color: #6c757d;
}

.diff-new {
  color: #28a745;
  font-weight: bold;
}

.json-content {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.json-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
}
</style>