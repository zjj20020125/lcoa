import { createRouter, createWebHistory } from 'vue-router'
import login from '../components/Login.vue'
import register from '../components/Register.vue'
import Index from '../components/Index.vue' // 导入首页组件
import UserCenter from '../views/UserCenter.vue'  // 导入用户中心组件
import AdminCenter from '../views/AdminCenter.vue'  // 导入管理员中心组件
import ProjectDetail from '../components/admin/projects/Detail.vue' // 导入项目详情组件

const routes = [
  {
    path: '/',
    component: Index  // 默认路径指向首页
  },
  {
    path: '/Login',
    component: login
  },
  {
    path: '/Register',
    component: register
  },
  {
    path: '/user-center',  // 添加用户中心路由
    component: UserCenter,
    meta: {
      requiresAuth: true  // 标记为需要登录
    }
  },
  {
    path: '/admin',  // 添加管理员中心路由
    component: AdminCenter,
    meta: {
      requiresAuth: true  // 标记为需要登录
    }
  },
  {
    path: '/admin/projects/detail/:id',  // 添加项目详情路由
    component: ProjectDetail,
    meta: {
      requiresAuth: true  // 标记为需要登录
    },
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 添加路由守卫，验证登录状态
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否有登录信息(检查token)
    const token = localStorage.getItem('token')
    if (token) {
      next()
    } else {
      next('/Login')
    }
  } else {
    // 如果已登录且试图访问登录页，则重定向到相应的中心页面
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('role')
    
    if (token && (to.path === '/Login' || to.path === '/')) {
      if (role === 'admin') {
        next('/admin')
      } else {
        next('/user-center')
      }
    } else {
      next()
    }
  }
})

export default router