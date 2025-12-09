<template>
  <div class="project-progress">
    <!-- 标签页导航 -->
    <div class="tabs flex border-b">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-btn px-3 py-2 text-sm', { 'bg-blue-600 text-white': activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- 工作计划标签页的内容 -->
    <div v-show="activeTab === 'workplan'" class="workplan-content p-4">
      <h3 class="text-lg font-semibold mb-4">今日工作计划</h3>
      <div v-if="todayTasksLoading" class="text-center py-8 text-gray-500">
        加载中...
      </div>
      <div v-else-if="todayTasks.length > 0">
        <div v-for="(task, index) in todayTasks" :key="index" class="task-item mb-3 p-3 border rounded">
          <div class="task-header flex justify-between items-center">
            <span class="font-medium">{{ task.projectName }}</span>
            <span class="text-sm text-gray-600">{{ task.date }}</span>
          </div>
          <div class="task-details mt-2">
            <p><strong>节点：</strong>{{ task.milestone }}</p>
            <p><strong>部门：</strong>{{ task.department }}</p>
            <p><strong>负责人：</strong>{{ task.responsiblePerson }}</p>
          </div>
        </div>
      </div>
      <div v-else class="no-tasks text-center py-8 text-gray-500">
        今日无相关任务
      </div>
    </div>

    <!-- 项目顶部信息栏 -->
    <div v-show="activeTab !== 'workplan'" class="project-header bg-white border-b p-2 flex items-center text-sm">
      <span>当前项目：</span>
      <div class="selected-projects ml-2">
        <span v-if="selectedProjects.length === 0">未选择项目</span>
        <span v-for="project in selectedProjects" :key="project.id" class="project-tag">
          {{ project.project_name }}
          <button @click="removeProject(project.id)" class="remove-btn">×</button>
        </span>
      </div>
      <div class="ml-auto flex items-center">
        <button class="px-2 py-1 border text-xs mr-2" @click="selectAllProjects">全选</button>
        <select v-model="selectedProjectId" @change="addProject" class="border rounded px-2 py-1 text-sm mr-2">
          <option value="">添加项目</option>
          <option v-for="project in availableProjects" :key="project.id" :value="project.id">
            {{ project.project_name }}
          </option>
        </select>
        <button class="px-2 py-1 border text-xs" @click="clearAllProjects">清空</button>
      </div>
    </div>

    <!-- 甘特图控制栏 -->
    <div v-show="activeTab !== 'workplan'" class="gantt-controls p-2 bg-gray-50 flex items-center text-sm">
      <span>日历维度：</span>
      <label class="ml-2">
        <input type="radio" name="scale" value="day" v-model="timeScale" @change="setTimeScale"> 日
      </label>
      <label class="ml-2">
        <input type="radio" name="scale" value="week" v-model="timeScale" @change="setTimeScale" checked> 周
      </label>
      <label class="ml-2">
        <input type="radio" name="scale" value="month" v-model="timeScale" @change="setTimeScale"> 月
      </label>
      <label class="ml-2">
        <input type="radio" name="scale" value="quarter" v-model="timeScale" @change="setTimeScale"> 季
      </label>
      <label class="ml-2">
        <input type="radio" name="scale" value="year" v-model="timeScale" @change="setTimeScale"> 年
      </label>
      <button class="ml-4 px-2 py-1 border text-xs">图例</button>
      <button class="ml-2 px-2 py-1 border text-xs" @click="refreshData">刷新</button>
      <div class="ml-auto flex items-center">
        <button class="px-2 py-1 border text-xs mr-1" @click="zoomIn">+</button>
        <button class="px-2 py-1 border text-xs" @click="zoomOut">-</button>
      </div>
    </div>

    <!-- 甘特图主体容器 -->
    <div v-show="activeTab === 'gantt'" ref="ganttRef" class="gantt-container h-[600px] w-full border mt-2"></div>
    
    <!-- 导入导出标签页的内容 -->
    <div v-show="activeTab === 'import'" class="import-export-content p-4">
      <h3 class="text-lg font-semibold mb-4">数据导入导出</h3>
      
      <!-- 导入部分 -->
      <div class="import-section mb-8">
        <h4 class="font-medium mb-2">数据导入</h4>
        <div class="border rounded p-4 mb-4">
          <div class="mb-3">
            <label class="block text-sm font-medium mb-1">选择Excel文件</label>
            <input 
              type="file" 
              ref="fileInput"
              accept=".xlsx,.xls"
              @change="handleFileSelect"
              class="border rounded px-3 py-2 w-full"
            />
          </div>
          <div class="flex items-center">
            <button 
              @click="importProjectsFromExcel" 
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded flex items-center"
              :disabled="importing || !selectedFile"
            >
              <span v-if="importing">导入中...</span>
              <span v-else>导入项目数据</span>
            </button>
            <button 
              @click="downloadTemplate" 
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center ml-2"
            >
              下载模板
            </button>
            <div v-if="selectedFile" class="ml-3 text-sm text-gray-600">
              已选择: {{ selectedFile.name }}
            </div>
          </div>
        </div>
        
        <div v-if="importResult" class="mt-4 p-3 rounded border" :class="{
          'bg-green-50 border-green-200 text-green-800': importResult.success,
          'bg-red-50 border-red-200 text-red-800': !importResult.success
        }">
          <h5 class="font-medium mb-1">{{ importResult.success ? '导入成功' : '导入失败' }}</h5>
          <p>{{ importResult.message }}</p>
          <div v-if="importResult.data">
            <p v-if="importResult.data.imported_projects">成功导入 {{ importResult.data.imported_projects.length }} 个项目</p>
            <p v-if="importResult.data.failed_projects">失败 {{ importResult.data.failed_projects.length }} 个项目</p>
          </div>
        </div>
      </div>

      <!-- 导出部分 -->
      <div class="export-section mb-6">
        <h4 class="font-medium mb-2">数据导出</h4>
        <div class="flex items-center mb-4">
          <input 
            type="text" 
            v-model="exportFileName" 
            placeholder="请输入导出文件名" 
            class="border rounded px-3 py-2 mr-2 flex-grow"
          />
          <button 
            @click="exportToExcel" 
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center"
            :disabled="exporting"
          >
            <span v-if="exporting">导出中...</span>
            <span v-else>导出Excel</span>
          </button>
        </div>
        <div class="text-sm text-gray-600 mb-2">
          <p>导出格式说明：</p>
          <ul class="list-disc pl-5 mt-1">
            <li>Excel文档包含序号、项目名称、产品名称、产品示意图等基本信息</li>
            <li>如果项目有多个关键里程碑节点，则同一项目的基本信息会重复显示</li>
            <li>每个项目还会显示关键里程碑节点、责任部门、计划开始时间、预计完成时间等详细信息</li>
          </ul>
        </div>
      </div>
      
      <div class="preview-section">
        <h4 class="font-medium mb-2">数据预览</h4>
        <div v-if="exportData.length > 0" class="overflow-x-auto">
          <table class="min-w-full bg-white border">
            <thead>
              <tr class="bg-gray-100">
                <th class="border px-4 py-2 text-left">序号</th>
                <th class="border px-4 py-2 text-left">项目名称</th>
                <th class="border px-4 py-2 text-left">产品名称</th>
                <th class="border px-4 py-2 text-left">产品示意图</th>
                <th class="border px-4 py-2 text-left">客户名称及订单情况</th>
                <th class="border px-4 py-2 text-left">关键里程碑节点</th>
                <th class="border px-4 py-2 text-left">责任部门</th>
                <th class="border px-4 py-2 text-left">计划开始时间</th>
                <th class="border px-4 py-2 text-left">预计完成时间</th>
                <th class="border px-4 py-2 text-left">实际完成时间</th>
                <th class="border px-4 py-2 text-left">负责人</th>
                <th class="border px-4 py-2 text-left">异常类别</th>
                <th class="border px-4 py-2 text-left">影响周期</th>
                <th class="border px-4 py-2 text-left">应对措施</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in exportData.slice(0, 10)" :key="index">
                <td class="border px-4 py-2">{{ item.index }}</td>
                <td class="border px-4 py-2">{{ item.projectName }}</td>
                <td class="border px-4 py-2">{{ item.productName }}</td>
                <td class="border px-4 py-2">
                  <div v-if="item.productImageUrl" class="flex items-center">
                    <img 
                      v-if="isImage(item.productImageUrl)" 
                      :src="item.productImageUrl" 
                      alt="产品示意图" 
                      class="w-16 h-16 object-contain cursor-pointer"
                      @click="openImagePreview(item.productImageUrl)"
                    />
                    <div 
                      v-else-if="isPdf(item.productImageUrl)"
                      class="w-16 h-16 flex items-center justify-center bg-red-100 rounded cursor-pointer"
                      @click="openPdfPreview(item.productImageUrl)"
                    >
                      <span class="text-red-600 font-bold">PDF</span>
                    </div>
                    <span v-else class="text-blue-600 underline cursor-pointer" @click="openFile(item.productImageUrl)">
                      查看文件
                    </span>
                  </div>
                  <span v-else>无文件</span>
                </td>
                <td class="border px-4 py-2">{{ item.customerInfo }}</td>
                <td class="border px-4 py-2">{{ item.milestone }}</td>
                <td class="border px-4 py-2">{{ item.department }}</td>
                <td class="border px-4 py-2">{{ item.plannedStartTime }}</td>
                <td class="border px-4 py-2">{{ item.plannedEndTime }}</td>
                <td class="border px-4 py-2">{{ item.actualCompletionTime }}</td>
                <td class="border px-4 py-2">{{ item.responsiblePerson }}</td>
                <td class="border px-4 py-2">{{ item.exceptionType }}</td>
                <td class="border px-4 py-2">{{ item.impactCycle }}</td>
                <td class="border px-4 py-2">{{ item.responseMeasures }}</td>
              </tr>
              <tr v-if="exportData.length > 10">
                <td class="border px-4 py-2 text-center" colspan="14">还有 {{ exportData.length - 10 }} 条数据未显示</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          暂无数据可导出
        </div>
      </div>
    </div>
    
    <!-- 其他标签页的内容 -->
    <div v-show="activeTab !== 'gantt' && activeTab !== 'workplan' && activeTab !== 'import'" class="tab-content p-4">
      <div v-if="activeTab === 'tasklink'">
        <h3>任务关联</h3>
        <p>这里是任务关联内容</p>
      </div>
      
      <div v-if="activeTab === 'track'">
        <h3>计划跟踪</h3>
        <p>这里是计划跟踪内容</p>
      </div>
      
      <div v-if="activeTab === 'feedback'">
        <h3>进展反馈</h3>
        <p>这里是进展反馈内容</p>
      </div>
      
      <div v-if="activeTab === 'document'">
        <h3>交付文档</h3>
        <p>这里是交付文档内容</p>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div v-if="showImagePreview" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click="closeImagePreview">
      <div class="max-w-4xl max-h-full p-4" @click.stop>
        <img :src="imagePreviewUrl" alt="预览图片" class="max-w-full max-h-full object-contain">
        <button @click="closeImagePreview" class="absolute top-4 right-4 text-white text-2xl">&times;</button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">加载中...</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import * as d3 from 'd3'
import * as XLSX from 'xlsx'

export default {
  name: 'ProjectProgress',
  data() {
    return {
      projects: [],
      selectedProjectId: '',
      selectedProjects: [],
      loading: false,
      todayTasksLoading: false,
      activeTab: 'gantt',
      timeScale: 'week', // 默认选中周
      tabs: [
        { id: 'workplan', name: '工作计划' },
        { id: 'tasklink', name: '任务关联' },
        { id: 'gantt', name: '甘特图' },
        { id: 'track', name: '计划跟踪' },
        { id: 'feedback', name: '进展反馈' },
        { id: 'document', name: '交付文档' },
        { id: 'import', name: '导入导出' }
      ],
      ganttSvg: null,
      allProjects: [], // 存储所有项目数据，用于工作计划标签页
      exportFileName: '项目数据导出',
      exporting: false,
      importing: false,
      selectedFile: null,
      importResult: null,
      imagePreviewUrl: '',
      showImagePreview: false,
      pdfPreviewUrl: '',
      showPdfPreview: false
    }
  },
  computed: {
    availableProjects() {
      // 返回未被选择的项目
      return this.projects.filter(project => 
        !this.selectedProjects.some(selected => selected.id === project.id)
      )
    },
    todayTasks() {
      // 获取今天相关的任务
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const tasks = [];
      
      this.allProjects.forEach(project => {
        if (project.milestones && project.milestones.length > 0) {
          project.milestones.forEach(milestone => {
            // 检查计划开始时间是否为今天
            if (milestone.planned_start_time) {
              const startDate = new Date(milestone.planned_start_time);
              startDate.setHours(0, 0, 0, 0);
              if (startDate.getTime() === today.getTime()) {
                tasks.push({
                  projectName: project.project_name,
                  milestone: milestone.milestone,
                  department: milestone.responsible_department || '未指定',
                  responsiblePerson: milestone.responsible_person || '未指定',
                  date: '计划开始'
                });
              }
            }
            
            // 检查计划结束时间是否为今天
            if (milestone.planned_end_time) {
              const endDate = new Date(milestone.planned_end_time);
              endDate.setHours(0, 0, 0, 0);
              if (endDate.getTime() === today.getTime()) {
                tasks.push({
                  projectName: project.project_name,
                  milestone: milestone.milestone,
                  department: milestone.responsible_department || '未指定',
                  responsiblePerson: milestone.responsible_person || '未指定',
                  date: '计划结束'
                });
              }
            }
            
            // 检查实际完成时间是否为今天
            if (milestone.actual_completion_time) {
              const actualDate = new Date(milestone.actual_completion_time);
              actualDate.setHours(0, 0, 0, 0);
              if (actualDate.getTime() === today.getTime()) {
                tasks.push({
                  projectName: project.project_name,
                  milestone: milestone.milestone,
                  department: milestone.responsible_department || '未指定',
                  responsiblePerson: milestone.responsible_person || '未指定',
                  date: '实际完成'
                });
              }
            }
            
            // 检查今天是否在计划时间范围内（今天在节点要求完成的时间段中）
            if (milestone.planned_start_time && milestone.planned_end_time) {
              const startDate = new Date(milestone.planned_start_time);
              const endDate = new Date(milestone.planned_end_time);
              startDate.setHours(0, 0, 0, 0);
              endDate.setHours(0, 0, 0, 0);
              
              // 如果今天在计划时间段内，且不是开始或结束日期（避免重复）
              if (today > startDate && today < endDate) {
                tasks.push({
                  projectName: project.project_name,
                  milestone: milestone.milestone,
                  department: milestone.responsible_department || '未指定',
                  responsiblePerson: milestone.responsible_person || '未指定',
                  date: '进行中'
                });
              }
            }
          });
        }
      });
      
      return tasks;
    },
    exportData() {
      const data = [];
      let index = 1;
      
      // 筛选出选中的项目，如果没有选中任何项目，则显示所有项目
      let projectsToExport = this.allProjects;
      if (this.selectedProjects.length > 0) {
        const selectedProjectIds = this.selectedProjects.map(p => p.id);
        projectsToExport = this.allProjects.filter(project => 
          selectedProjectIds.includes(project.id)
        );
      }
      
      projectsToExport.forEach(project => {
        if (project.milestones && project.milestones.length > 0) {
          project.milestones.forEach(milestone => {
            data.push({
              index: index++,
              projectName: project.project_name,
              productName: project.product_name,
              productImageUrl: project.product_image || '', // 产品图片URL
              customerInfo: `${project.customer_name || ''} (${project.order_status || ''})`, // 客户名称及订单情况
              milestone: milestone.milestone,
              department: milestone.responsible_department || '',
              plannedStartTime: milestone.planned_start_time || '',
              plannedEndTime: milestone.planned_end_time || '',
              actualCompletionTime: milestone.actual_completion_time || '',
              responsiblePerson: milestone.responsible_person || '',
              exceptionType: milestone.exception_type || '',
              impactCycle: milestone.impact_cycle || '',
              responseMeasures: milestone.response_measures || ''
            });
          });
        } else {
          // 如果项目没有里程碑，也导出项目基本信息
          data.push({
            index: index++,
            projectName: project.project_name,
            productName: project.product_name,
            productImageUrl: project.product_image || '',
            customerInfo: `${project.customer_name || ''} (${project.order_status || ''})`,
            milestone: '',
            department: '',
            plannedStartTime: '',
            plannedEndTime: '',
            actualCompletionTime: '',
            responsiblePerson: '',
            exceptionType: '',
            impactCycle: '',
            responseMeasures: ''
          });
        }
      });
      
      return data;
    }
  },
  methods: {
    async fetchProjectData() {
      this.loading = true
      try {
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          this.projects = response.data.data
          // 数据更新后重新渲染甘特图
          if (this.activeTab === 'gantt') {
            this.$nextTick(() => {
              this.renderGanttChart()
            })
          }
        }
      } catch (err) {
        console.error('获取项目数据时出错:', err)
      } finally {
        this.loading = false
      }
    },
    
    async fetchAllProjectData() {
      this.todayTasksLoading = true
      try {
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          this.allProjects = response.data.data
          // 数据更新后重新渲染甘特图
          if (this.activeTab === 'gantt') {
            this.$nextTick(() => {
              this.renderGanttChart()
            })
          }
        }
      } catch (err) {
        console.error('获取所有项目数据时出错:', err)
      } finally {
        this.todayTasksLoading = false
      }
    },
    
    addProject() {
      if (this.selectedProjectId) {
        const project = this.projects.find(p => p.id == this.selectedProjectId)
        if (project && !this.selectedProjects.some(p => p.id === project.id)) {
          this.selectedProjects.push(project)
        }
        this.selectedProjectId = ''
      }
    },
    
    removeProject(projectId) {
      this.selectedProjects = this.selectedProjects.filter(p => p.id !== projectId)
    },
    
    clearAllProjects() {
      this.selectedProjects = []
    },
    
    selectAllProjects() {
      // 选择所有项目
      this.selectedProjects = [...this.projects]
    },
    
    setTimeScale() {
      // 时间尺度变化时重新渲染甘特图
      this.renderGanttChart()
    },
    
    refreshData() {
      // 刷新数据
      this.fetchProjectData()
      this.fetchAllProjectData()
      this.renderGanttChart()
    },
    
    zoomIn() {
      // 放大功能可以以后实现
      console.log('放大甘特图')
    },
    
    zoomOut() {
      // 缩小功能可以以后实现
      console.log('缩小甘特图')
    },
    
    // 添加甘特图渲染方法
    renderGanttChart() {
      // 清空之前的甘特图
      const ganttContainer = this.$refs.ganttRef
      if (!ganttContainer) return
      
      // 清空容器
      ganttContainer.innerHTML = ''
      
      // 只在甘特图标签页显示时渲染
      if (this.activeTab !== 'gantt') return
      
      // 检查是否有选中的项目
      if (!this.selectedProjects || this.selectedProjects.length === 0) {
        ganttContainer.innerHTML = '<div class="no-data">请选择要显示的项目</div>'
        return
      }
      
      // 收集所有任务数据
      const tasks = []
      const projectColors = d3.scaleOrdinal(d3.schemeCategory10)
      
      this.selectedProjects.forEach((project, projectIndex) => {
        if (project.milestones && project.milestones.length > 0) {
          project.milestones.forEach((milestone, milestoneIndex) => {
            // 解析日期
            let startDate = null
            let endDate = null
            
            if (milestone.planned_start_time) {
              startDate = new Date(milestone.planned_start_time)
            }
            
            if (milestone.planned_end_time) {
              endDate = new Date(milestone.planned_end_time)
            }
            
            // 只有开始和结束时间都存在时才添加任务
            if (startDate && endDate) {
              tasks.push({
                projectName: project.project_name,
                taskId: `${project.id}-${milestoneIndex}`,
                taskName: milestone.milestone,
                startDate: startDate,
                endDate: endDate,
                color: projectColors(projectIndex),
                actualCompletionTime: milestone.actual_completion_time ? new Date(milestone.actual_completion_time) : null
              })
            }
          })
        }
      })
      
      // 如果没有任务数据
      if (tasks.length === 0) {
        ganttContainer.innerHTML = '<div class="no-data">所选项目没有可用的里程碑数据</div>'
        return
      }
      
      // 设置甘特图尺寸
      const width = ganttContainer.clientWidth
      // 根据任务数量动态计算高度，每个任务占用40像素的高度
      const height = Math.max(600, tasks.length * 40 + 100) // 最小高度600px，根据任务数增加高度
      
      // 创建SVG元素
      const svg = d3.select(ganttContainer)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
      
      // 设置边距
      const margin = { top: 50, right: 20, bottom: 50, left: 150 }
      const chartWidth = width - margin.left - margin.right
      const chartHeight = height - margin.top - margin.bottom
      
      // 创建图表组
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
      
      // 计算时间范围
      const minDate = d3.min(tasks, d => d.startDate)
      const maxDate = d3.max(tasks, d => d.endDate)
      
      // 添加一些边距到时间范围
      const timeMargin = (maxDate - minDate) * 0.05
      const startDate = new Date(minDate.getTime() - timeMargin)
      const endDate = new Date(maxDate.getTime() + timeMargin)
      
      // 创建比例尺
      const xScale = d3.scaleTime()
        .domain([startDate, endDate])
        .range([0, chartWidth])
      
      const yScale = d3.scaleBand()
        .domain(tasks.map((d, i) => i))
        .range([0, chartHeight])
        .padding(0.2)
      
      // 添加X轴
      const xAxis = d3.axisBottom(xScale)
        .tickFormat(d3.timeFormat('%Y-%m-%d'))
        .ticks(Math.min(10, Math.floor(chartWidth / 100))) // 根据图表宽度调整刻度数量
      
      g.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${chartHeight})`)
        .call(xAxis)
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end')
        .style('font-size', '12px')
      
      // 添加Y轴（任务名称）
      tasks.forEach((task, i) => {
        g.append('text')
          .attr('x', -10)
          .attr('y', yScale(i) + yScale.bandwidth() / 2)
          .attr('dy', '0.35em')
          .attr('text-anchor', 'end')
          .text(`${task.projectName} - ${task.taskName}`)
          .attr('class', 'task-label')
      })
      
      // 绘制任务条
      const taskBars = g.selectAll('.task-bar')
        .data(tasks)
        .enter()
        .append('g')
        .attr('class', 'task-bar')
      
      // 计划任务条
      taskBars.append('rect')
        .attr('x', d => xScale(d.startDate))
        .attr('y', (d, i) => yScale(i) + yScale.bandwidth() * 0.2)
        .attr('width', d => xScale(d.endDate) - xScale(d.startDate))
        .attr('height', yScale.bandwidth() * 0.6)
        .attr('fill', d => d.color)
        .attr('rx', 3)
        .attr('ry', 3)
      
      // 实际完成进度条
      taskBars.append('rect')
        .attr('x', d => xScale(d.startDate))
        .attr('y', (d, i) => yScale(i) + yScale.bandwidth() * 0.3)
        .attr('width', d => {
          if (d.actualCompletionTime && d.actualCompletionTime <= d.endDate) {
            return xScale(d.actualCompletionTime) - xScale(d.startDate)
          }
          return 0
        })
        .attr('height', yScale.bandwidth() * 0.4)
        .attr('fill', 'rgba(255, 255, 255, 0.7)')
      
      // 添加今天线
      const today = new Date()
      if (today >= startDate && today <= endDate) {
        g.append('line')
          .attr('x1', xScale(today))
          .attr('x2', xScale(today))
          .attr('y1', 0)
          .attr('y2', chartHeight)
          .attr('class', 'today-line')
          .attr('stroke', '#ff0000')
          .attr('stroke-width', 2)
          .attr('stroke-dasharray', '5,5')
      }
      
      // 添加标题
      svg.append('text')
        .attr('x', width / 2)
        .attr('y', 20)
        .attr('text-anchor', 'middle')
        .attr('class', 'chart-title')
        .text('项目甘特图')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
    },
    
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },
    
    async importProjectsFromExcel() {
      if (!this.selectedFile) {
        alert('请先选择一个Excel文件');
        return;
      }
      
      this.importing = true;
      this.importResult = null;
      
      try {
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        
        const response = await axios.post('/api/import_projects', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        this.importResult = response.data;
        console.log('导入结果:', response.data);
        
        // 导入成功后刷新项目数据
        if (response.data.code === 200) {
          await this.fetchProjectData();
          await this.fetchAllProjectData();
          // 清空文件选择
          this.selectedFile = null;
          this.$refs.fileInput.value = '';
        }
      } catch (error) {
        console.error('导入失败:', error);
        this.importResult = {
          success: false,
          message: error.response?.data?.message || '导入失败，请查看控制台了解详情'
        };
      } finally {
        this.importing = false;
      }
    },
    
    downloadTemplate() {
      // 创建一个工作簿
      const wb = XLSX.utils.book_new();
      
      // 创建项目信息工作表数据
      const projectData = [
        ['项目名称', '产品名称', 'Unnamed: 2', '客户名称及订单情况', 'Unnamed: 4']
      ];
      
      // 创建项目信息工作表
      const projectWs = XLSX.utils.aoa_to_sheet(projectData);
      XLSX.utils.book_append_sheet(wb, projectWs, '项目信息');
      
      // 创建里程碑工作表数据
      const milestoneData = [
        ['项目名称', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', '关键里程碑节点', '责任部门', '计划开始时间', '计划结束时间', '实际完成时间', '负责人', '异常类别', '影响周期（天）', '应对措施']
      ];
      
      // 创建里程碑工作表
      const milestoneWs = XLSX.utils.aoa_to_sheet(milestoneData);
      XLSX.utils.book_append_sheet(wb, milestoneWs, '里程碑信息');
      
      // 导出文件
      XLSX.writeFile(wb, '项目数据导入模板.xlsx');
    },
    
    isImage(url) {
      if (!url) return false;
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
      return imageExtensions.some(ext => url.toLowerCase().endsWith(ext));
    },
    
    isPdf(url) {
      if (!url) return false;
      return url.toLowerCase().endsWith('.pdf');
    },
    
    openImagePreview(url) {
      this.imagePreviewUrl = url;
      this.showImagePreview = true;
    },
    
    closeImagePreview() {
      this.showImagePreview = false;
      this.imagePreviewUrl = '';
    },
    
    openPdfPreview(url) {
      window.open(url, '_blank');
    },
    
    openFile(url) {
      window.open(url, '_blank');
    },
    
    // 在组件挂载时初始化甘特图
    initializeGanttChart() {
      this.$nextTick(() => {
        this.renderGanttChart()
      })
    }
  },
  
  watch: {
    // 监听选中项目变化
    selectedProjects: {
      handler() {
        this.$nextTick(() => {
          this.renderGanttChart()
        })
      },
      deep: true
    },
    
    // 监听活动标签页变化
    activeTab: {
      handler(newTab) {
        // 当切换到工作计划标签页时，确保数据是最新的
        if (newTab === 'workplan') {
          this.fetchAllProjectData()
        }
        // 当切换到导入导出标签页时，确保数据是最新的
        if (newTab === 'import') {
          this.fetchAllProjectData()
        }
        // 当切换到甘特图标签页时，渲染甘特图
        if (newTab === 'gantt') {
          this.$nextTick(() => {
            this.renderGanttChart()
          })
        }
      }
    }
  },
  
  mounted() {
    this.fetchProjectData()
    // 在组件挂载时获取所有项目数据用于工作计划
    this.fetchAllProjectData()
    // 初始化甘特图
    this.initializeGanttChart()
  }
}
</script>

<style scoped>
.project-progress {
  padding: 0;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  overflow: hidden; /* 防止整个组件出现双重滚动条 */
}

.project-header {
  font-size: 0.875rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0.5rem;
  display: flex;
  align-items: center;
}

.selected-projects {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.project-tag {
  background-color: #e1f0fa;
  border: 1px solid #b8d4e6;
  border-radius: 0.25rem;
  padding: 0.125rem 0.5rem;
  display: flex;
  align-items: center;
  font-size: 0.75rem;
}

.remove-btn {
  background: none;
  border: none;
  color: #666;
  margin-left: 0.25rem;
  cursor: pointer;
  font-weight: bold;
}

.remove-btn:hover {
  color: #f44336;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}

.tab-btn {
  cursor: pointer;
  border: none;
  background: transparent;
  transition: background-color 0.2s;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.tab-btn:hover {
  background-color: #f3f4f6;
}

.tab-btn.bg-blue-600 {
  background-color: #2563eb;
  color: white;
}

.gantt-controls {
  font-size: 0.875rem;
  background-color: #f9fafb;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
}

.gantt-container {
  flex: 1;
  width: 100%;
  overflow: auto;
  position: relative;
  border: 1px solid #ddd;
  background-color: #fafafa;
  min-height: 600px;
}

.workplan-content,
.import-export-content {
  flex: 1;
  overflow-y: auto;
}

.task-item {
  background-color: #f8f9fa;
  border-color: #e9ecef;
}

.task-header {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.5rem;
}

.h-\[600px\] {
  height: auto;
  min-height: 600px;
}

.w-full {
  width: 100%;
}

.border {
  border: 1px solid #e5e7eb;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-1 {
  margin-top: 0.25rem;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
}

.ml-auto {
  margin-left: auto;
}

.ml-2 {
  margin-left: 0.5rem;
}

.ml-4 {
  margin-left: 1rem;
}

.mr-1 {
  margin-right: 0.25rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.px-2 {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.p-3 {
  padding: 0.75rem;
}

.p-4 {
  padding: 1rem;
}

.text-xs {
  font-size: 0.75rem;
}

.text-sm {
  font-size: 0.875rem;
}

.text-lg {
  font-size: 1.125rem;
}

.font-semibold {
  font-weight: 600;
}

.font-medium {
  font-weight: 500;
}

.rounded {
  border-radius: 0.25rem;
}

.flex {
  display: flex;
}

.flex-grow {
  flex-grow: 1;
}

.items-center {
  align-items: center;
}

.text-gray-500 {
  color: #9ca3af;
}

.text-gray-600 {
  color: #6b7280;
}

.bg-gray-100 {
  background-color: #f3f4f6;
}

.list-disc {
  list-style-type: disc;
}

.pl-5 {
  padding-left: 1.25rem;
}

.overflow-x-auto {
  overflow-x: auto;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.no-tasks {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-style: italic;
}

.text-center {
  text-align: center;
}

/* 甘特图样式 */
.no-data {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-style: italic;
  text-align: center;
}

.gantt-container svg {
  display: block;
  width: 100%;
  height: 100%;
}

.x-axis path,
.x-axis line {
  stroke: #999;
}

.task-label {
  font-family: sans-serif;
  font-size: 12px;
  cursor: pointer;
}

.grid-line {
  shape-rendering: crispEdges;
}

.task-bar rect {
  stroke: #333;
  stroke-width: 0.5;
}

.today-line {
  stroke: #FF5722;
  stroke-width: 2;
  stroke-dasharray: 5,5;
}

.chart-title {
  font-family: sans-serif;
}

/* 确保容器有合适的高度 */
.project-progress {
  padding: 0;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>