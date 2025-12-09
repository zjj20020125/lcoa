<template>
  <div class="lcoa-data-section">
    <h2 class="section-title">📊 LCOA数据详情</h2>
    
    <!-- 操作栏 -->
    <div class="data-actions">
      <div class="action-buttons">
        <button class="refresh-btn" @click="refreshLcoaData" :disabled="lcoaLoading">
          {{ lcoaLoading ? '加载中...' : '刷新数据' }}
        </button>
        <div class="search-box">
          <input 
            type="text" 
            v-model="lcoaSearchKeyword" 
            placeholder="搜索数据..." 
            class="search-input"
            @keyup.enter="performLcoaSearch"
          >
          <button class="search-btn" @click="performLcoaSearch">
            🔍 搜索
          </button>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="lcoaError" class="error-message">
      错误: {{ lcoaError }}
    </div>
    
    <!-- 数据加载状态 -->
    <div v-if="lcoaLoading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载数据...</p>
    </div>
    
    <!-- 数据表格 -->
    <div class="data-table-container" v-else-if="!lcoaError && lcoaFilteredData && lcoaFilteredData.length > 0">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th class="id-column">ID</th>
              <th 
                v-for="(header, index) in lcoaTableHeaders" 
                :key="index"
                @click="sortLcoaTable(lcoaTableFields[index])"
                class="sortable-header"
              >
                {{ header }}
                <span 
                  v-if="lcoaSortField === lcoaTableFields[index]" 
                  class="sort-indicator"
                >
                  {{ lcoaSortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th 
                @click="sortLcoaTable('start_time')"
                class="sortable-header time-column"
              >
                开始时间
                <span 
                  v-if="lcoaSortField === 'start_time'" 
                  class="sort-indicator"
                >
                  {{ lcoaSortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th 
                @click="sortLcoaTable('final_time')"
                class="sortable-header time-column"
              >
                结束时间
                <span 
                  v-if="lcoaSortField === 'final_time'" 
                  class="sort-indicator"
                >
                  {{ lcoaSortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th class="action-column">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in lcoaPaginatedData" :key="item.id">
              <td>{{ item.id }}</td>
              <td 
                v-for="(field, index) in lcoaTableFields" 
                :key="index"
                :class="{ 'truncated': shouldTruncate(item[field]) }"
                :title="item[field]"
              >
                {{ truncateText(item[field]) }}
              </td>
              <td>{{ formatDateTime(item.start_time) }}</td>
              <td>{{ formatDateTime(item.final_time) }}</td>
              <td>
                <button class="detail-btn" @click="showLcoaDetail(item)">
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
          显示第 {{ lcoaDisplayedFrom }} 到 {{ lcoaDisplayedTo }} 条，共 {{ lcoaFilteredData.length }} 条数据
        </div>
        <div class="pagination-buttons">
          <button 
            @click="lcoaCurrentPage = 1" 
            :disabled="lcoaCurrentPage === 1"
            class="page-btn"
          >
            首页
          </button>
          <button 
            @click="lcoaCurrentPage--" 
            :disabled="lcoaCurrentPage === 1"
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ lcoaCurrentPage }} 页，共 {{ lcoaTotalPages }} 页
          </span>
          <button 
            @click="lcoaCurrentPage++" 
            :disabled="lcoaCurrentPage === lcoaTotalPages"
            class="page-btn"
          >
            下一页
          </button>
          <button 
            @click="lcoaCurrentPage = lcoaTotalPages" 
            :disabled="lcoaCurrentPage === lcoaTotalPages"
            class="page-btn"
          >
            末页
          </button>
        </div>
        <!-- 页面大小选择 -->
        <div class="page-size-selector">
          <label>每页显示:</label>
          <select v-model="lcoaPageSize" @change="handleLcoaPageSizeChange">
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
    <div v-else-if="!lcoaError && !lcoaLoading && (!lcoaFilteredData || lcoaFilteredData.length === 0)" class="no-data">
      <p>暂无数据</p>
    </div>
  </div>
  
  <!-- 详情弹窗 -->
  <div v-if="showLcoaModal" class="modal-overlay" @click="closeLcoaModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>详细信息</h3>
        <button class="close-btn" @click="closeLcoaModal">×</button>
      </div>
      <div class="modal-body">
        <div class="detail-item" v-for="(header, index) in lcoaTableHeaders" :key="index">
          <label>{{ header }}:</label>
          <span>{{ currentLcoaDetail[lcoaTableFields[index]] || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>开始时间:</label>
          <span>{{ formatDateTime(currentLcoaDetail.start_time) || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>结束时间:</label>
          <span>{{ formatDateTime(currentLcoaDetail.final_time) || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>导入时间:</label>
          <span>{{ formatDateTime(currentLcoaDetail.import_date) || '-' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { dataAPI as lcoaAPI } from '../../services/api'

export default {
  name: 'LcoaDataTable',
  emits: ['detail-show', 'modal-close'],
  setup(props, { emit }) {
    // 响应式数据
    const lcoaTableData = ref([])
    const lcoaLoading = ref(false)
    const lcoaError = ref(null)
    const lcoaSearchKeyword = ref('')
    const lcoaCurrentPage = ref(1)
    const lcoaPageSize = ref(10)
    const lcoaSortField = ref('')
    const lcoaSortOrder = ref('asc')
    
    // 模态框相关
    const showLcoaModal = ref(false)
    const currentLcoaDetail = ref({})
    
    // 表格相关
    const lcoaTableHeaders = ref([
      '流程ID','流程节点ID', '流程标题', '流程类型', '所属部门',
      '所属分部', '流程名称', '节点操作者', '节点操作类型'
    ])
    
    const lcoaTableFields = ref([
      'process_id','processNode', 'Title', 'processType', 'Department',
      'Club', 'Process_Name', 'user_Name', 'Status'
    ])
    
    // 计算属性
    const lcoaFilteredData = computed(() => {
      let result = lcoaTableData.value || []
      
      // 应用搜索过滤
      if (lcoaSearchKeyword.value) {
        const keyword = lcoaSearchKeyword.value.toLowerCase()
        result = result.filter(item => {
          // 在所有列中搜索关键词
          for (const field of lcoaTableFields.value) {
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
      }
      
      // 应用排序
      if (lcoaSortField.value) {
        result = [...result].sort((a, b) => {
          const aVal = a[lcoaSortField.value] || ''
          const bVal = b[lcoaSortField.value] || ''
          
          let comparison = 0
          if (typeof aVal === 'string' && typeof bVal === 'string') {
            comparison = aVal.localeCompare(bVal)
          } else {
            comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
          }
          
          return lcoaSortOrder.value === 'asc' ? comparison : -comparison
        })
      }
      
      return result
    })
    
    const lcoaPaginatedData = computed(() => {
      const start = (lcoaCurrentPage.value - 1) * lcoaPageSize.value
      const end = start + lcoaPageSize.value
      return (lcoaFilteredData.value || []).slice(start, end)
    })
    
    const lcoaDisplayedFrom = computed(() => {
      return (lcoaFilteredData.value || []).length > 0 ? (lcoaCurrentPage.value - 1) * lcoaPageSize.value + 1 : 0
    })
    
    const lcoaDisplayedTo = computed(() => {
      const end = lcoaCurrentPage.value * lcoaPageSize.value
      return end > (lcoaFilteredData.value || []).length ? (lcoaFilteredData.value || []).length : end
    })
    
    const lcoaTotalPages = computed(() => {
      return Math.ceil((lcoaFilteredData.value || []).length / lcoaPageSize.value)
    })
    
    // 工具函数
    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      return dateString
    }
    
    const truncateText = (text) => {
      if (!text) return '-'
      return text.length > 20 ? text.substring(0, 20) + '...' : text
    }
    
    const shouldTruncate = (text) => {
      return text && text.length > 20
    }
    
    // 处理函数
    const handleLcoaPageSizeChange = () => {
      lcoaCurrentPage.value = 1
    }
    
    const refreshLcoaData = () => {
      fetchLcoaTableData()
    }
    
    const performLcoaSearch = () => {
      lcoaCurrentPage.value = 1
    }
    
    const sortLcoaTable = (field) => {
      if (lcoaSortField.value === field) {
        lcoaSortOrder.value = lcoaSortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        lcoaSortField.value = field
        lcoaSortOrder.value = 'asc'
      }
    }
    
    const showLcoaDetail = (item) => {
      currentLcoaDetail.value = { ...item }
      showLcoaModal.value = true
      emit('detail-show', item)
    }
    
    const closeLcoaModal = () => {
      showLcoaModal.value = false
      emit('modal-close')
    }
    
    // 数据获取函数
    const fetchLcoaTableData = async () => {
      lcoaLoading.value = true
      lcoaError.value = null
      try {
        const res = await lcoaAPI.getLcoaData()
        if (res.code === 200) {
          lcoaTableData.value = Array.isArray(res.data) ? res.data : []
        } else {
          throw new Error(res.message || '获取数据失败')
        }
      } catch (err) {
        lcoaError.value = err.response?.data?.message || err.message || '获取数据失败'
        lcoaTableData.value = []
      } finally {
        lcoaLoading.value = false
      }
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      fetchLcoaTableData()
    })
    
    // 暴露给父组件的方法
    const loadData = () => {
      fetchLcoaTableData()
    }
    
    return {
      // 数据属性
      lcoaTableData,
      lcoaLoading,
      lcoaError,
      lcoaSearchKeyword,
      lcoaCurrentPage,
      lcoaPageSize,
      lcoaSortField,
      lcoaSortOrder,
      showLcoaModal,
      currentLcoaDetail,
      lcoaTableHeaders,
      lcoaTableFields,
      
      // 计算属性
      lcoaFilteredData,
      lcoaPaginatedData,
      lcoaDisplayedFrom,
      lcoaDisplayedTo,
      lcoaTotalPages,
      
      // 方法
      formatDateTime,
      truncateText,
      shouldTruncate,
      handleLcoaPageSizeChange,
      refreshLcoaData,
      performLcoaSearch,
      sortLcoaTable,
      showLcoaDetail,
      closeLcoaModal,
      loadData
    }
  }
}
</script>

<style scoped>
.lcoa-data-section {
  margin-top: 30px;
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.section-title {
  color: #333;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.data-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.refresh-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.refresh-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.search-box {
  display: flex;
  gap: 5px;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 200px;
  max-width: 100%;
}

.search-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-size: 14px;
}

.search-btn:hover {
  background-color: #45a049;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  border-left: 4px solid #f44336;
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

.data-table-container {
  overflow-x: auto;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #eee;
  border-radius: 6px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.data-table th,
.data-table td {
  padding: 12px 8px;
  text-align: center;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
  position: relative;
}

.data-table th.sortable-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.data-table th.sortable-header:hover {
  background-color: #e9ecef;
}

.sort-indicator {
  margin-left: 5px;
  font-size: 12px;
}

.data-table td {
  color: #666;
}

.data-table tr:hover td {
  background-color: #f8f9fa;
}

.truncated {
  cursor: help;
}

.id-column {
  width: 60px;
}

.time-column {
  width: 150px;
}

.action-column {
  width: 80px;
}

.detail-btn {
  background-color: #17a2b8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  font-size: 13px;
}

.detail-btn:hover {
  background-color: #138496;
}

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 20px;
  padding: 15px 0;
  border-top: 1px solid #eee;
}

.pagination-info {
  color: #666;
  font-size: 14px;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
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
  
  .page-size-selector {
    justify-content: center;
  }
  
  .detail-item {
    flex-direction: column;
  }
  
  .detail-item label {
    width: auto;
    margin-bottom: 5px;
  }
}
</style><template>
  <div class="lcoa-data-section">
    <h2 class="section-title">📊 LCOA数据详情</h2>
    
    <!-- 操作栏 -->
    <div class="data-actions">
      <div class="action-buttons">
        <button class="refresh-btn" @click="refreshLcoaData" :disabled="lcoaLoading">
          {{ lcoaLoading ? '加载中...' : '刷新数据' }}
        </button>
        <div class="search-box">
          <input 
            type="text" 
            v-model="lcoaSearchKeyword" 
            placeholder="搜索数据..." 
            class="search-input"
            @keyup.enter="performLcoaSearch"
          >
          <button class="search-btn" @click="performLcoaSearch">
            🔍 搜索
          </button>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="lcoaError" class="error-message">
      错误: {{ lcoaError }}
    </div>
    
    <!-- 数据加载状态 -->
    <div v-if="lcoaLoading" class="loading-state">
      <div class="spinner"></div>
      <p>正在加载数据...</p>
    </div>
    
    <!-- 数据表格 -->
    <div class="data-table-container" v-else-if="!lcoaError && lcoaFilteredData && lcoaFilteredData.length > 0">
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th 
                v-for="(header, index) in lcoaTableHeaders" 
                :key="index"
                @click="sortLcoaTable(lcoaTableFields[index])"
                class="sortable-header"
              >
                {{ header }}
                <span 
                  v-if="lcoaSortField === lcoaTableFields[index]" 
                  class="sort-indicator"
                >
                  {{ lcoaSortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th 
                @click="sortLcoaTable('start_time')"
                class="sortable-header time-column"
              >
                开始时间
                <span 
                  v-if="lcoaSortField === 'start_time'" 
                  class="sort-indicator"
                >
                  {{ lcoaSortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th 
                @click="sortLcoaTable('final_time')"
                class="sortable-header time-column"
              >
                结束时间
                <span 
                  v-if="lcoaSortField === 'final_time'" 
                  class="sort-indicator"
                >
                  {{ lcoaSortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th class="action-column">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in lcoaPaginatedData" :key="item.id">
              <td 
                v-for="(field, index) in lcoaTableFields" 
                :key="index"
                :class="{ 'truncated': shouldTruncate(item[field]) }"
                :title="item[field]"
              >
                {{ truncateText(item[field]) }}
              </td>
              <td>{{ formatDateTime(item.start_time) }}</td>
              <td>{{ formatDateTime(item.final_time) }}</td>
              <td>
                <button class="detail-btn" @click="showLcoaDetail(item)">
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
          显示第 {{ lcoaDisplayedFrom }} 到 {{ lcoaDisplayedTo }} 条，共 {{ lcoaFilteredData.length }} 条数据
        </div>
        <div class="pagination-buttons">
          <button 
            @click="lcoaCurrentPage = 1" 
            :disabled="lcoaCurrentPage === 1"
            class="page-btn"
          >
            首页
          </button>
          <button 
            @click="lcoaCurrentPage--" 
            :disabled="lcoaCurrentPage === 1"
            class="page-btn"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ lcoaCurrentPage }} 页，共 {{ lcoaTotalPages }} 页
          </span>
          <button 
            @click="lcoaCurrentPage++" 
            :disabled="lcoaCurrentPage === lcoaTotalPages"
            class="page-btn"
          >
            下一页
          </button>
          <button 
            @click="lcoaCurrentPage = lcoaTotalPages" 
            :disabled="lcoaCurrentPage === lcoaTotalPages"
            class="page-btn"
          >
            末页
          </button>
        </div>
        <!-- 页面大小选择 -->
        <div class="page-size-selector">
          <label>每页显示:</label>
          <select v-model="lcoaPageSize" @change="handleLcoaPageSizeChange">
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
    <div v-else-if="!lcoaError && !lcoaLoading && (!lcoaFilteredData || lcoaFilteredData.length === 0)" class="no-data">
      <p>暂无数据</p>
    </div>
  </div>
  
  <!-- 详情弹窗 -->
  <div v-if="showLcoaModal" class="modal-overlay" @click="closeLcoaModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>详细信息</h3>
        <button class="close-btn" @click="closeLcoaModal">×</button>
      </div>
      <div class="modal-body">
        <div class="detail-item" v-for="(header, index) in lcoaTableHeaders" :key="index">
          <label>{{ header }}:</label>
          <span>{{ currentLcoaDetail[lcoaTableFields[index]] || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>开始时间:</label>
          <span>{{ formatDateTime(currentLcoaDetail.start_time) || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>结束时间:</label>
          <span>{{ formatDateTime(currentLcoaDetail.final_time) || '-' }}</span>
        </div>
        <div class="detail-item">
          <label>导入时间:</label>
          <span>{{ formatDateTime(currentLcoaDetail.import_date) || '-' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { dataAPI as lcoaAPI } from '../../services/api'

export default {
  name: 'LcoaDataTable',
  emits: ['detail-show', 'modal-close'],
  setup(props, { emit }) {
    // 响应式数据
    const lcoaTableData = ref([])
    const lcoaLoading = ref(false)
    const lcoaError = ref(null)
    const lcoaSearchKeyword = ref('')
    const lcoaCurrentPage = ref(1)
    const lcoaPageSize = ref(10)
    const lcoaSortField = ref('')
    const lcoaSortOrder = ref('asc')
    
    // 模态框相关
    const showLcoaModal = ref(false)
    const currentLcoaDetail = ref({})
    
    // 表格相关
    const lcoaTableHeaders = ref([
      '流程ID','流程节点ID', '流程标题', '流程类型', '所属部门',
      '所属分部', '流程名称', '节点操作者', '节点操作类型'
    ])
    
    const