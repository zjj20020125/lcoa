<template>
  <div class="projects-container">
    <h2 class="title">📁 新制项目管理</h2>
    
    <!-- 横向导航栏 -->
    <div class="horizontal-nav">
      <div 
        class="nav-item" 
        :class="{ active: currentSubTab === 'overview' }" 
        @click="switchSubTab('overview')"
      >
        项目概览
      </div>
    </div>
    
    <!-- 子页面内容 -->
    <div class="sub-content">
      <component :is="currentSubComponent"></component>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import ProjectOverview from './projects/Overview.vue'

export default {
  name: 'Projects',
  components: {
    ProjectOverview
  },
  props: {
    defaultTab: {
      type: String,
      default: 'overview'
    }
  },
  setup(props) {
    const currentSubTab = ref(props.defaultTab || 'overview')

    // 切换子标签页
    const switchSubTab = (tab) => {
      currentSubTab.value = tab
    }
    
    // 获取当前子组件
    const currentSubComponent = computed(() => {
      switch (currentSubTab.value) {
        case 'overview':
          return 'ProjectOverview'
        default:
          return 'ProjectOverview'
      }
    })

    return {
      currentSubTab,
      switchSubTab,
      currentSubComponent
    }
  }
}
</script>

<style scoped>
.projects-container {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: relative;
  width: calc(100% - 60px);
  max-width: calc(100vw - 220px);
  box-sizing: border-box;
  margin: 20px;
}

.projects-container h2 {
  margin-top: 0;
  color: #4A90E2;
  font-size: 28px;
  text-align: center;
  margin-bottom: 25px;
}

/* 横向导航栏样式 */
.horizontal-nav {
  display: flex;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.nav-item {
  flex: 1;
  text-align: center;
  padding: 15px 0;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #666;
  border-bottom: 3px solid transparent;
}

.nav-item:hover {
  background: #e9ecef;
}

.nav-item.active {
  color: #4A90E2;
  border-bottom-color: #4A90E2;
  background: #ffffff;
}

.sub-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  min-height: 400px;
}

@media (max-width: 768px) {
  .horizontal-nav {
    flex-direction: column;
  }
  
  .nav-item {
    border-bottom: 1px solid #eee;
    border-left: 3px solid transparent;
  }
  
  .nav-item.active {
    border-bottom-color: #eee;
    border-left-color: #4A90E2;
  }
}
</style>