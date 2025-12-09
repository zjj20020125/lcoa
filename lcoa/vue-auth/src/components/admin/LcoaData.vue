<template>
  <div class="lcoa-data-container">
    <h2 class="title">📊 LCOA数据展示</h2>
    
    <!-- 操作栏 -->
    <div class="data-actions">
      <div class="action-buttons">
        <button class="refresh-btn" @click="refreshData" :disabled="loading">
          {{ loading ? '加载中...' : '刷新数据' }}
        </button>
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索数据..." 
            class="search-input"
            @keyup.enter="performSearch"
          >
          <button class="search-btn" @click="performSearch">
            🔍 搜索
          </button>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      错误: {{ error }}
    </div>
    
    <!-- 数据加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载数据...</p>
    </div>
    
    <!-- 数据表格 -->
    <div class="data-table-container" v-else-if="!error && filteredData && filteredData.length > 0">
      <div class="table-wrapper" ref="tableWrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="id-column">ID<div class="resizer" @mousedown="initResize($event, 'id')"></div></th>
              <th 
                v-for="(header, index) in visibleHeadersWithoutInterTime" 
                :key="index"
                @click="sortTable(tableFieldsWithoutInterTime[index])"
                class="sortable-header title-column"
              >
                {{ header }}
                <span 
                  v-if="sortField === tableFieldsWithoutInterTime[index]" 
                  class="sort-indicator"
                >
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
                <div class="resizer" @mousedown="initResize($event, 'title')"></div>
              </th>
              <th 
                @click="sortTable('start_time')"
                class="sortable-header time-column"
              >
                开始时间
                <span 
                  v-if="sortField === 'start_time'" 
                  class="sort-indicator"
                >
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
                <div class="resizer" @mousedown="initResize($event, 'start_time')"></div>
              </th>
              <th 
                @click="sortTable('final_time')"
                class="sortable-header time-column"
              >
                结束时间
                <span 
                  v-if="sortField === 'final_time'" 
                  class="sort-indicator"
                >
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
                <div class="resizer" @mousedown="initResize($event, 'final_time')"></div>
              </th>
              <th class="action-column">操作<div class="resizer" @mousedown="initResize($event, 'action')"></div></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedData" :key="item.id">
              <td>{{ item.id }}</td>
              <td 
                v-for="(field, index) in visibleFieldsWithoutInterTime" 
                :key="index"
                :class="{ 'truncated': shouldTruncate(item[field]) }"
                :title="item[field]"
              >
                {{ truncateText(item[field]) }}
              </td>
              <td>{{ formatDateTime(item.start_time) }}</td>
              <td>{{ formatDateTime(item.final_time) }}</td>
              <td>
                <button class="detail-btn" @click="showDetail(item)">
                  详情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页控件 -->
      <div class="pagination-controls">
        <div class="pagination-info">
          显示第 {{ displayedFrom }} 到 {{ displayedTo }} 条，共 {{ filteredData.length }} 条数据
        </div>
        <div class="pagination-buttons">
          <button 
            @click="currentPage = 1" 
            :disabled="currentPage === 1"
            class="page-btn"
          >
            首页
          </button>
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1"
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页
          </span>
          <button 
            @click="currentPage++" 
            :disabled="currentPage === totalPages"
            class="page-btn"
          >
            下一页
          </button>
          <button 
            @click="currentPage = totalPages" 
            :disabled="currentPage === totalPages"
            class="page-btn"
          >
            末页
          </button>
        </div>
        <!-- 页面大小选择 -->
        <div class="page-size-selector">
          <label>每页显示:</label>
          <select v-model="pageSize" @change="currentPage = 1">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="200">200</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- 无数据状态 -->
    <div v-else-if="!error && !loading && (!filteredData || filteredData.length === 0)" class="no-data">
      <p>暂无数据</p>
    </div>
    
    <!-- 详情弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>详细信息</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-item" v-for="(header, index) in tableHeadersWithoutInterTime" :key="index">
            <label>{{ header }}:</label>
            <span>{{ currentDetail[tableFieldsWithoutInterTime[index]] || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>开始时间:</label>
            <span>{{ formatDateTime(currentDetail.start_time) || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>结束时间:</label>
            <span>{{ formatDateTime(currentDetail.final_time) || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>导入时间:</label>
            <span>{{ formatDateTime(currentDetail.import_date) || '-' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { lcoaAPI } from '../../services/api'

export default {
  name: 'LcoaData',
  setup() {
    const lcoaData = ref([])
    const loading = ref(false)
    const error = ref(null)
    const searchKeyword = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)  // 修改默认页面大小为10
    const sortField = ref('')
    const sortOrder = ref('asc')
    const showModal = ref(false)
    const currentDetail = ref({})
    const tableWrapper = ref(null)
    
    // 表格列标题（不含中间时间）
    const tableHeadersWithoutInterTime = ref([
      '流程节点', '标题', '流程类型', '部门', '社团',
      '流程名称', '用户名', '状态', '流程名称'
    ])
    
    // 表格列标题
    const tableHeaders = ref([
      '流程节点', '标题', '流程类型', '部门', '社团',
      '流程名称', '用户名', '状态', '流程名称', '中间时间'
    ])
    
    // 表格字段名（不含中间时间）
    const tableFieldsWithoutInterTime = ref([
      'processNode', 'Title', 'processType', 'Department', 'Club',
      'name_process', 'user_Name', 'Status', 'Process_Name'
    ])
    
    // 表格字段名
    const tableFields = ref([
      'processNode', 'Title', 'processType', 'Department', 'Club',
      'name_process', 'user_Name', 'Status', 'Process_Name', 'inter_time'
    ])
    
    // 可见列（用于响应式显示，不含中间时间）
    const getVisibleHeadersWithoutInterTime = () => {
      // 在小屏幕上只显示前几列
      const width = window.innerWidth
      if (width < 768) {
        return tableHeadersWithoutInterTime.value.slice(0, 3)
      } else if (width < 1024) {
        return tableHeadersWithoutInterTime.value.slice(0, 6)
      }
      return tableHeadersWithoutInterTime.value
    }
    
    const getVisibleFieldsWithoutInterTime = () => {
      const width = window.innerWidth
      if (width < 768) {
        return tableFieldsWithoutInterTime.value.slice(0, 3)
      } else if (width < 1024) {
        return tableFieldsWithoutInterTime.value.slice(0, 6)
      }
      return tableFieldsWithoutInterTime.value
    }
    
    // 可见列（用于响应式显示）
    const getVisibleHeaders = () => {
      // 在小屏幕上只显示前几列
      const width = window.innerWidth
      if (width < 768) {
        return tableHeaders.value.slice(0, 3)
      } else if (width < 1024) {
        return tableHeaders.value.slice(0, 6)
      }
      return tableHeaders.value
    }
    
    const getVisibleFields = () => {
      const width = window.innerWidth
      if (width < 768) {
        return tableFields.value.slice(0, 3)
      } else if (width < 1024) {
        return tableFields.value.slice(0, 6)
      }
      return tableFields.value
    }
    
    const visibleHeaders = computed(() => getVisibleHeaders())
    const visibleFields = computed(() => getVisibleFields())
    const visibleHeadersWithoutInterTime = computed(() => getVisibleHeadersWithoutInterTime())
    const visibleFieldsWithoutInterTime = computed(() => getVisibleFieldsWithoutInterTime())
    
    // 获取LCOA数据
    const fetchLcoaData = async () => {
      loading.value = true
      error.value = null
      try {
        console.log('开始获取LCOA数据...')
        const res = await lcoaAPI.getLcoaData()
        console.log('API响应:', res)
        if (res.code === 200) {
          lcoaData.value = Array.isArray(res.data) ? res.data : []
          console.log('数据加载完成，数量:', lcoaData.value.length)
        } else {
          throw new Error(res.message || '获取数据失败')
        }
      } catch (err) {
        console.error('获取LCOA数据失败:', err)
        error.value = err.response?.data?.message || err.message || '获取数据失败'
        lcoaData.value = [] // 确保在出错时将数据设为空数组
      } finally {
        loading.value = false
      }
    }
    
    // 刷新数据
    const refreshData = () => {
      console.log('Refreshing data...')
      fetchLcoaData()
    }
    
    // 执行搜索
    const performSearch = () => {
      currentPage.value = 1
    }
    
    // 过滤后的数据
    const filteredData = computed(() => {
      console.log('计算filteredData, lcoaData.value:', lcoaData.value)
      let result = lcoaData.value || []
      console.log('初始结果数量:', result.length)
      
      // 应用搜索过滤
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase()
        result = result.filter(item => {
          // 在所有列中搜索关键词（不包括中间时间）
          for (const field of tableFieldsWithoutInterTime.value) {
            const fieldValue = item[field]
            if (fieldValue && fieldValue.toLowerCase().includes(keyword)) {
              return true
            }
          }
          // 也在时间字段中搜索
          const timeFields = ['start_time', 'final_time', 'import_date']
          for (const field of timeFields) {
            const fieldValue = item[field]
            if (fieldValue && fieldValue.toLowerCase().includes(keyword)) {
              return true
            }
          }
          return false
        })
        console.log('搜索后结果数量:', result.length)
      }
      
      // 应用排序
      if (sortField.value) {
        result = [...result].sort((a, b) => {
          const aVal = a[sortField.value] || ''
          const bVal = b[sortField.value] || ''
          
          let comparison = 0
          if (typeof aVal === 'string' && typeof bVal === 'string') {
            comparison = aVal.localeCompare(bVal)
          } else {
            comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
          }
          
          return sortOrder.value === 'asc' ? comparison : -comparison
        })
        console.log('排序后结果数量:', result.length)
      }
      
      console.log('最终filteredData数量:', result.length)
      return result
    })
    
    // 分页数据
    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return (filteredData.value || []).slice(start, end)
    })
    
    // 分页信息
    const displayedFrom = computed(() => {
      return (filteredData.value || []).length > 0 ? (currentPage.value - 1) * pageSize.value + 1 : 0
    })
    
    const displayedTo = computed(() => {
      const end = currentPage.value * pageSize.value
      return end > (filteredData.value || []).length ? (filteredData.value || []).length : end
    })
    
    const totalPages = computed(() => {
      return Math.ceil((filteredData.value || []).length / pageSize.value)
    })
    
    // 排序表格
    const sortTable = (field) => {
      if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        sortField.value = field
        sortOrder.value = 'asc'
      }
    }
    
    // 显示详情
    const showDetail = (item) => {
      currentDetail.value = { ...item }
      showModal.value = true
    }
    
    // 关闭模态框
    const closeModal = () => {
      showModal.value = false
    }
    
    // 格式化日期时间
    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      return dateString
    }
    
    // 截断文本
    const truncateText = (text) => {
      if (!text) return '-'
      const str = String(text)
      return str.length > 20 ? str.substring(0, 20) + '...' : str
    }
    
    // 判断是否需要截断
    const shouldTruncate = (text) => {
      if (!text) return false
      return String(text).length > 20
    }
    
    // 监听窗口大小变化
    const handleResize = () => {
      // 触发重新计算可见列
    }
    
    // 列宽调整功能
    const initResize = (e, columnType) => {
      // 列宽调整逻辑
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      console.log('LcoaData组件已挂载')
      fetchLcoaData()
      window.addEventListener('resize', handleResize)
      
      // 添加鼠标事件监听器用于列宽调整
      window.addEventListener('mousemove', (e) => {
        // 调整列宽的逻辑
      });
      
      window.addEventListener('mouseup', () => {
        // 结束调整列宽
      });
    })
    
    return {
      lcoaData,
      loading,
      error,
      searchKeyword,
      tableHeaders,
      tableFields,
      tableHeadersWithoutInterTime,
      tableFieldsWithoutInterTime,
      visibleHeaders,
      visibleFields,
      visibleHeadersWithoutInterTime,
      visibleFieldsWithoutInterTime,
      filteredData,
      paginatedData,
      currentPage,
      pageSize,
      displayedFrom,
      displayedTo,
      totalPages,
      sortField,
      sortOrder,
      showModal,
      currentDetail,
      tableWrapper,
      refreshData,
      performSearch,
      sortTable,
      showDetail,
      closeModal,
      formatDateTime,
      truncateText,
      shouldTruncate,
      initResize
    }
  }
}
</script>

<style scoped>
.lcoa-data-container {
  background: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: relative;
  width: calc(100% - 60px);
  max-width: calc(100vw - 220px);
  box-sizing: border-box;
  margin: 20px;
}

.lcoa-data-container h2 {
  margin-top: 0;
  color: #4A90E2; /* 淡蓝色 */
  font-size: 32px; /* 放大一号 */
  text-align: center; /* 居中 */
  margin-bottom: 25px;
}

.data-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-box {
  display: flex;
  gap: 10px;
  max-width: 400px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px 0 0 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color:#00B4A0;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-btn {
  background-color:#00B4A0; /* 淡绿色 */
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.search-btn:hover {
  background-color:  #00B4A0; /* 淡绿色的深色变体 */
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  background-color:#00B4A0; /* 淡绿色 */
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #00B4A0; /* 淡绿色的深色变体 */
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  background-color: #a0b0e0;
  cursor: not-allowed;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 12px 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  border-left: 4px solid #f44336;
}

.data-table-container {
  overflow-x: auto;
  width: 100%;
  max-width: 100%;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  resize: horizontal;
  min-width: auto;
  max-width: 100%;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  min-width: 500px;
  table-layout: fixed;
  box-sizing: border-box;
}

.data-table th,
.data-table td {
  padding: 4px 6px;
  text-align: center;
  border-bottom: 1px solid #eee;
  color: #000; /* 黑色字体 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
  position: sticky;
  top: 0;
  cursor: pointer;
  user-select: none;
}

.sortable-header {
  position: relative;
  padding-right: 20px;
  user-select: none;
}

.sort-indicator {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
}

.data-table th:first-child {
  border-top-left-radius: 8px;
}

.data-table th:last-child {
  border-top-right-radius: 8px;
}

.id-column {
  width: 60px;
}

.title-column {
  width: 120px;
}

.time-column {
  width: 150px;
}

.action-column {
  width: 80px;
}

/* 列宽调整 */
.resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 5px;
  height: 100%;
  cursor: col-resize;
  background-color: transparent;
  transition: background-color 0.2s ease;
}

.resizer:hover {
  background-color: #00B4A0;
}

.resize-active {
  user-select: none;
  pointer-events: none;
}

.data-table tbody tr:hover {
  background-color: #f5f7fa;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table td.truncated {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail-btn {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.detail-btn:hover {
  background-color: #1565c0;
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 20px;
  padding: 15px 0;
}

.pagination-info {
  color: #666;
  font-size: 14px;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 14px;
}

.page-size-selector select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.page-btn {
  background-color: #f5f7fa;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
}

.page-btn:hover:not(:disabled) {
  background-color: #667eea;
  color: white;
  border-color: #667eea;
}

.page-btn:disabled {
  background-color: #f0f0f0;
  color: #999;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
  white-space: nowrap;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #667eea;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(102, 126, 234, 0.2);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.detail-item {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.detail-item label {
  font-weight: 600;
  width: 100px;
  color: #555;
  flex-shrink: 0;
}

.detail-item span {
  flex: 1;
  color: #333;
  word-break: break-word;
}

.scroll-item {
  display: flex;
  height: 30px;
  line-height: 30px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

@media (max-width: 768px) {
  .data-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .pagination-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .pagination-buttons {
    justify-content: center;
  }
  
  .lcoa-data-container {
    padding: 10px;
    width: calc(100% - 40px);
    max-width: calc(100vw - 80px);
    margin: 10px;
  }
  
  .page-size-selector {
    justify-content: center;
  }
}
</script>

<style scoped>
