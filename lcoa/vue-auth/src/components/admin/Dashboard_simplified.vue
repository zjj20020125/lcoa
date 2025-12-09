<template>
  <div class="dashboard">
    <div v-if="componentError" class="error-container">
      <h2>组件加载错误</h2>
      <p>{{ componentError }}</p>
      <button @click="reloadComponent" class="retry-btn">重新加载</button>
    </div>
    <div v-else>
      <h1>数据看板</h1>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-title">LCOA数据总量</div>
          <div class="stat-value" v-if="!loading.lcoa">{{ formatNumber(lcoaTotal) }}</div>
          <div class="stat-value" v-else>加载中...</div>
          <div class="stat-change" :class="{ positive: lcoaTotal > 0 }">
            {{ lcoaTotal > 0 ? '已加载' : '无数据' }}
          </div>
          <div v-if="error.lcoa" class="stat-error">错误: {{ error.lcoa }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">LCOA未处理流程总量</div>
          <div class="stat-value" v-if="!loading.sysDeal">{{ formatNumber(sysDealTotal) }}</div>
          <div class="stat-value" v-else>加载中...</div>
          <div class="stat-change" :class="{ positive: sysDealTotal > 0 }">
            {{ sysDealTotal > 0 ? '已加载' : '无数据' }}
          </div>
          <div v-if="error.sysDeal" class="stat-error">错误: {{ error.sysDeal }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">LCOA记录最大ID</div>
          <div class="stat-value" v-if="lcoaMaxId !== null">{{ formatNumber(lcoaMaxId) }}</div>
          <div class="stat-value" v-else>加载中...</div>
          <div class="stat-change" :class="{ positive: lcoaMaxId > 0 }">
            {{ lcoaMaxId > 0 ? '已加载' : '无数据' }}
          </div>
        </div>
      </div>

      <!-- 数据概览 -->
      <div class="charts-container">
        <div class="chart-card">
          <h3>访问趋势</h3>
          <div class="chart-container">
            <canvas ref="barChartCanvas" v-if="barChartData.length > 0"></canvas>
            <div v-else class="chart-placeholder">{{ chartLoading ? '数据加载中...' : '暂无数据' }}</div>
          </div>
        </div>
        <div class="chart-card">
          <h3>用户分布</h3>
          <div class="chart-container">
            <canvas ref="userPieChartCanvas" v-if="userPieChartData.length > 0"></canvas>
            <div v-else class="chart-placeholder">{{ chartLoading ? '数据加载中...' : '暂无数据' }}</div>
          </div>
        </div>
        <div class="chart-card">
          <h3 class="xiangxi-title">{{ getXiangxiDateInfo || '详细信息' }}数据</h3>
          <div class="scroll-container xiangxi-scroll-container">
            <div class="scroll-header">
              <div class="header-item">姓名</div>
              <div class="header-item">部门</div>
              <div class="header-item">流程状态</div>
              <div class="header-item">数量</div>
            </div>
            <div class="scroll-content" ref="xiangxiScrollContent">
              <div 
                class="scroll-item-wrapper"
                :class="{ animating: isXiangxiScrolling }"
                :style="{ transform: `translateY(${xiangxiScrollOffset}px)` }"
              >
                <div 
                  class="scroll-item" 
                  v-for="(item, index) in xiangxiData" 
                  :key="index"
                  :class="{ even: index % 2 === 0 }"
                >
                  <div class="item-cell name-cell">{{ item.姓名 }}</div>
                  <div class="item-cell department-cell">{{ item.部门 }}</div>
                  <div class="item-cell status-cell">{{ item.流程状态 }}</div>
                  <div class="item-cell count-cell">{{ item.数量 }}</div>
                </div>
              </div>
            </div>
            <div class="scroll-placeholder" v-if="xiangxiData.length === 0">
              {{ xiangxiLoading ? '数据加载中...' : (xiangxiError ? '数据加载失败: ' + xiangxiError : '暂无数据') }}
            </div>
          </div>
          <div class="data-info xiangxi-data-info">
            共 {{ xiangxiData.length }} 条记录
          </div>
        </div>
      </div>

      <!-- LCOA数据展示 -->
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
    </div>
  </div>
</template>

<script>
import { onMounted, onUnmounted, ref, watch, nextTick, computed } from 'vue'
import { dataAPI as lcoaAPI } from '../../services/api'
import Chart from 'chart.js/auto'

export default {
  name: 'Dashboard',
  setup() {
    // 响应式数据
    const componentError = ref(null)
    const lcoaTotal = ref(0)
    const lcoaData = ref([])
    const lcoaTableData = ref([])
    const lcoaLoading = ref(false)
    const lcoaError = ref(null)
    const lcoaSearchKeyword = ref('')
    const lcoaCurrentPage = ref(1)
    const lcoaPageSize = ref(10)
    const lcoaSortField = ref('')
    const lcoaSortOrder = ref('asc')
    const lcoaMaxId = ref(0)
    
    // sys_deal数据相关
    const sysDealTotal = ref(0)
    const clubData = ref([])
    const chartLoading = ref(false)
    const pieChartCanvas = ref(null)
    let pieChart = null
    
    // 图表数据
    const barChartCanvas = ref(null)
    let barChart = null
    const barChartData = ref([])
    
    const userPieChartCanvas = ref(null)
    let userPieChart = null
    const userPieChartData = ref([])
    
    // xiangxi数据相关
    const xiangxiData = ref([])
    const xiangxiLoading = ref(false)
    const xiangxiError = ref(null)
    const xiangxiScrollContent = ref(null)
    const xiangxiScrollOffset = ref(0)
    const isXiangxiScrolling = ref(false)
    const xiangxiItemHeight = 35
    let xiangxiScrollInterval = null
    
    // 加载状态和错误信息
    const loading = ref({
      lcoa: false,
      sysDeal: false,
      club: false
    })
    
    const error = ref({
      lcoa: null,
      sysDeal: null,
      club: null
    })
    
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
    const getXiangxiDateInfo = computed(() => {
      if (xiangxiData.value.length > 0) {
        return xiangxiData.value[0].import_date || ''
      }
      return ''
    })
    
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
    
    const formatNumber = (num) => {
      if (num === null || num === undefined) return '-'
      return num.toLocaleString()
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
    }
    
    const closeLcoaModal = () => {
      showLcoaModal.value = false
    }
    
    const reloadComponent = () => {
      componentError.value = null
      initComponent()
    }
    
    // 数据获取函数
    const fetchLcoaCount = async () => {
      loading.value.lcoa = true
      error.value.lcoa = null
      try {
        const res = await lcoaAPI.getLcoaCount()
        if (res.code === 200) {
          lcoaTotal.value = res.data.total
        } else {
          throw new Error(res.message || '获取数据失败')
        }
      } catch (err) {
        error.value.lcoa = err.response?.data?.message || err.message || '获取数据失败'
      } finally {
        loading.value.lcoa = false
      }
    }
    
    const fetchLcoaMaxId = async () => {
      try {
        const res = await lcoaAPI.getLcoaMaxId()
        if (res.code === 200) {
          lcoaMaxId.value = res.data.max_id
        } else {
          throw new Error(res.message || '获取数据失败')
        }
      } catch (err) {
        console.error('获取LCOA表最大ID值失败', err)
      }
    }
    
    const fetchSysDealCount = async () => {
      loading.value.sysDeal = true
      error.value.sysDeal = null
      try {
        const res = await lcoaAPI.getSysDealCount()
        if (res.code === 200) {
          sysDealTotal.value = res.data.total
        } else {
          throw new Error(res.message || '获取数据失败')
        }
      } catch (err) {
        error.value.sysDeal = err.response?.data?.message || err.message || '获取数据失败'
      } finally {
        loading.value.sysDeal = false
      }
    }
    
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
    
    const fetchXiangxiLatestData = async () => {
      xiangxiLoading.value = true
      xiangxiError.value = null
      try {
        const res = await lcoaAPI.getSysXiangxiLatest()
        if (res.code === 200) {
          xiangxiData.value = Array.isArray(res.data) ? res.data : []
          nextTick(() => {
            startXiangxiScrolling()
          })
        } else {
          throw new Error(res.message || '获取数据失败')
        }
      } catch (err) {
        xiangxiError.value = err.response?.data?.message || err.message || '获取数据失败'
        xiangxiData.value = []
      } finally {
        xiangxiLoading.value = false
      }
    }
    
    const fetchClubData = async () => {
      chartLoading.value = true
      error.value.club = null
      try {
        const res = await lcoaAPI.getSysClubLatest()
        if (res.code === 200) {
          clubData.value = res.data
          await nextTick()
          drawPieChart()
        } else {
          throw new Error(res.message || '获取部门数据失败')
        }
      } catch (err) {
        error.value.club = err.response?.data?.message || err.message || '获取部门数据失败'
      } finally {
        chartLoading.value = false
      }
    }
    
    const fetchAndFilterClubData = async () => {
      try {
        const res = await lcoaAPI.getSysClubLatest()
        if (res.code === 200) {
          const targetDepartments = [
            '经营管理部', 
            '制造管理部', 
            '工艺技术部', 
            '市场营销部', 
            '质量管理部',
            '钢构件本部',
            '铝合金车间',
            '财务管理部'
          ]
          
          const departmentMap = {}
          res.data.forEach(item => {
            departmentMap[item.部门] = item.人数
          })
          
          const chartData = targetDepartments.map(department => ({
            label: department,
            value: departmentMap[department] || 0
          }))
          
          userPieChartData.value = chartData
          nextTick(() => {
            drawUserPieChart()
          })
        } else {
          throw new Error(res.message || '获取部门数据失败')
        }
      } catch (err) {
        console.error('获取部门数据失败', err)
        generateUserPieChartData()
        nextTick(() => {
          drawUserPieChart()
        })
      }
    }
    
    // 图表相关函数
    const generateBarChartData = () => {
      const data = []
      for (let i = 0; i < 5; i++) {
        data.push({
          label: `第${i+1}月`,
          value: Math.floor(Math.random() * 1000) + 100
        })
      }
      barChartData.value = data
    }
    
    const drawBarChart = () => {
      if (!barChartCanvas.value || barChartData.value.length === 0) return
      
      if (barChart) {
        barChart.destroy()
      }
      
      const ctx = barChartCanvas.value.getContext('2d')
      const labels = barChartData.value.map(item => item.label)
      const data = barChartData.value.map(item => item.value)
      
      barChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: '访问量',
            data: data,
            backgroundColor: [
              '#36A2EB',
              '#4BC0C0',
              '#FF6384',
              '#FF9F40',
              '#9966FF'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }
    
    const drawPieChart = () => {
      if (!pieChartCanvas.value || clubData.value.length === 0) return
      
      if (pieChart) {
        pieChart.destroy()
      }
      
      const ctx = pieChartCanvas.value.getContext('2d')
      const labels = clubData.value.map(item => item.department)
      const data = clubData.value.map(item => item.count)
      
      const backgroundColors = [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40',
        '#FF6384',
        '#C9CBCF'
      ]
      
      pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: backgroundColors.slice(0, data.length),
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }
    
    const generateUserPieChartData = () => {
      const data = [
        { label: '经营管理部', value: 25 },
        { label: '制造管理部', value: 30 },
        { label: '工艺技术部', value: 20 },
        { label: '市场营销部', value: 35 },
        { label: '质量管理部', value: 15 }
      ]
      userPieChartData.value = data
    }
    
    const drawUserPieChart = () => {
      if (!userPieChartCanvas.value || userPieChartData.value.length === 0) return
      
      if (userPieChart) {
        userPieChart.destroy()
      }
      
      const ctx = userPieChartCanvas.value.getContext('2d')
      const labels = userPieChartData.value.map(item => item.label)
      const data = userPieChartData.value.map(item => item.value)
      
      const backgroundColors = [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40',
        '#FF6B8B',
        '#2ED08A'
      ]
      
      userPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: backgroundColors,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }
    
    // 滚动相关函数
    const startXiangxiScrolling = () => {
      stopXiangxiScrolling()
      
      if (xiangxiData.value.length > 5) {
        xiangxiScrollInterval = setInterval(() => {
          isXiangxiScrolling.value = true
          const totalItems = xiangxiData.value.length
          const itemHeight = xiangxiItemHeight
          const maxOffset = -(totalItems * itemHeight)
          
          let currentOffset = xiangxiScrollOffset.value
          const targetOffset = currentOffset - itemHeight
          
          if (Math.abs(targetOffset) >= Math.abs(maxOffset)) {
            xiangxiScrollOffset.value = 0
          } else {
            xiangxiScrollOffset.value = targetOffset
          }
        }, 3000)
      }
    }
    
    const stopXiangxiScrolling = () => {
      if (xiangxiScrollInterval) {
        clearInterval(xiangxiScrollInterval)
        xiangxiScrollInterval = null
      }
      isXiangxiScrolling.value = false
      xiangxiScrollOffset.value = 0
    }
    
    // 初始化组件
    const initComponent = async () => {
      try {
        fetchLcoaCount()
        fetchLcoaMaxId()
        fetchSysDealCount()
        fetchClubData()
        fetchAndFilterClubData()
        generateBarChartData()
        fetchLcoaTableData()
        fetchXiangxiLatestData()
        
        nextTick(() => {
          drawBarChart()
          drawPieChart()
          drawUserPieChart()
        })
      } catch (error) {
        componentError.value = '组件初始化失败: ' + (error.message || '未知错误')
      }
    }
    
    onMounted(() => {
      initComponent()
    })
    
    onUnmounted(() => {
      stopXiangxiScrolling()
    })
    
    return {
      componentError,
      lcoaTotal,
      sysDealTotal,
      lcoaMaxId,
      clubData,
      barChartData,
      userPieChartData,
      loading,
      error,
      lcoaTableData,
      lcoaLoading,
      lcoaError,
      lcoaSearchKeyword,
      lcoaCurrentPage,
      lcoaPageSize,
      lcoaSortField,
      lcoaSortOrder,
      lcoaFilteredData,
      lcoaPaginatedData,
      lcoaTableHeaders,
      lcoaTableFields,
      getXiangxiDateInfo,
      showLcoaModal,
      currentLcoaDetail,
      xiangxiData,
      xiangxiLoading,
      xiangxiError,
      xiangxiScrollContent,
      xiangxiScrollOffset,
      isXiangxiScrolling,
      xiangxiItemHeight,
      refreshLcoaData,
      performLcoaSearch,
      sortLcoaTable,
      closeLcoaModal,
      formatDateTime,
      formatNumber,
      handleLcoaPageSizeChange,
      startXiangxiScrolling,
      stopXiangxiScrolling,
      reloadComponent,
      showLcoaDetail,
      truncateText,
      shouldTruncate
    }
  }
}
</script>

<style scoped>
.dashboard h1 {
  color: #333;
  margin-top: 0;
  margin-bottom: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stat-title {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-error {
  font-size: 12px;
  color: #f44336;
  margin-top: 5px;
}

.positive {
  color: #4caf50;
}

.negative {
  color: #f44336;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.chart-card {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.chart-card h3 {
  color: #333;
  margin-top: 0;
  margin-bottom: 12px;
}

.xiangxi-title {
  background: linear-gradient(90deg, #4A90E2, #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  font-weight: 600;
  padding: 5px 0;
}

.chart-container {
  height: 250px;
  position: relative;
}

.chart-placeholder {
  height: 250px;
  background-color: #f5f7fa;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.scroll-container {
  height: 250px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.xiangxi-scroll-container {
  height: 210px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.scroll-content {
  height: 170px;
  overflow: hidden;
  position: relative;
}

.scroll-item-wrapper {
  transition: transform 0.5s ease-in-out;
}

.scroll-item {
  display: flex;
  height: 30px;
  line-height: 30px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.scroll-item:hover {
  background-color: #f0f8ff;
}

.scroll-item.even {
  background-color: #fafafa;
}

.scroll-placeholder {
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.data-table th,
.data-table td {
  padding: 4px 6px;
  text-align: center;
  border-bottom: 1px solid #eee;
  color: #000;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lcoa-data-section {
  margin-top: 30px;
  background: white;
  border-radius: 10px;
  padding: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.section-title {
  margin-top: 0;
  color: #4A90E2;
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
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
  background-color:#00B4A0;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.search-btn:hover {
  background-color: #00B4A0;
}

.refresh-btn {
  background-color:#00B4A0;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #00B4A0;
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
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: auto;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  min-width: 500px;
  table-layout: fixed;
  box-sizing: border-box;
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

.id-column {
  width: 60px;
}

.time-column {
  width: 150px;
}

.action-column {
  width: 80px;
}

.data-table tbody tr:hover {
  background-color: #f5f7fa;
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

.data-info {
  text-align: center;
  padding: 15px;
  color: #666;
  font-size: 14px;
}

.xiangxi-data-info {
  background-color: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  border-radius: 0 0 6px 6px;
  font-weight: 500;
  color: #555;
}

.scroll-header {
  display: flex;
  background: linear-gradient(180deg, #3a3a52 0%, #2c2c44 100%);
  color: white;
  font-weight: bold;
  padding: 10px 0;
  border-bottom: 1px solid #e0e0e0;
}

.header-item, .item-cell {
  flex: 1;
  text-align: center;
  padding: 0 8px;
}

.name-cell {
  font-weight: 500;
  color: #333;
}

.department-cell {
  color: #666;
}

.status-cell {
  color: #4caf50;
  font-weight: 500;
}

.count-cell {
  color: #2196f3;
  font-weight: 600;
}

.scroll-item {
  display: flex;
  height: 35px;
  line-height: 35px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
  font-size: 13px;
}

.scroll-item:hover {
  background-color: #e3f2fd;
}

.scroll-item.even {
  background-color: #fafafa;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .scroll-header, .scroll-item {
    font-size: 14px;
  }
  
  .header-item, .item-cell {
    padding: 0 5px;
  }
  
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
}
</style>