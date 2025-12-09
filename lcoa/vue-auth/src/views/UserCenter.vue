<template>
  <div class="user-container">
    <!-- 侧边栏导航 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <h2>用户中心</h2>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li :class="{ active: currentMenu === 'index' }" @click="switchMenu('index')">
            <span class="icon">🏠</span>
            <span>首页</span>
          </li>
          <li :class="{ active: currentMenu === 'dashboard' }" @click="switchMenu('dashboard')">
            <span class="icon">📊</span>
            <span>数据看板</span>
          </li>
          <li :class="{ active: currentMenu === 'projects' }" @click="toggleProjectsMenu">
            <span class="icon">📁</span>
            <span>新制项目管理</span>
            <span class="arrow" :class="{ 'arrow-rotate': showProjectsSubmenu }">▼</span>
          </li>
          <transition name="slide">
            <ul v-show="showProjectsSubmenu" class="submenu">
              <li :class="{ active: currentMenu === 'projects-list' }" @click="switchMenu('projects-list')">
                <span class="icon">📋</span>
                <span>项目列表</span>
              </li>
              <li :class="{ active: currentMenu === 'projects-overview' }" @click="switchMenu('projects-overview')">
                <span class="icon">📈</span>
                <span>项目概览</span>
              </li>
              <li :class="{ active: currentMenu === 'projects-progress' }" @click="switchMenu('projects-progress')">
                <span class="icon">📊</span>
                <span>项目进度</span>
              </li>
            </ul>
          </transition>

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
          <span class="username">{{ username }} (用户)</span>
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
      <div class="page-content">
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
  </div>
</template>

<script>
import Profile from '../components/admin/Profile.vue'
import Settings from '../components/admin/Settings.vue'
import Projects from '../components/admin/Projects.vue'
import ProjectList from '../components/admin/projects/List.vue'
import ProjectProgress from '../components/admin/projects/Progress.vue'
import ModificationLog from '../components/admin/ModificationLog.vue'
import History from '../components/admin/History.vue'
import UserHome from '../components/user/Home.vue'
import Dashboard from '../components/admin/Dashboard.vue'
import { authAPI } from '../services/api'

export default {
  name: 'UserCenter',
  components: {
    UserHome,
    Profile,
    Settings,
    Projects,
    ProjectList,
    ProjectProgress,
    ModificationLog,
    History,
    Dashboard
  },
  data() {
    return {
      currentMenu: 'index', // 默认页面改为首页
      componentKey: 0,
      username: '用户',
      role: 'user',
      componentLoaded: true,
      showProjectsSubmenu: false, // 控制项目管理子菜单的显示
      showUserMenu: false // 控制用户菜单的显示
    }
  },
  computed: {
    currentComponent() {
      switch(this.currentMenu) {
        case 'index':
          return UserHome
        case 'dashboard':
          return Dashboard
        case 'profile':
          return Profile
        case 'settings':
          return Settings
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
          return UserHome
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
          this.username = res.data.username || '未知用户';
        } else {
          this.username = '未知用户';
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.username = '未知用户';
      }
    }
  },
  mounted() {
    this.fetchUserInfo();
  }
}
</script>

<style scoped>
.user-container {
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
  flex-shrink: 0;
  position: relative;
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
  min-width: 0;
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
  background-color: #00B4A0;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.logout-btn:hover {
  background-color: #009380;
  transform: translateY(-2px);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 70px;
  }
  
  .sidebar-logo h2,
  .sidebar-nav span:not(.icon),
  .submenu span {
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
  
  .submenu li {
    padding: 12px 0;
    justify-content: center;
  }
  
  .page-content {
    padding: 10px;
  }
}
</style>