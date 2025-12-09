<template>
  <div class="admin-container">
    <!-- 侧边栏导航 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <h2>管理中心</h2>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li :class="{ active: currentMenu === 'index' }" @click="switchMenu('index')">
            <span class="icon">🏠</span>
            <span>首页</span>
          </li>
          <li :class="{ active: currentMenu === 'dashboard' }" @click="switchMenu('dashboard')">
            <span class="icon">📊</span>
            <span>OA数据看板</span>
          </li>
          <li :class="{ active: currentMenu === 'projects' }" @click="toggleProjectsMenu">
            <span class="icon">📁</span>
            <span>新制项目管理</span>
            <span class="arrow" :class="{ 'arrow-rotate': showProjectsSubmenu }">▼</span>
          </li>
          <transition name="slide">
            <ul v-show="showProjectsSubmenu" class="submenu">

              <li :class="{ active: currentMenu === 'projects-overview' }" @click="switchMenu('projects-overview')">
                <span class="icon">📈</span>
                <span>项目概览</span>
              </li>
              <li :class="{ active: currentMenu === 'projects-list' }" @click="switchMenu('projects-list')">
                              <span class="icon">📋</span>
                              <span>项目列表</span>
                            </li>
              <li :class="{ active: currentMenu === 'projects-progress' }" @click="switchMenu('projects-progress')">
                <span class="icon">📊</span>
                <span>项目进度</span>
              </li>
            </ul>
          </transition>

          <li :class="{ active: currentMenu === 'permissions' }" @click="switchMenu('permissions')">
            <span class="icon">🔑</span>
            <span>权限设置</span>
          </li>
          <li :class="{ active: currentMenu === 'history' }" @click="switchMenu('history')">
            <span class="icon">📝</span>
            <span>操作历史</span>
          </li>
          <li :class="{ active: currentMenu === 'modificationLog' }" @click="switchMenu('modificationLog')">
            <span class="icon">📋</span>
            <span>修改日志</span>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航栏 -->
      <header class="main-header">
        <div class="logo-container">
          <img src="../image/logo.jpg" alt="Logo" class="header-logo">
        </div>
        <div class="user-info" @mouseenter="showUserMenu = true" @mouseleave="showUserMenu = false">
          <span class="username">{{ username }} (管理员)</span>
          <div class="user-dropdown" v-show="showUserMenu">
            <div class="dropdown-item" @click="goToProfile">
              <span class="icon">👤</span>
              个人中心
            </div>
            <div class="dropdown-item" @click="goToSettings">
              <span class="icon">⚙️</span>
              账户设置
            </div>
            <div class="dropdown-item" @click="changePassword">
              <span class="icon">🔒</span>
              修改密码
            </div>
            <div class="dropdown-item" @click="changeAvatar">
              <span class="icon">🖼️</span>
              修改头像
            </div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item logout-item" @click="handleLogout">
              <span class="icon">🚪</span>
              注销
            </div>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-content" ref="pageContent">
        <component 
          :is="currentComponent" 
          :key="componentKey"
          :username="username"
          v-if="componentLoaded"
        ></component>
        <div v-else class="loading-placeholder">
          组件加载中...
        </div>
      </div>
    </main>
    
    <!-- 回到顶部按钮 -->
    <div class="back-to-top" v-show="showBackToTop" @click="scrollToTop">
      <span class="arrow-up">↑</span>
    </div>
  </div>
</template>

<script>
import Dashboard from '../components/admin/Dashboard.vue'
import Profile from '../components/admin/Profile.vue'
import Settings from '../components/admin/Settings.vue'
import History from '../components/admin/History.vue'
import Permissions from '../components/admin/Permissions.vue'
import Projects from '../components/admin/Projects.vue'
import ProjectList from '../components/admin/projects/List.vue'
import ModificationLog from '../components/admin/ModificationLog.vue'
import ProjectProgress from '../components/admin/projects/Progress.vue'
import Home from '../components/admin/Home.vue'
import { authAPI } from '../services/api'

export default {
  name: 'AdminCenter',
  components: {
    Dashboard,
    Profile,
    Settings,
    History,
    Permissions,
    Projects,
    ProjectList,
    ModificationLog,
    ProjectProgress,
    Home
  },
  data() {
    return {
      currentMenu: 'index', // 默认页面改为首页
      componentKey: 0,
      username: '管理员', // 实际应用中应从登录信息获取
      componentLoaded: true,
      showProjectsSubmenu: false, // 控制项目管理子菜单的显示
      showUserMenu: false, // 控制用户菜单的显示
      showBackToTop: false, // 控制回到顶部按钮的显示
      scrollThreshold: 100 // 降低滚动阈值，方便测试
    }
  },
  mounted() {
    this.fetchUserInfo();
    this.handleRouteQuery();
    // 使用 nextTick 确保 DOM 已经渲染完成
    this.$nextTick(() => {
      // 添加滚动事件监听器
      if (this.$refs.pageContent) {
        this.$refs.pageContent.addEventListener('scroll', this.throttledHandleScroll);
        console.log('滚动监听器已添加');
      }
    });
  },
  beforeDestroy() {
    // 移除滚动事件监听器
    if (this.$refs.pageContent) {
      this.$refs.pageContent.removeEventListener('scroll', this.throttledHandleScroll);
    }
  },
  computed: {
    currentComponent() {
      switch(this.currentMenu) {
        case 'index':
          return Home
        case 'dashboard':
          return Dashboard
        case 'profile':
          return Profile
        case 'settings':
          return Settings
        case 'permissions':
          return Permissions
        case 'history':
          return History
        case 'modificationLog':
          return ModificationLog
        case 'projects':
        case 'projects-list':
          return ProjectList
        case 'projects-overview':
          // 返回项目概览组件
          return Projects
        case 'projects-progress':
          // 返回项目进度组件
          return ProjectProgress
        default:
          return Dashboard
      }
    }
  },
  methods: {
    // 切换项目管理子菜单的显示状态
    toggleProjectsMenu() {
      this.showProjectsSubmenu = !this.showProjectsSubmenu;
    },
    
    switchMenu(menu) {
      console.log('点击菜单:', menu, '当前菜单:', this.currentMenu);
      // 设置加载状态
      this.componentLoaded = false;
      // 更新当前菜单
      this.currentMenu = menu
      // 总是增加componentKey以确保组件刷新
      this.componentKey++
      // 模拟组件加载完成
      this.$nextTick(() => {
        this.componentLoaded = true;
      });
      console.log('切换到菜单:', menu, 'componentKey:', this.componentKey);
    },
    handleLogout() {
      // 注销逻辑
      localStorage.removeItem('currentUser')
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      this.$router.push('/Login')
    },
    goToProfile() {
      this.switchMenu('profile')
      this.showUserMenu = false
    },
    goToSettings() {
      this.switchMenu('settings')
      this.showUserMenu = false
    },
    changePassword() {
      this.switchMenu('settings')
      this.showUserMenu = false
    },
    changeAvatar() {
      this.switchMenu('profile')
      this.showUserMenu = false
    },
    async fetchUserInfo() {
      try {
        const res = await authAPI.getMe();
        if (res.code === 200) {
          this.username = res.data.username || '未知管理员';
        } else {
          this.username = '未知管理员';
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.username = '未知管理员';
      }
    },
    
    // 处理路由查询参数以切换菜单
    handleRouteQuery() {
      const query = this.$route.query;
      if (query.menu) {
        // 展开项目管理子菜单
        this.showProjectsSubmenu = true;
        // 切换到指定菜单
        this.switchMenu(query.menu);
      }
    },
    
    // 节流处理滚动事件
    throttledHandleScroll: function() {
      // 节流，避免频繁触发
      if (!this.throttleTimer) {
        this.throttleTimer = setTimeout(() => {
          this.handleScroll();
          this.throttleTimer = null;
        }, 100);
      }
    },
    
    // 处理滚动事件
    handleScroll() {
      if (!this.$refs.pageContent) return;
      
      const scrollTop = this.$refs.pageContent.scrollTop;
      const shouldShow = scrollTop > this.scrollThreshold;
      
      // 只有在状态改变时才更新，减少不必要的重渲染
      if (this.showBackToTop !== shouldShow) {
        this.showBackToTop = shouldShow;
      }
      
      // 添加调试信息
      console.log('滚动位置:', scrollTop, '是否显示按钮:', this.showBackToTop);
    },
    
    // 滚动到顶部
    scrollToTop() {
      const pageContent = this.$refs.pageContent;
      if (pageContent) {
        pageContent.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
        console.log('滚动到顶部');
      }
    },
  },
  // 监听路由变化
  watch: {
    '$route'(to) {
      if (to.query.menu) {
        this.showProjectsSubmenu = true;
        this.switchMenu(to.query.menu);
      }
    }
  }
}
</script>

<style scoped>
.admin-container {
  display: flex;
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #87CEFA 0%, #6495ED 100%); /* 淡蓝色渐变 */
  color: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  flex-shrink: 0; /* 防止侧边栏被压缩 */
  position: relative; /* 相对定位 */
}

.sidebar-logo {
  padding: 25px 0;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  padding: 15px 25px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  position: relative;
}

/* 添加箭头样式 */
.arrow {
  margin-left: auto;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.arrow-rotate {
  transform: rotate(180deg);
}

/* 子菜单样式 */
.submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: rgba(0, 0, 0, 0.1);
}

.submenu li {
  padding: 12px 25px 12px 45px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.submenu li:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.submenu li.active {
  background-color: rgba(255, 255, 255, 0.15);
  border-left-color: #00B4A0;
}

.submenu .icon {
  margin-right: 12px;
  font-size: 16px;
  width: 20px;
  text-align: center;
}

/* 添加滑动动画效果 */
.slide-enter-active,
.slide-leave-active {
  transition: max-height 0.3s ease;
  overflow: hidden;
}

.slide-enter,
.slide-leave-to {
  max-height: 0;
}

.slide-enter-to,
.slide-leave {
  max-height: 200px;
}

.sidebar-nav li:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-nav li.active {
  background-color: rgba(255, 255, 255, 0.15);
  border-left-color: #00B4A0;
}

.sidebar-nav .icon {
  margin-right: 12px;
  font-size: 18px;
  width: 20px;
  text-align: center;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 允许内容区域收缩 */
}

.main-header {
  height: 60px;
  background: linear-gradient(90deg, #E0F7FF 0%, #B0E0E6 100%); /* 与左侧导航栏搭配的淡蓝色渐变 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
}

.logo-container {
  display: flex;
  align-items: center;
  height: 100%;
}

.header-logo {
  height: 40px;
  width: auto;
  object-fit: contain;
  border-radius: 4px;
}

.user-info {
  display: flex;
  align-items: center;
  position: relative;
  cursor: pointer;
}

.username {
  margin-right: 20px;
  font-weight: 500;
  color: #333;
  transition: color 0.2s;
}

.username:hover {
  color: #4A90E2;
}

.logout-btn {
  background-color: #00B4A0; /* 与搜索按钮相同的颜色 */
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.logout-btn:hover {
  background-color: #009380; /* 搜索按钮的深色变体 */
  transform: translateY(-2px);
}

/* 用户下拉菜单样式 */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 10px 0;
  min-width: 160px;
  z-index: 100;
  border: 1px solid #eee;
}

.dropdown-item {
  padding: 12px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
  color: #333;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
}

.dropdown-item .icon {
  margin-right: 10px;
  font-size: 16px;
}

.dropdown-divider {
  height: 1px;
  background-color: #eee;
  margin: 5px 0;
}

.logout-item {
  color: #e74c3c;
}

.logout-item:hover {
  background-color: #fdf2f2;
}

.page-content {
  flex: 1;
  padding: 25px;
  overflow-y: auto;
}

.loading-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 18px;
  color: #666;
}

/* 回到顶部按钮样式 */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background-color: #4A90E2;
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 1000;
  /* 添加测试用的边框，确保按钮可见 */
  border: 2px solid #fff;
}

.back-to-top:hover {
  background-color: #357AE8;
  transform: translateY(-3px);
}

.arrow-up {
  font-size: 24px;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 70px;
  }
  
  .sidebar-logo h2,
  .sidebar-nav span:not(.icon) {
    display: none;
  }
  
  .sidebar-nav li {
    justify-content: center;
    padding: 15px 0;
  }
  
  .sidebar-nav .icon {
    margin-right: 0;
    font-size: 20px;
  }
  
  .page-content {
    padding: 10px;
  }
}
</style>