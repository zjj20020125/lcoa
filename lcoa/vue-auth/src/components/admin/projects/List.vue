<template>
  <div class="project-list">
    <h2>📂 项目列表</h2>
    <div class="toolbar">
      <button class="btn btn-primary" @click="showAddForm">新增项目</button>
      <button class="btn btn-secondary" @click="showImportExportSection">导入导出</button>
      <button class="btn btn-secondary" @click="toggleSelectAll">{{ selectAll ? '取消全选' : '全选' }}</button>
      <button class="btn btn-danger" @click="confirmDeleteSelected" :disabled="selectedProjects.length === 0">删除选中</button>
      <input 
        type="file" 
        ref="fileInput" 
        accept=".xlsx,.xls,.csv" 
        @change="handleFileImport" 
        style="display: none;"
      />
    </div>
    
    <!-- 导入导出部分 -->
    <div v-if="showImportExport" class="import-export-section mb-4 p-4 border rounded">
      <h3 class="text-lg font-semibold mb-3">数据导入导出</h3>
      
      <!-- 导入部分 -->
      <div class="import-section mb-4">
        <h4 class="font-medium mb-2">数据导入</h4>
        <div class="border rounded p-3 mb-3">
          <div class="mb-2">
            <label class="block text-sm font-medium mb-1">选择Excel文件</label>
            <input 
              type="file" 
              ref="importFileInput"
              accept=".xlsx,.xls"
              @change="handleImportFileSelect"
              class="border rounded px-2 py-1 w-full"
            />
          </div>
          <div class="flex items-center">
            <button 
              @click="importProjectsFromExcel" 
              class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm flex items-center"
              :disabled="importing || !selectedImportFile"
            >
              <span v-if="importing">导入中...</span>
              <span v-else>导入项目数据</span>
            </button>
            <button 
              @click="downloadTemplate" 
              class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm flex items-center ml-2"
            >
              下载模板
            </button>
            <div v-if="selectedImportFile" class="ml-3 text-sm text-gray-600">
              已选择: {{ selectedImportFile.name }}
            </div>
          </div>
        </div>
        
        <div class="import-notes mb-3 p-3 bg-blue-50 border border-blue-200 rounded">
          <h5 class="font-medium text-blue-800 mb-2">导入说明：</h5>
          <ul class="list-disc pl-5 text-sm text-blue-700 space-y-1">
            <li>系统会自动对同一项目下的多个里程碑节点按时间顺序进行编号</li>
            <li>较小编号的里程碑计划结束时间应早于或等于较大编号的计划开始时间</li>
            <li>系统将自动验证时间节点的逻辑一致性</li>
          </ul>
        </div>
        
        <div v-if="importResult" class="mt-3 p-2 rounded border text-sm" :class="{
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
      <div class="export-section mb-4">
        <h4 class="font-medium mb-2">数据导出</h4>
        <div class="flex items-center mb-3">
          <input 
            type="text" 
            v-model="exportFileName" 
            placeholder="请输入导出文件名" 
            class="border rounded px-2 py-1 mr-2 flex-grow text-sm"
          />
          <button 
            @click="exportToExcel" 
            class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm flex items-center"
            :disabled="exporting"
          >
            <span v-if="exporting">导出中...</span>
            <span v-else>导出Excel</span>
          </button>
        </div>
        <div class="text-xs text-gray-600 mb-2">
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
          <table class="min-w-full bg-white border text-sm">
            <thead>
              <tr class="bg-gray-100">
                <th class="border px-2 py-1 text-left">序号</th>
                <th class="border px-2 py-1 text-left">项目名称</th>
                <th class="border px-2 py-1 text-left">产品名称</th>
                <th class="border px-2 py-1 text-left">产品示意图</th>
                <th class="border px-2 py-1 text-left">客户名称及订单情况</th>
                <th class="border px-2 py-1 text-left">关键里程碑节点</th>
                <th class="border px-2 py-1 text-left">责任部门</th>
                <th class="border px-2 py-1 text-left">计划开始时间</th>
                <th class="border px-2 py-1 text-left">预计完成时间</th>
                <th class="border px-2 py-1 text-left">实际完成时间</th>
                <th class="border px-2 py-1 text-left">负责人</th>
                <th class="border px-2 py-1 text-left">异常类别</th>
                <th class="border px-2 py-1 text-left">影响周期</th>
                <th class="border px-2 py-1 text-left">应对措施</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in exportData.slice(0, 5)" :key="index">
                <td class="border px-2 py-1">{{ item.index }}</td>
                <td class="border px-2 py-1">{{ item.projectName }}</td>
                <td class="border px-2 py-1">{{ item.productName }}</td>
                <td class="border px-2 py-1">
                  <div v-if="item.productImageUrl" class="flex items-center">
                    <img 
                      v-if="isImage(item.productImageUrl)" 
                      :src="item.productImageUrl" 
                      alt="产品示意图" 
                      class="w-8 h-8 object-contain cursor-pointer"
                      @click="openImagePreview(item.productImageUrl)"
                    />
                    <div 
                      v-else-if="isPdf(item.productImageUrl)"
                      class="w-8 h-8 flex items-center justify-center bg-red-100 rounded cursor-pointer"
                      @click="openPdfPreview(item.productImageUrl)"
                    >
                      <span class="text-red-600 font-bold text-xs">PDF</span>
                    </div>
                    <span v-else class="text-blue-600 underline cursor-pointer text-xs" @click="openFile(item.productImageUrl)">
                      查看文件
                    </span>
                  </div>
                  <span v-else>无文件</span>
                </td>
                <td class="border px-2 py-1">{{ item.customerInfo }}</td>
                <td class="border px-2 py-1">{{ item.milestone }}</td>
                <td class="border px-2 py-1">{{ item.department }}</td>
                <td class="border px-2 py-1">{{ item.plannedStartTime }}</td>
                <td class="border px-2 py-1">{{ item.plannedEndTime }}</td>
                <td class="border px-2 py-1">{{ item.actualCompletionTime }}</td>
                <td class="border px-2 py-1">{{ item.responsiblePerson }}</td>
                <td class="border px-2 py-1">{{ item.exceptionType }}</td>
                <td class="border px-2 py-1">{{ item.impactCycle }}</td>
                <td class="border px-2 py-1">{{ item.responseMeasures }}</td>
              </tr>
              <tr v-if="exportData.length > 5">
                <td class="border px-2 py-1 text-center" colspan="14">还有 {{ exportData.length - 5 }} 条数据未显示</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-4 text-gray-500 text-sm">
          暂无数据可导出
        </div>
      </div>
      
      <button @click="hideImportExportSection" class="mt-2 text-sm text-gray-600 hover:text-gray-800">收起</button>
    </div>
    
    <div class="legend">
      <h4>项目状态说明</h4>
      <div class="legend-item">
        <div class="status-indicator status-orange">
          <span class="status-dot"></span>
        </div>
        <span>已签约</span>
      </div>
      <div class="legend-item">
        <div class="status-indicator status-yellow">
          <span class="status-dot"></span>
        </div>
        <span>实施中</span>
      </div>
      <div class="legend-item">
        <div class="status-indicator status-green">
          <span class="status-dot"></span>
        </div>
        <span>已完成</span>
      </div>
    </div>
    <div class="list-content">
      <div class="project-table">
        <table>
          <thead>
            <tr>
              <th style="width: 50px;">
                <input type="checkbox" @change="toggleSelectAll" :checked="selectAll">
              </th>
              <th style="width: 80px;">项目状态</th>
              <th>项目名称</th>
              <th>产品名称</th>
              <th>产品示意图</th>
              <th>客户名称及订单情况</th>
              <th>开始时间</th>
              <th>结束时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="project in projects" :key="project.id" :class="{ selected: selectedProjects.includes(project.id) }" :data-project-id="project.id">
              <td>
                <input type="checkbox" :value="project.id" v-model="selectedProjects">
              </td>
              <td>
                <div class="status-indicator" :class="getStatusClass(project.order_status)">
                  <span class="status-dot"></span>
                </div>
              </td>
              <td><a href="#" @click.prevent="goToDetail(project.id)" class="project-link">{{ project.project_name }}</a></td>
              <td>{{ project.product_name }}</td>
              <td>
                <div class="image-container">
                  <img
                    v-if="project.product_image && isValidImageUrl(project.product_image)"
                    :src="getImageUrl(project.product_image)"
                    :alt="'产品示意图-' + project.project_name"
                    class="product-image"
                    @load="onImageLoad(project.id)"
                    @error="onImageError(project.id)"
                    :class="{ 'image-loading': imageLoading[project.id], 'image-error': imageErrors[project.id] }"
                  />
                  <div v-else-if="project.product_image && isBase64Image(project.product_image)" class="image-placeholder">
                    Base64图像
                  </div>
                  <div v-else-if="imageErrors[project.id]" class="image-error-placeholder">
                    图片加载失败
                  </div>
                  <div v-else class="no-image-placeholder">
                    无图片
                  </div>
                  <div v-if="imageLoading[project.id]" class="image-loading-indicator">
                    加载中...
                  </div>
                </div>
              </td>
              <td>
                <div>{{ project.customer_name }}</div>
                <div class="order-status">{{ project.order_status || '无数据' }}</div>
              </td>
              <td>{{ project.planned_start_time }}</td>
              <td>{{ project.planned_end_time }}</td>
              <td>
                <!-- 操作按钮已移至工具栏 -->
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增项目模态框 -->
    <div class="modal" v-if="showAddModal">
      <div class="modal-content">
        <span class="close" @click="closeAddModal">&times;</span>
        <h3>新增项目</h3>
        <form @submit.prevent="addProject">
          <div class="form-group">
            <label>项目名称:</label>
            <input v-model="newProject.project_name" type="text" required />
          </div>
          <div class="form-group">
            <label>产品名称:</label>
            <input v-model="newProject.product_name" type="text" required />
          </div>
          <div class="form-group">
            <label>产品示意图:</label>
            <div class="image-upload">
              <input
                type="file"
                ref="imageInput"
                accept="image/*"
                @change="handleImageSelect"
                style="display: none;"
              />
              <button type="button" class="btn btn-secondary" @click="triggerImageSelect">
                选择图片
              </button>
              <span v-if="newProject.product_image_name" class="file-name">
                {{ newProject.product_image_name }}
              </span>
              <!-- 图片预览 -->
              <img
                v-if="newProject.product_image_preview"
                :src="newProject.product_image_preview"
                alt="预览"
                class="image-preview"
              />
            </div>
          </div>
          <div class="form-group">
            <label>客户名称:</label>
            <input v-model="newProject.customer_name" type="text" required />
          </div>
          <div class="form-group">
            <label>订单情况:</label>
            <select v-model="newProject.order_status">
              <option value="已签约">已签约</option>
              <option value="实施中">实施中</option>
              <option value="已完成">已完成</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>计划开始时间:</label>
              <input v-model="newProject.planned_start_time" type="date" />
            </div>
            <div class="form-group">
              <label>计划结束时间:</label>
              <input v-model="newProject.planned_end_time" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>责任部门:</label>
            <input v-model="newProject.responsible_department" type="text" />
          </div>
          <div class="form-group">
            <label>负责人:</label>
            <input v-model="newProject.responsible_person" type="text" />
          </div>
          <div class="form-actions">
            <button type="button" @click="closeAddModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">添加</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 项目详情模态框 -->
    <div class="modal" v-if="showDetailModal">
      <div class="modal-content detail-modal">
        <span class="close" @click="closeDetailModal">&times;</span>
        <h3>项目详情</h3>
        <div class="detail-content">
          <div class="detail-row">
            <span class="detail-label">项目名称:</span>
            <span class="detail-value">{{ detailProject.project_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">产品名称:</span>
            <span class="detail-value">{{ detailProject.product_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">产品示意图:</span>
            <div class="detail-value">
              <div class="image-container">
                <img
                  v-if="detailProject.product_image && isValidImageUrl(detailProject.product_image)"
                  :src="getImageUrl(detailProject.product_image)"
                  :alt="'产品示意图-' + detailProject.project_name"
                  class="detail-image"
                  @load="onDetailImageLoad"
                  @error="onDetailImageError"
                  :class="{ 'image-loading': detailImageLoading, 'image-error': detailImageError }"
                />
                <div v-else-if="detailProject.product_image && isBase64Image(detailProject.product_image)" class="image-placeholder">
                  Base64图像
                </div>
                <div v-else-if="detailImageError" class="image-error-placeholder">
                  图片加载失败
                </div>
                <div v-else class="no-image-placeholder">
                  无图片
                </div>
                <div v-if="detailImageLoading" class="image-loading-indicator">
                  加载中...
                </div>
              </div>
            </div>
          </div>
          <div class="detail-row">
            <span class="detail-label">客户名称:</span>
            <span class="detail-value">{{ detailProject.customer_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">订单情况:</span>
            <span class="detail-value">{{ detailProject.order_status }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">创建时间:</span>
            <span class="detail-value">{{ detailProject.created_at || '未知' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">更新时间:</span>
            <span class="detail-value">{{ detailProject.updated_at || '未知' }}</span>
          </div>

          <!-- 里程碑信息 -->
          <div class="milestones-section">
            <h4>关键里程碑节点</h4>
            <div v-if="detailProject.milestones && detailProject.milestones.length > 0">
              <div
                v-for="(milestone, index) in detailProject.milestones"
                :key="milestone.id"
                class="milestone-item"
              >
                <div class="milestone-header">
                  <h5>里程碑 {{ index + 1 }}: {{ milestone.milestone }}</h5>
                  <button
                    class="btn btn-secondary btn-small"
                    @click="editMilestone(milestone)"
                  >
                    编辑
                  </button>
                </div>
                <div class="milestone-details">
                  <div class="detail-row">
                    <span class="detail-label">负责部门:</span>
                    <span class="detail-value">{{ milestone.responsible_department || '未指定' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">计划开始时间:</span>
                    <span class="detail-value">{{ milestone.planned_start_time || '未指定' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">计划结束时间:</span>
                    <span class="detail-value">{{ milestone.planned_end_time || '未指定' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">实际完成时间:</span>
                    <span class="detail-value">{{ milestone.actual_completion_time || '未完成' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">负责人:</span>
                    <span class="detail-value">{{ milestone.responsible_person || '未指定' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">异常类别:</span>
                    <span class="detail-value">{{ milestone.exception_type || '无' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">影响周期:</span>
                    <span class="detail-value">{{ milestone.impact_cycle ? milestone.impact_cycle + ' 天' : '无' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">应对措施:</span>
                    <span class="detail-value">{{ milestone.response_measures || '无' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">修改日志:</span>
                    <span class="detail-value">{{ milestone.modification_log || '无' }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p>暂无里程碑信息</p>
            </div>
          </div>
        </div>
        <div class="detail-actions">
          <button class="btn btn-secondary" @click="editProject(detailProject)">编辑项目</button>
          <button class="btn btn-primary" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 项目编辑模态框 -->
    <div class="modal" v-if="showEditModal">
      <div class="modal-content">
        <span class="close" @click="closeEditModal">&times;</span>
        <h3>编辑项目</h3>
        <form @submit.prevent="updateProject">
          <div class="form-group">
            <label>项目名称:</label>
            <input v-model="editingProject.project_name" type="text" required />
          </div>
          <div class="form-group">
            <label>产品名称:</label>
            <input v-model="editingProject.product_name" type="text" required />
          </div>
          <div class="form-group">
            <label>产品示意图:</label>
            <div class="image-upload">
              <input
                type="file"
                ref="editImageInput"
                accept="image/*"
                @change="handleEditImageSelect"
                style="display: none;"
              />
              <button type="button" class="btn btn-secondary" @click="triggerEditImageSelect">
                选择图片
              </button>
              <span v-if="editingProject.product_image_name" class="file-name">
                {{ editingProject.product_image_name }}
              </span>
              <!-- 图片预览 -->
              <img
                v-if="editingProject.product_image_preview"
                :src="editingProject.product_image_preview"
                alt="预览"
                class="image-preview"
              />
              <div v-else-if="editingProject.product_image && editingProject.product_image.startsWith('data:image')" class="image-preview-container">
                <img
                  :src="editingProject.product_image"
                  alt="当前图片"
                  class="image-preview"
                />
                <p>当前图片</p>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>客户名称:</label>
            <input v-model="editingProject.customer_name" type="text" required />
          </div>
          <div class="form-group">
            <label>订单情况:</label>
            <select v-model="editingProject.order_status">
              <option value="已签约">已签约</option>
              <option value="实施中">实施中</option>
              <option value="已完成">已完成</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeEditModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 里程碑编辑模态框 -->
    <div class="modal" v-if="showMilestoneEditModal">
      <div class="modal-content">
        <span class="close" @click="closeMilestoneEditModal">&times;</span>
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
            <button type="button" @click="closeMilestoneEditModal" class="btn btn-secondary">取消</button>
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
  name: 'ProjectList',
  data() {
    return {
      projects: [],
      showAddModal: false,
      showDetailModal: false,
      showMilestoneEditModal: false,
      showEditModal: false, // 添加编辑模态框状态
      newProject: {
        project_name: '',
        product_name: '',
        product_image: null,
        product_image_name: '',
        customer_name: '',
        order_status: '已签约',
        responsible_department: '',
        planned_start_time: '',
        planned_end_time: '',
        responsible_person: ''
      },
      detailProject: {},
      editingProject: {}, // 添加编辑项目的数据
      editingMilestone: {},
      selectedProjects: [], // 选中的项目
      selectAll: false, // 是否全选
      // 图片加载状态管理
      imageLoading: {},
      imageErrors: {},
      detailImageLoading: false,
      detailImageError: false,
      // 导入导出相关
      showImportExport: false,
      selectedImportFile: null,
      importing: false,
      importResult: null,
      exportFileName: '项目数据',
      exporting: false,
      exportData: [],
      // 定时任务相关
      statusUpdateTimer: null
    }
  },
  mounted() {
    this.fetchProjects()
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
    async fetchProjects() {
      try {
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          // 只计算状态，不主动更新数据库
          const projectsWithStatus = response.data.data.map(project => ({
            ...project,
            order_status: this.calculateProjectStatus(project)
          }))

          this.projects = projectsWithStatus
          this.filteredProjects = projectsWithStatus
          this.total = projectsWithStatus.length
          this.loading = false
          this.currentPage = 1
          this.filterProjects()
        }
      } catch (error) {
        console.error('获取项目数据失败:', error)
        this.loading = false
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
          
          // 更新完成后重新获取项目列表
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
        // 确保正确处理日期比较
        const startDateValid = !date.start || date.start > today;
        const endDateValid = !date.end || date.end > today;
        return startDateValid && endDateValid;
      });
      
      // 如果今天是任何里程碑的开始日期，则项目应标记为"实施中"
      const startsToday = milestoneDates.some(date => {
        return date.start && date.start.getTime() === today.getTime();
      });
      
      if (startsToday) {
        return '实施中';
      }
      
      if (allInFuture) {
        return '已签约';
      }
      
      // 检查是否所有里程碑的计划结束时间都在今天之前（已完成）
      const allCompleted = milestoneDates.every(date => {
        const endDateValid = date.end && date.end < today;
        return endDateValid;
      });
      
      if (allCompleted) {
        return '已完成';
      }
      
      // 检查是否在任何里程碑的执行期间（实施中）
      // 今天在任何一个里程碑的时间范围内（左闭右闭区间）
      const anyInProgress = milestoneDates.some(date => {
        // 如果有开始和结束时间，检查今天是否在这两个时间之间（包含边界）
        if (date.start && date.end) {
          return date.start <= today && today <= date.end;
        }
        // 如果只有开始时间，检查今天是否在开始之后（包含边界）
        if (date.start) {
          return date.start <= today;
        }
        // 如果只有结束时间，检查今天是否在结束之前（包含边界）
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
    
    async calculateAndSyncProjectStatus(project) {
      // 计算项目状态
      const calculatedStatus = this.calculateProjectStatus(project);
      
      // 如果计算出的状态与数据库中的状态不同，则更新数据库
      if (calculatedStatus !== project.order_status) {
        console.log(`项目 ${project.id} 状态发生变化，从 "${project.order_status}" 变为 "${calculatedStatus}"`);
        const success = await this.updateProjectStatusInDatabase(project.id, calculatedStatus);
        if (success) {
          // 更新成功后，刷新数据
          await this.fetchProjects();
        }
      } else {
        console.log(`项目 ${project.id} 状态未发生变化: "${calculatedStatus}"`);
      }
      
      return calculatedStatus;
    },
    
    initializeImageStates(projects) {
      // 初始化每个项目的图片加载状态
      projects.forEach(project => {
        this.$set(this.imageLoading, project.id, false)
        this.$set(this.imageErrors, project.id, false)
      })
    },
    
    showAddForm() {
      this.showAddModal = true
      // 重置表单
      this.newProject = {
        project_name: '',
        product_name: '',
        product_image: null,
        product_image_name: '',
        customer_name: '',
        order_status: '已签约',
        responsible_department: '',
        planned_start_time: '',
        planned_end_time: '',
        responsible_person: ''
      }
    },
    
    goToDetail(projectId) {
      this.$router.push(`/admin/projects/detail/${projectId}`);
    },
    
    confirmDeleteSelected() {
      if (this.selectedProjects.length === 0) {
        alert('请先选择要删除的项目');
        return;
      }
      
      const projectNames = this.projects
        .filter(p => this.selectedProjects.includes(p.id))
        .map(p => p.project_name);
      
      const message = `确定要删除选中的 ${this.selectedProjects.length} 个项目吗？

${projectNames.join('\n')}

此操作将同时删除这些项目及其所有里程碑信息，且不可恢复。`;
      if (confirm(message)) {
        this.deleteSelectedProjects();
      }
    },
    
    async deleteSelectedProjects() {
      try {
        // 批量删除项目
        const deletePromises = this.selectedProjects.map(id => 
          axios.delete(`/api/sys_project/${id}`)
        );
        
        const responses = await Promise.all(deletePromises);
        
        // 检查是否有删除失败的项目
        const failedDeletes = responses.filter(r => r.data.code !== 200);
        
        if (failedDeletes.length > 0) {
          alert(`有 ${failedDeletes.length} 个项目删除失败: ${failedDeletes.map(r => r.data.message).join(', ')}`);
        } else {
          alert(`${this.selectedProjects.length} 个项目删除成功!`);
        }
        
        // 清空选中项并刷新数据
        this.selectedProjects = [];
        this.selectAll = false;
        this.fetchProjects();
      } catch (error) {
        console.error('删除项目失败:', error);
        alert('删除项目时发生错误');
      }
    },
    closeAddModal() {
      this.showAddModal = false
    },
    showDetail(project) {
      this.detailProject = { ...project }
      this.showDetailModal = true
    },
    closeDetailModal() {
      this.showDetailModal = false
    },
    triggerImageSelect() {
      this.$refs.imageInput.click()
    },
    handleImageSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.newProject.product_image = file
        this.newProject.product_image_name = file.name

        // 可选：将图片转换为Base64用于预览
        const reader = new FileReader()
        reader.onload = (e) => {
          this.newProject.product_image_preview = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    async addProject() {
      try {
        const formData = new FormData()
        formData.append('project_name', this.newProject.project_name)
        formData.append('product_name', this.newProject.product_name)
        formData.append('customer_name', this.newProject.customer_name)
        formData.append('order_status', this.newProject.order_status)
        formData.append('responsible_department', this.newProject.responsible_department)
        formData.append('planned_start_time', this.newProject.planned_start_time)
        formData.append('planned_end_time', this.newProject.planned_end_time)
        formData.append('responsible_person', this.newProject.responsible_person)

        if (this.newProject.product_image) {
          // 读取文件内容并转换为Base64
          const fileReader = new FileReader()
          fileReader.onload = async (e) => {
            // 将Base64数据添加到表单中
            formData.append('product_image', e.target.result)

            // 发送请求
            const response = await axios.post('/api/sys_project', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })

            if (response.data.code === 200) {
              this.closeAddModal()
              this.fetchProjects() // 重新加载数据
              alert('项目添加成功!')
            } else {
              alert('添加失败: ' + response.data.message)
            }
          }
          fileReader.readAsDataURL(this.newProject.product_image)
          return // 异步处理，直接返回
        }

        // 如果没有图片文件，直接发送请求
        const response = await axios.post('/api/sys_project', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.code === 200) {
          this.closeAddModal()
          this.fetchProjects() // 重新加载数据
          alert('项目添加成功!')
        } else {
          alert('添加失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('添加项目失败:', error)
        alert('添加项目时发生错误')
      }
    },
    triggerFileImport() {
      this.$refs.fileInput.click()
    },
    async handleFileImport(event) {
      const file = event.target.files[0]
      if (!file) return

      const formData = new FormData()
      formData.append('file', file)

      try {
        // 这里应该调用实际的批量导入API
        // 由于后端尚未实现，我们暂时只显示一个提示
        alert('批量导入功能已触发，实际实现需要后端支持。文件名: ' + file.name)

        // 清空文件输入框
        event.target.value = ''
      } catch (error) {
        console.error('导入文件失败:', error)
        alert('导入文件时发生错误')
      }
    },
    editMilestone(milestone) {
      this.editingMilestone = { ...milestone }
      this.showMilestoneEditModal = true
    },
    closeMilestoneEditModal() {
      this.showMilestoneEditModal = false
    },
    async updateMilestone() {
      try {
        // 添加当前用户名到请求数据中
        const requestData = {
          ...this.editingMilestone,
          modified_by: localStorage.getItem('username') || 'Unknown'
        };
        
        const response = await axios.put(
          `/api/sys_project_milestone/${this.editingMilestone.id}`,
          requestData
        )

        if (response.data.code === 200) {
          this.closeMilestoneEditModal()
          this.fetchProjects() // 重新加载数据
          alert('里程碑更新成功!')
        } else {
          alert('更新失败: ' + response.data.message)
        }
      } catch (error) {
        console.error('更新里程碑失败:', error)
        alert('更新里程碑时发生错误')
      }
    },
    triggerEditImageSelect() {
      this.$refs.editImageInput.click()
    },
    handleEditImageSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.editingProject.product_image = file
        this.editingProject.product_image_name = file.name

        // 将图片转换为Base64用于预览
        const reader = new FileReader()
        reader.onload = (e) => {
          this.editingProject.product_image_preview = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    closeEditModal() {
      this.showEditModal = false
      // 清除文件输入框
      if (this.$refs.editImageInput) {
        this.$refs.editImageInput.value = ''
      }
    },
    // 添加编辑项目的方法
    editProject(project) {
      this.editingProject = { ...project }
      this.showDetailModal = false
      this.showEditModal = true
    },
    
    // 生成项目修改日志
    generateProjectModificationLog(editedProject) {
      // 获取原始项目数据
      const originalProject = this.projects.find(p => p.id === editedProject.id);
      if (!originalProject) return '';
      
      const changes = [];
      const fieldMapping = {
        'project_name': '项目名称',
        'product_name': '产品名称',
        'customer_name': '客户名称',
        'order_status': '订单状态'
      };
      
      // 对比各个字段
      Object.keys(fieldMapping).forEach(key => {
        const oldValue = originalProject[key] || '';
        const newValue = editedProject[key] || '';
        
        if (oldValue !== newValue) {
          changes.push(`${fieldMapping[key]}: 从"${oldValue}"修改为"${newValue}"`);
        }
      });
      
      if (changes.length === 0) return '';
      
      const currentTime = new Date().toLocaleString('zh-CN');
      return `${localStorage.getItem('username') || '用户'} 于 ${currentTime} 修改了 ${changes.join(', ')}`;
    },
    
    async updateProject() {
      try {
        console.log('开始更新项目');
        const formData = new FormData()
        formData.append('project_name', this.editingProject.project_name)
        formData.append('product_name', this.editingProject.product_name)
        formData.append('customer_name', this.editingProject.customer_name)
        formData.append('order_status', this.editingProject.order_status)
        
        // 生成修改日志并添加到表单数据中
        const modificationLog = this.generateProjectModificationLog(this.editingProject);
        if (modificationLog) {
          formData.append('modification_log', modificationLog);
        }

        console.log('准备发送的数据:', {
          project_name: this.editingProject.project_name,
          product_name: this.editingProject.product_name,
          customer_name: this.editingProject.customer_name,
          order_status: this.editingProject.order_status,
          modification_log: modificationLog
        });

        if (this.editingProject.product_image && typeof this.editingProject.product_image !== 'string') {
          console.log('处理新上传的文件');
          // 如果是文件对象，则读取为Base64
          const fileReader = new FileReader()
          fileReader.onload = async (e) => {
            formData.append('product_image', e.target.result)
            console.log('文件读取完成，准备发送请求');

            // 注意：使用FormData时不要手动设置Content-Type，让浏览器自动设置
            try {
              const response = await axios.put(
                `/api/sys_project/${this.editingProject.id}`,
                formData
              )
              console.log('收到服务器响应:', response);

              if (response.data.code === 200) {
                this.closeEditModal() // 关闭编辑模态框
                this.fetchProjects() // 重新加载数据
                alert('项目更新成功!')
              } else {
                console.error('服务器返回错误:', response.data)
                alert('更新失败: ' + response.data.message)
              }
            } catch (error) {
              console.error('更新项目失败:', error)
              console.error('错误详情:', {
                message: error.message,
                status: error.response?.status,
                statusText: error.response?.statusText,
                data: error.response?.data
              })
              alert('更新项目时发生错误: ' + error.message)
            }
          }

          fileReader.onerror = (e) => {
            console.error('文件读取出错:', e)
            alert('文件读取出错，请重新选择文件')
          }

          fileReader.readAsDataURL(this.editingProject.product_image)
          return
        } else {
          console.log('使用现有图片数据或无图片');
          // 如果是字符串（Base64数据或URL），直接使用
          formData.append('product_image', this.editingProject.product_image || '')

          // 注意：使用FormData时不要手动设置Content-Type，让浏览器自动设置
          try {
            const response = await axios.put(
              `/api/sys_project/${this.editingProject.id}`,
              formData
            )
            console.log('收到服务器响应:', response);

            if (response.data.code === 200) {
              this.closeEditModal() // 关闭编辑模态框
              this.fetchProjects() // 重新加载数据
              alert('项目更新成功!')
            } else {
              console.error('服务器返回错误:', response.data)
              alert('更新失败: ' + response.data.message)
            }
          } catch (error) {
            console.error('更新项目失败:', error)
            console.error('错误详情:', {
              message: error.message,
              status: error.response?.status,
              statusText: error.response?.statusText,
              data: error.response?.data
            })
            alert('更新项目时发生错误: ' + error.message)
          }
        }
      } catch (error) {
        console.error('更新项目失败:', error)
        alert('更新项目时发生错误')
      }
    },

    // 删除项目相关的方法已移至 confirmDeleteSelected 和 deleteSelectedProjects
    toggleSelectAll() {
      this.selectAll = !this.selectAll;
      if (this.selectAll) {
        this.selectedProjects = this.projects.map(project => project.id);
      } else {
        this.selectedProjects = [];
      }
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
    
    onDetailImageLoad() {
      // 详情图片加载成功回调
      this.detailImageLoading = false;
      this.detailImageError = false;
    },
    
    onDetailImageError() {
      // 详情图片加载失败回调
      this.detailImageLoading = false;
      this.detailImageError = true;
    },
    
    async handleStatusChange(row) {
      try {
        const response = await axios.put(`/api/sys_project/${row.id}`, {
          order_status: row.order_status
        })

        if (response.data.code === 200) {
          this.$message.success('状态更新成功')
          // 不再重新获取数据，而是直接更新本地数据
          const index = this.projects.findIndex(p => p.id === row.id)
          if (index !== -1) {
            this.$set(this.projects[index], 'order_status', row.order_status)
          }
        } else {
          this.$message.error('状态更新失败: ' + response.data.message)
          // 恢复原状态
          const originalProject = this.projects.find(p => p.id === row.id)
          if (originalProject) {
            row.order_status = originalProject.order_status
          }
        }
      } catch (error) {
        this.$message.error('状态更新失败: ' + error.message)
        // 恢复原状态
        const originalProject = this.projects.find(p => p.id === row.id)
        if (originalProject) {
          row.order_status = originalProject.order_status
        }
      }
    },
    showImportExportSection() {
      this.showImportExport = true;
    },
    hideImportExportSection() {
      this.showImportExport = false;
    },
    handleImportFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedImportFile = file;
      }
    },
    async importProjectsFromExcel() {
      if (!this.selectedImportFile) {
        alert('请选择一个Excel文件');
        return;
      }

      this.importing = true;
      this.importResult = null;

      const formData = new FormData();
      formData.append('file', this.selectedImportFile);

      try {
        // 检查API是否存在
        const apiResponse = await axios.options('/api/sys_project/import').catch(() => ({}));
        
        const response = await axios.post('/api/import_projects', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (response.data.code === 200) {
          this.importResult = {
            success: true,
            message: '导入成功',
            data: response.data.data
          };
          this.fetchProjects(); // 重新加载数据
        } else {
          this.importResult = {
            success: false,
            message: '导入失败: ' + response.data.message
          };
        }
      } catch (error) {
        console.error('导入项目数据失败:', error);
        
        // 更详细的错误信息
        let errorMessage = '导入项目数据时发生错误';
        if (error.response) {
          // 服务器响应了错误状态码
          if (error.response.status === 404) {
            errorMessage = '导入接口不存在，请联系系统管理员';
          } else if (error.response.status === 500) {
            errorMessage = '服务器内部错误，请稍后再试';
          } else {
            errorMessage = `导入失败 (${error.response.status}): ${error.response.data?.message || '未知错误'}`;
          }
        } else if (error.request) {
          // 请求已发出但没有收到响应
          errorMessage = '网络连接失败，请检查网络设置';
        }
        
        this.importResult = {
          success: false,
          message: errorMessage
        };
      } finally {
        this.importing = false;
      }
    },
    downloadTemplate() {
      // 下载服务器上的模板文件
      const link = document.createElement('a');
      link.href = '/templates/项目模板.xls'; // 指向服务器上的模板文件
      link.download = '项目模板.xls';
      link.click();
    },
    async exportToExcel() {
      if (this.exporting) return;

      this.exporting = true;
      this.exportData = [];

      try {
        const response = await axios.get('/api/sys_project/export', {
          responseType: 'blob'
        });

        if (response.status === 200) {
          const workbook = XLSX.read(response.data, { type: 'array' });
          const worksheet = workbook.Sheets[workbook.SheetNames[0]];
          const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

          this.exportData = data.map((row, index) => ({
            index: index + 1,
            projectName: row[0],
            productName: row[1],
            productImageUrl: row[2],
            customerInfo: row[3],
            milestone: row[4],
            department: row[5],
            plannedStartTime: row[6],
            plannedEndTime: row[7],
            actualCompletionTime: row[8],
            responsiblePerson: row[9],
            exceptionType: row[10],
            impactCycle: row[11],
            responseMeasures: row[12]
          }));
        } else {
          alert('导出失败: ' + response.statusText);
        }
      } catch (error) {
        console.error('导出项目数据失败:', error);
        alert('导出项目数据时发生错误');
      } finally {
        this.exporting = false;
      }
    },
    isImage(url) {
      if (!url) return false;
      return /\.(jpg|jpeg|png|gif|bmp)$/i.test(url);
    },
    isPdf(url) {
      if (!url) return false;
      return /\.pdf$/i.test(url);
    },
    openImagePreview(url) {
      window.open(url, '_blank');
    },
    openPdfPreview(url) {
      window.open(url, '_blank');
    },
    openFile(url) {
      window.open(url, '_blank');
    }
  }
}
</script>

<style scoped>
.project-list {
  padding: 20px;
  background-color: #f5f7fa;
}

.project-list h2 {
  color: #333;
  margin-bottom: 20px;
}

.toolbar {
  margin-bottom: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
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

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-danger:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
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

.project-link {
  color: #4A90E2;
  text-decoration: none;
}

.project-link:hover {
  text-decoration: underline;
}

.order-status {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.action-btn {
  background-color: #4A90E2;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.action-btn:hover {
  background-color: #357AE8;
}

.delete-btn {
  background-color: #e74c3c;
  margin-left: 5px;
}

.delete-btn:hover {
  background-color: #c0392b;
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
  overflow-y: auto; /* 允许模态框滚动 */
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

.detail-modal {
  max-width: 800px;
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

.image-upload {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.file-name {
  font-size: 14px;
  color: #666;
}

.image-preview {
  max-width: 100px;
  max-height: 100px;
  margin-top: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* 详情模态框样式 */
.detail-content {
  margin-top: 20px;
  max-height: 70vh;
  overflow-y: auto; /* 允许详情内容滚动 */
}

.detail-row {
  display: flex;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-label {
  font-weight: bold;
  width: 150px;
  flex-shrink: 0;
}

.detail-value {
  flex: 1;
}

.detail-image {
  max-width: 200px;
  max-height: 150px;
}

/* 里程碑样式 */
.milestones-section {
  margin-top: 30px;
}

.milestone-item {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.milestone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.milestone-header h5 {
  margin: 0;
  color: #333;
}

.milestone-details .detail-row {
  margin-bottom: 10px;
  padding-bottom: 10px;
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

.selected {
  background-color: #f0f8ff;
}

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

.detail-image {
  max-width: 200px;
  max-height: 150px;
}

.image-error-placeholder {
  color: #e74c3c;
}
</style>