<template>
  <div class="project-members">
    <h2>👥 项目成员</h2>
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
</template>

<script>
import axios from 'axios'

export default {
  name: 'ProjectMembers',
  data() {
    return {
      projects: []
    }
  },
  mounted() {
    this.fetchProjectMembers()
  },
  methods: {
    async fetchProjectMembers() {
      try {
        const response = await axios.get('/api/sys_project')
        if (response.data.code === 200) {
          this.projects = response.data.data
        }
      } catch (error) {
        console.error('获取项目成员数据失败:', error)
      }
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
.project-members {
  padding: 20px;
}

.project-members h2 {
  color: #333;
  margin-bottom: 20px;
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