<template>
  <div class="dashboard">
    <div v-if="componentError" class="error-container">
      <h2>组件加载错误</h2>
      <p>{{ componentError }}</p> <!-- 补全错误信息显示 -->
      <button @click="reloadComponent" class="retry-btn">重新加载</button>
    </div>
    <div v-else>
      <h1>联诚结构件OA流程未处理数据看板</h1>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-title">LCOA数据总量</div>
          <div class="stat-value" v-if="!loading.lcoa">{{ lcoaTotal }}</div>
          <div class="stat-value" v-else>加载中...</div>
          <div class="stat-change" :class="{ positive: lcoaTotal > 0 }">
            {{ lcoaTotal > 0 ? '已加载' : '无数据' }}
          </div>
          <div v-if="error.lcoa" class="stat-error">错误: {{ error.lcoa }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">LCOA未处理流程总量</div>
          <div class="stat-value" v-if="!loading.sysDeal">{{ sysDealTotal }}</div>
          <div class="stat-value" v-else>加载中...</div>
          <div class="stat-change" :class="{ positive: sysDealTotal > 0 }">
            {{ sysDealTotal > 0 ? '已加载' : '无数据' }}
          </div>
          <div v-if="error.sysDeal" class="stat-error">错误: {{ error.sysDeal }}</div>
        </div>
      </div>

      <!-- 数据概览 -->
      <div class="charts-container">

        <!-- 部门人员分布扇形图 -->
        <div class="chart-card">
          <h3 class="club-title">{{ xiangxiLatestDate || clubLatestDate ? (xiangxiLatestDate || clubLatestDate) + '部门人员' : '部门人员' }}</h3>
          <div class="chart-container">
            <canvas ref="clubPieChartCanvas" v-if="clubPieChartData.length > 0"></canvas>
            <div v-else class="chart-placeholder">{{ chartLoading ? '数据加载中...' : '暂无数据' }}</div>
          </div>
        </div>
        <div class="chart-card">
          <h3 class="xiangxi-title">{{ xiangxiLatestDate || clubLatestDate ? (xiangxiLatestDate || clubLatestDate) + '部门人员' : '部门人员' }}</h3>
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
        
        <!-- xiangxi每日统计数据图表（新增） -->
        <div class="chart-card">
          <h3>最近七天数据统计</h3>
          <div class="chart-container">
            <canvas ref="xiangxiStatsChartCanvas" v-if="xiangxiDailyStats.length > 0"></canvas>
            <div v-else class="chart-placeholder">{{ xiangxiDailyStatsLoading ? '数据加载中...' : '暂无数据' }}</div>
          </div>
          <div class="data-info" v-if="xiangxiDailyStats.length > 0">
            总计: {{ xiangxiDailyStats.reduce((sum, item) => sum + item.count, 0) }} 条记录
          </div>
        </div>
      </div>

      <!-- LCOA数据展示 -->
      <div class="lcoa-data-section">
        <h2 class="section-title">📊 未处理流程数据详情</h2>

        <!-- 操作栏 -->
        <div class="data-actions">
          <div class="action-buttons">
            <button class="refresh-btn" @click="refreshNodealData" :disabled="nodealLoading">
              {{ nodealLoading ? '加载中...' : '刷新数据' }}
            </button>
            <div class="search-box">
              <input
                type="text"
                v-model="nodealSearchKeyword"
                placeholder="搜索数据..."
                class="search-input"
                @keyup.enter="performNodealSearch"
              >
              <button class="search-btn" @click="performNodealSearch">
                🔍 搜索
              </button>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="nodealError" class="error-message">
          错误: {{ nodealError }}
        </div>

        <!-- 数据加载状态 -->
        <div v-if="nodealLoading" class="loading-state">
          <div class="spinner"></div>
          <p>正在加载数据...</p>
        </div>

        <!-- 数据表格 -->
        <div class="data-table-container" v-else-if="!nodealError && nodealFilteredData && nodealFilteredData.length > 0">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th
                    @click="sortNodealTable('extracted_date')"
                    class="sortable-header time-column"
                    :title="'导入时间'"
                  >
                    导入时间
                    <span
                      v-if="nodealSortField === 'extracted_date'"
                      class="sort-indicator"
                    >
                      {{ nodealSortOrder === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th
                    v-for="(header, index) in nodealTableHeaders"
                    :key="index"
                    @click="sortNodealTable(nodealTableFields[index])"
                    class="sortable-header"
                    :title="header"
                  >
                    {{ header }}
                    <span
                      v-if="nodealSortField === nodealTableFields[index]"
                      class="sort-indicator"
                    >
                      {{ nodealSortOrder === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th
                    @click="sortNodealTable('first_receive_time')"
                    class="sortable-header time-column"
                    :title="'最初接收时间'"
                  >
                    最初接收时间
                    <span
                      v-if="nodealSortField === 'first_receive_time'"
                      class="sort-indicator"
                    >
                      {{ nodealSortOrder === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th
                    @click="sortNodealTable('last_process_time')"
                    class="sortable-header time-column"
                    :title="'最后处理时间'"
                  >
                    最后处理时间
                    <span
                      v-if="nodealSortField === 'last_process_time'"
                      class="sort-indicator"
                    >
                      {{ nodealSortOrder === 'asc' ? '↑' : '↓' }}
                    </span>
                  </th>
                  <th class="action-column" :title="'操作'">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in nodealPaginatedData" :key="item.id">
                  <td :title="formatDateTime(item.extracted_date)">{{ formatDateTime(item.extracted_date) }}</td>
                  <td
                    v-for="(field, index) in nodealTableFields"
                    :key="index"
                    :class="{ 'truncated': shouldTruncate(item[field]) }"
                    :title="item[field]"
                  >
                    {{ truncateText(item[field]) }}
                  </td>
                  <td :title="formatDateTime(item.first_receive_time)">{{ formatDateTime(item.first_receive_time) }}</td>
                  <td :title="formatDateTime(item.last_process_time)">{{ formatDateTime(item.last_process_time) }}</td>
                  <td>
                    <button class="detail-btn" @click="showNodealDetail(item)">
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
              显示第 {{ nodealDisplayedFrom }} 到 {{ nodealDisplayedTo }} 条，共 {{ nodealFilteredData.length }} 条数据
            </div>
            <div class="pagination-buttons">
              <button
                @click="nodealCurrentPage = 1"
                :disabled="nodealCurrentPage === 1"
                class="page-btn"
              >
                首页
              </button>
              <button
                @click="nodealCurrentPage--"
                :disabled="nodealCurrentPage === 1"
                class="page-btn"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ nodealCurrentPage }} 页，共 {{ nodealTotalPages }} 页
              </span>
              <button
                @click="nodealCurrentPage++"
                :disabled="nodealCurrentPage === nodealTotalPages"
                class="page-btn"
              >
                下一页
              </button>
              <button
                @click="nodealCurrentPage = nodealTotalPages"
                :disabled="nodealCurrentPage === nodealTotalPages"
                class="page-btn"
              >
                末页
              </button>
            </div>
            <!-- 页面大小选择 -->
            <div class="page-size-selector">
              <label>每页显示:</label>
              <select v-model="nodealPageSize" @change="handleNodealPageSizeChange">
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
        <div v-else-if="!nodealError && !nodealLoading && (!nodealFilteredData || nodealFilteredData.length === 0)" class="no-data">
          <p>暂无数据</p>
        </div>
      </div>

      <!-- 详情弹窗 -->
      <div v-if="showNodealModal" class="modal-overlay" @click="closeNodealModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>详细信息</h3>
            <button class="close-btn" @click="closeNodealModal">×</button>
          </div>
          <div class="modal-body">
            <div class="detail-item">
              <label>导入时间:</label>
              <span>{{ formatDateTime(currentNodealDetail.extracted_date) || '-' }}</span>
            </div>
            <div class="detail-item" v-for="(header, index) in nodealTableHeaders" :key="index">
              <label>{{ header }}:</label>
              <span>{{ currentNodealDetail[nodealTableFields[index]] || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>最初接收时间:</label>
              <span>{{ formatDateTime(currentNodealDetail.first_receive_time) || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>最后处理时间:</label>
              <span>{{ formatDateTime(currentNodealDetail.last_process_time) || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>总计耗时:</label>
              <span>{{ currentNodealDetail.total_duration || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>总计超时:</label>
              <span>{{ currentNodealDetail.total_timeout || '-' }}</span>
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
    const lcoaTableData = ref([]) // 补全缺失的响应式数据定义
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
    const clubLatestDate = ref('')

    // 图表数据（仅保留用到的图表）
    const barChartCanvas = ref(null)
    let barChart = null
    const barChartData = ref([])

    // 部门人员分布扇形图
    const clubPieChartCanvas = ref(null)
    let clubPieChart = null
    const clubPieChartData = ref([])

    // xiangxi数据相关
    const xiangxiData = ref([])
    const xiangxiLoading = ref(false)
    const xiangxiError = ref(null)
    const xiangxiScrollContent = ref(null)
    const xiangxiScrollOffset = ref(0)
    const isXiangxiScrolling = ref(false)
    const xiangxiItemHeight = 35
    const xiangxiLatestDate = ref('')
    let xiangxiScrollInterval = null
    
    // xiangxi每日统计数据相关（新增）
    const xiangxiDailyStats = ref([])
    const xiangxiDailyStatsLoading = ref(false)
    const xiangxiDailyStatsError = ref(null)
    const xiangxiStatsChartCanvas = ref(null)
    let xiangxiStatsChart = null

    // nodeal数据相关（新增）
    const nodealData = ref([])
    const nodealTableData = ref([])
    const nodealLoading = ref(false)
    const nodealError = ref(null)
    const nodealSearchKeyword = ref('')
    const nodealCurrentPage = ref(1)
    const nodealPageSize = ref(10)
    const nodealSortField = ref('')
    const nodealSortOrder = ref('asc')
    const showNodealModal = ref(false)
    const currentNodealDetail = ref({})

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

    // nodeal表头（新增）
    const nodealTableHeaders = ref([
      '流程ID', '流程节点ID', '流程标题', '流程类型', '所属部门',
      '所属分部', '流程名称', '节点操作者', '节点操作类型', '节点名称'
    ])

    const nodealTableFields = ref([
      'process_id', 'process_node_id', 'process_title', 'process_type', 'department',
      'branch', 'process_name', 'node_operator', 'node_operation_type', 'node_name'
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
          return false // 修复：补充返回值，避免语法错误
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

    // nodeal计算属性（新增）
    const nodealFilteredData = computed(() => {
      let result = nodealTableData.value || []

      // 应用搜索过滤
      if (nodealSearchKeyword.value) {
        const keyword = nodealSearchKeyword.value.toLowerCase()
        result = result.filter(item => {
          // 在所有列中搜索关键词
          for (const field of nodealTableFields.value) {
            const fieldValue = item[field]
            if (fieldValue && fieldValue.toLowerCase().includes(keyword)) {
              return true
            }
          }
          // 也在时间字段中搜索
          const timeFields = ['first_receive_time', 'last_process_time']
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
      if (nodealSortField.value) {
        result = [...result].sort((a, b) => {
          const aVal = a[nodealSortField.value] || ''
          const bVal = b[nodealSortField.value] || ''

          let comparison = 0
          if (typeof aVal === 'string' && typeof bVal === 'string') {
            comparison = aVal.localeCompare(bVal)
          } else {
            comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
          }

          return nodealSortOrder.value === 'asc' ? comparison : -comparison
        })
      }

      return result
    })

    const lcoaPaginatedData = computed(() => {
      const start = (lcoaCurrentPage.value - 1) * lcoaPageSize.value
      const end = start + lcoaPageSize.value
      return (lcoaFilteredData.value || []).slice(start, end)
    })

    // nodeal分页计算属性（新增）
    const nodealPaginatedData = computed(() => {
      const start = (nodealCurrentPage.value - 1) * nodealPageSize.value
      const end = start + nodealPageSize.value
      return (nodealFilteredData.value || []).slice(start, end)
    })

    const lcoaDisplayedFrom = computed(() => {
      return (lcoaFilteredData.value || []).length > 0 ? (lcoaCurrentPage.value - 1) * lcoaPageSize.value + 1 : 0
    })

    // nodeal显示范围计算属性（新增）
    const nodealDisplayedFrom = computed(() => {
      return (nodealFilteredData.value || []).length > 0 ? (nodealCurrentPage.value - 1) * nodealPageSize.value + 1 : 0
    })

    const lcoaDisplayedTo = computed(() => {
      const end = lcoaCurrentPage.value * lcoaPageSize.value
      return end > (lcoaFilteredData.value || []).length ? (lcoaFilteredData.value || []).length : end
    })

    // nodeal显示范围计算属性（新增）
    const nodealDisplayedTo = computed(() => {
      const end = nodealCurrentPage.value * nodealPageSize.value
      return end > (nodealFilteredData.value || []).length ? (nodealFilteredData.value || []).length : end
    })

    const lcoaTotalPages = computed(() => {
      return Math.ceil((lcoaFilteredData.value || []).length / lcoaPageSize.value)
    })

    // nodeal总页数计算属性（新增）
    const nodealTotalPages = computed(() => {
      return Math.ceil((nodealFilteredData.value || []).length / nodealPageSize.value)
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

    // nodeal页面大小变化处理函数（新增）
    const handleNodealPageSizeChange = () => {
      nodealCurrentPage.value = 1
    }

    const refreshLcoaData = () => {
      fetchLcoaTableData()
    }

    // nodeal刷新数据函数（新增）
    const refreshNodealData = () => {
      fetchNodealTableData()
    }

    const performLcoaSearch = () => {
      lcoaCurrentPage.value = 1
    }

    // nodeal搜索函数（新增）
    const performNodealSearch = () => {
      nodealCurrentPage.value = 1
    }

    const sortLcoaTable = (field) => {
      if (lcoaSortField.value === field) {
        lcoaSortOrder.value = lcoaSortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        lcoaSortField.value = field
        lcoaSortOrder.value = 'asc'
      }
    }

    // nodeal排序函数（新增）
    const sortNodealTable = (field) => {
      if (nodealSortField.value === field) {
        nodealSortOrder.value = nodealSortOrder.value === 'asc' ? 'desc' : 'asc'
      } else {
        nodealSortField.value = field
        lcoaSortOrder.value = 'asc'
      }
    }

    const showLcoaDetail = (item) => {
      currentLcoaDetail.value = { ...item }
      showLcoaModal.value = true
    }

    // nodeal详情显示函数（新增）
    const showNodealDetail = (item) => {
      currentNodealDetail.value = { ...item }
      showNodealModal.value = true
    }

    const closeLcoaModal = () => {
      showLcoaModal.value = false
    }

    // nodeal关闭模态框函数（新增）
    const closeNodealModal = () => {
      showNodealModal.value = false
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

    // 补全缺失的函数定义
    const fetchLcoaTableData = async () => {
      lcoaLoading.value = true
      lcoaError.value = null
      try {
        const res = await lcoaAPI.getLcoaData()
        if (res.code === 200) {
          lcoaTableData.value = Array.isArray(res.data) ? res.data : []
        } else {
          throw new Error(res.message || '获取LCOA表格数据失败')
        }
      } catch (err) {
        lcoaError.value = err.response?.data?.message || err.message || '获取LCOA表格数据失败'
        lcoaTableData.value = []
      } finally {
        lcoaLoading.value = false
      }
    }

    // nodeal数据获取函数（新增）
    const fetchNodealTableData = async () => {
      nodealLoading.value = true
      nodealError.value = null
      try {
        const res = await lcoaAPI.getSysDealData() // 使用sys_deal接口获取nodeal数据
        if (res.code === 200) {
          nodealTableData.value = Array.isArray(res.data) ? res.data : []
        } else {
          throw new Error(res.message || '获取未处理流程表格数据失败')
        }
      } catch (err) {
        nodealError.value = err.response?.data?.message || err.message || '获取未处理流程表格数据失败'
        nodealTableData.value = []
      } finally {
        nodealLoading.value = false
      }
    }

    const fetchXiangxiLatestData = async () => {
      xiangxiLoading.value = true
      xiangxiError.value = null
      try {
        const res = await lcoaAPI.getSysXiangxiLatest()
        // 获取最新日期
        const dateRes = await lcoaAPI.getSysClubLatestDate()
        const xiangxiDateRes = await lcoaAPI.getSysXiangxiLatestDate()
        
        if (res.code === 200) {
          xiangxiData.value = Array.isArray(res.data) ? res.data : []
          nextTick(() => {
            startXiangxiScrolling()
          })
        } else {
          throw new Error(res.message || '获取数据失败')
        }
        
        // 更新日期信息
        if (dateRes.code === 200) {
          clubLatestDate.value = dateRes.data
        }
        
        // 如果sys_xiangxi有更新的日期，则使用它
        if (xiangxiDateRes.code === 200 && xiangxiDateRes.data) {
          xiangxiLatestDate.value = xiangxiDateRes.data.latest_date
        }
      } catch (err) {
        xiangxiError.value = err.response?.data?.message || err.message || '获取数据失败'
        xiangxiData.value = []
      } finally {
        xiangxiLoading.value = false
      }
    }

    // 获取xiangxi每日统计数据（新增）
    const fetchXiangxiDailyStats = async () => {
      xiangxiDailyStatsLoading.value = true
      xiangxiDailyStatsError.value = null
      try {
        const res = await lcoaAPI.getSysXiangxiDailyStats()
        
        if (res.code === 200) {
          xiangxiDailyStats.value = Array.isArray(res.data) ? res.data : []
        } else {
          throw new Error(res.message || '获取统计数据失败')
        }
      } catch (err) {
        xiangxiDailyStatsError.value = err.response?.data?.message || err.message || '获取统计数据失败'
        xiangxiDailyStats.value = []
      } finally {
        xiangxiDailyStatsLoading.value = false
      }
    }

    const fetchClubData = async () => {
      chartLoading.value = true
      error.value.club = null
      try {
        // 获取部门数据
        const res = await lcoaAPI.getSysClubLatest()
        // 获取最新日期
        const dateRes = await lcoaAPI.getSysClubLatestDate()
        
        if (res.code === 200) {
          clubData.value = res.data
          clubPieChartData.value = res.data
          await nextTick()
          drawClubPieChart() // 绘制部门人员分布图
        } else {
          throw new Error(res.message || '获取部门数据失败')
        }
        
        // 更新日期信息
        if (dateRes.code === 200) {
          clubLatestDate.value = dateRes.data
        }
      } catch (err) {
        error.value.club = err.response?.data?.message || err.message || '获取部门数据失败'
      } finally {
        chartLoading.value = false
      }
    }

    // 图表绘制函数
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

    // 绘制部门人员分布扇形图
    const drawClubPieChart = () => {
      if (!clubPieChartCanvas.value || clubPieChartData.value.length === 0) return

      if (clubPieChart) {
        clubPieChart.destroy()
      }

      const ctx = clubPieChartCanvas.value.getContext('2d')
      const labels = clubPieChartData.value.map(item => item.department)
      const data = clubPieChartData.value.map(item => parseInt(item.personnel_count) || 0)

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

      clubPieChart = new Chart(ctx, {
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

    // 绘制xiangxi每日统计数据图表（新增）
    const drawXiangxiStatsChart = () => {
      if (!xiangxiStatsChartCanvas.value || xiangxiDailyStats.value.length === 0) return

      if (xiangxiStatsChart) {
        xiangxiStatsChart.destroy()
      }

      const ctx = xiangxiStatsChartCanvas.value.getContext('2d')
      // 反转数据顺序，使最新的日期在右侧
      const reversedStats = [...xiangxiDailyStats.value].reverse()
      const labels = reversedStats.map(item => item.date)
      const data = reversedStats.map(item => item.count)

      xiangxiStatsChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: '数据量',
            data: data,
            backgroundColor: '#4BC0C0',
            borderColor: '#36A2EB',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: '数据量'
              }
            },
            x: {
              title: {
                display: true,
                text: '日期'
              }
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

    // 滚动相关函数
    const startXiangxiScrolling = () => {
      stopXiangxiScrolling()

      if (xiangxiData.value.length > 7) {
        xiangxiScrollInterval = setInterval(() => {
          isXiangxiScrolling.value = true
          const totalItems = xiangxiData.value.length
          const itemHeight = xiangxiItemHeight
          const maxOffset = -(totalItems * itemHeight) + (7 * itemHeight)

          let currentOffset = xiangxiScrollOffset.value
          const targetOffset = currentOffset - (7 * itemHeight)

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
        fetchSysDealCount()
        fetchClubData()
        generateBarChartData()
        fetchLcoaTableData() // 调用表格数据获取函数
        fetchNodealTableData() // 获取nodeal数据
        fetchXiangxiLatestData()
        fetchXiangxiDailyStats() // 获取xiangxi每日统计数据

        nextTick(() => {
          drawBarChart()
          drawClubPieChart()
        })
      } catch (error) {
        componentError.value = '组件初始化失败: ' + (error.message || '未知错误')
      }
    }

    const reloadComponent = () => {
      componentError.value = null
      initComponent()
    }

    onMounted(() => {
      initComponent()
    })

    onUnmounted(() => {
      stopXiangxiScrolling()
      // 销毁图表实例，避免内存泄漏
      if (barChart) barChart.destroy()
      if (clubPieChart) clubPieChart.destroy()
      if (xiangxiStatsChart) xiangxiStatsChart.destroy()
    })

    // 监听xiangxi每日统计数据变化，重新绘制图表
    watch(xiangxiDailyStats, () => {
      nextTick(() => {
        drawXiangxiStatsChart()
      })
    })

    return {
      componentError,
      lcoaTotal,
      sysDealTotal,
      clubData,
      barChartData,
      clubPieChartCanvas,
      clubPieChartData,
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
      shouldTruncate,
      lcoaDisplayedFrom,
      lcoaDisplayedTo,
      lcoaTotalPages,
      clubLatestDate,
      xiangxiLatestDate,
      
      // xiangxi每日统计数据相关返回值（新增）
      xiangxiDailyStats,
      xiangxiDailyStatsLoading,
      xiangxiDailyStatsError,
      xiangxiStatsChartCanvas,
      
      // nodeal相关返回值（新增）
      nodealData,
      nodealTableData,
      nodealLoading,
      nodealError,
      nodealSearchKeyword,
      nodealCurrentPage,
      nodealPageSize,
      nodealSortField,
      nodealSortOrder,
      nodealFilteredData,
      nodealPaginatedData,
      nodealTableHeaders,
      nodealTableFields,
      showNodealModal,
      currentNodealDetail,
      refreshNodealData,
      performNodealSearch,
      sortNodealTable,
      closeNodealModal,
      showNodealDetail,
      handleNodealPageSizeChange,
      nodealDisplayedFrom,
      nodealDisplayedTo,
      nodealTotalPages
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
  max-width: calc(100vw - 200px); /* 减去侧边栏宽度，与整体界面保持一致 */
  margin: 0 auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    max-width: calc(100vw - 70px); /* 移动端侧边栏宽度为70px */
    padding: 10px;
  }
}

.error-container {
  background: white;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.retry-btn {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background-color: #337ecc;
}

h1 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  justify-content: center;
}

.stat-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
  width: 100%;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
  width: 100%;
}

.stat-change {
  font-size: 14px;
  color: #999;
}

.stat-change.positive {
  color: #67c23a;
}

.stat-error {
  color: #f56c6c;
  font-size: 14px;
  margin-top: 10px;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.scroll-container {
  height: 280px;
  overflow: hidden;
  position: relative;
}

.scroll-header {
  display: flex;
  background: #f5f7fa;
  font-weight: bold;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.header-item {
  flex: 1;
  padding: 0 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scroll-content {
  height: 245px;
  overflow: hidden;
}

.scroll-item-wrapper {
  transition: transform 0.5s ease;
}

.scroll-item {
  display: flex;
  height: 35px;
  line-height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f0f0f0;
}

.scroll-item.even {
  background-color: #fafafa;
}

.item-cell {
  flex: 1;
  padding: 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}

.data-info {
  margin-top: 10px;
  text-align: right;
  color: #666;
  font-size: 14px;
}

.club-title {
  text-align: center;
  margin: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.xiangxi-title {
  text-align: center;
  margin: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.lcoa-data-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.data-actions {
  display: flex;
  justify-content: space-between;
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
  background-color: #67c23a;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn {
  background-color: #67c23a;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.error-message {
  color: #f56c6c;
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.loading-state {
  text-align: center;
  padding: 40px 0;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.data-table-container {
  overflow-x: auto;
  width: 100%;
}

.table-wrapper {
  max-height: 500px;
  overflow-y: auto;
  overflow-x: visible; /* 允许横向滚动以显示完整表头 */
  width: 100%;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
  min-width: 500px;
}

.data-table th,
.data-table td {
  padding: 12px 10px;
  text-align: left;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}

.data-table th {
  background-color: #f5f7fa;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 1;
  white-space: nowrap;
  overflow: visible;
}

.data-table td {
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: top;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.sortable-header:hover {
  background-color: #e1e6f0;
}

.sort-indicator {
  margin-left: 5px;
  font-size: 12px;
}

.id-column {
  width: 60px;
}

.time-column {
  width: 120px; /* 减少时间列宽度 */
}

.action-column {
  width: 70px; /* 减少操作列宽度 */
}

/* 其他列自动分配宽度 */
.data-table th:not(.id-column):not(.time-column):not(.action-column),
.data-table td:not(.id-column):not(.time-column):not(.action-column) {
  width: auto;
  min-width: 100px;
}

/* 最近七天数据统计标题居中 */
.chart-card h3 {
  text-align: center;
}

.truncated {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.detail-btn {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
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
}

.page-btn {
  background-color: #f4f4f5;
  color: #606266;
  border: 1px solid #dcdfe6;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.page-btn:disabled {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background-color: #409eff;
  color: white;
}

.page-info {
  color: #666;
  font-size: 14px;
  margin: 0 10px;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 14px;
}

.page-size-selector select {
  padding: 5px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.no-data {
  text-align: center;
  padding: 40px 0;
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
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
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
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .charts-container {
    grid-template-columns: 1fr;
  }

  .data-actions {
    flex-direction: column;
  }

  .search-box {
    width: 100%;
  }

  .action-buttons {
    width: 100%;
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