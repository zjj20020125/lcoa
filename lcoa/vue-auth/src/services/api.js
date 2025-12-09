import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理错误
api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.message || 
                   error.message || 
                   '请求失败，请检查网络连接'
    
    // 如果是401错误，清除本地存储的认证信息并跳转到登录页
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('role');
      localStorage.removeItem('currentUser');
      // 如果在浏览器环境中，跳转到登录页
      if (typeof window !== 'undefined' && window.location) {
        window.location.href = '/#/Login';
      }
    }
    
    console.error('API请求错误:', message)
    return Promise.reject(error)
  }
)

// 用户认证接口
export const authAPI = {
  register: (data) => api.post('/register', data),
  login: (data) => api.post('/login', data),
  getMe: () => api.get('/me')
}

// 用户管理接口
export const userAPI = {
  // 获取所有用户
  getAllUsers: () => api.get('/users'),
  // 更新用户角色
  updateUserRole: (userId, role) => api.put(`/users/${userId}/role`, { role })
}

// 数据查询接口
export const dataAPI = {
  // 获取LCOA表所有数据
  getLcoaData: () => api.get('/lcoa'),
  // 获取LCOA表数据条数
  getLcoaCount: () => api.get('/lcoa/count'),
  // 获取LCOA表最大ID
  getLcoaMaxId: () => api.get('/lcoa/max-id'),
  
  // 获取sys_deal表所有数据
  getSysDealData: () => api.get('/sys_nodeal'),
  // 获取sys_deal表数据条数
  getSysDealCount: () => api.get('/sys_nodeal/count'),
  // 获取sys_xiangxi表所有数据
  getSysXiangxiData: () => api.get('/sys_xiangxi'),
  // 获取sys_xiangxi表所有数据
  getSysXiangxiLatest: () => api.get('/sys_xiangxi/latest'),
  // 获取sys_xiangxi表每日统计数据
  getSysXiangxiDailyStats: () => api.get('/sys_xiangxi/daily_stats'),
  // 获取sys_xiangxi表最接近当前时间的日期（月日格式）
  getSysXiangxiLatestDate: () => api.get('/sys_xiangxi/latest_date'),
  
  // 获取sys_club表所有数据
  getSysClubData: () => api.get('/sys_club'),
  // 获取sys_club表最接近当前时间的数据
  getSysClubLatest: () => api.get('/sys_club/latest'),
  // 获取sys_club表最接近当前时间的日期（月日格式）
  getSysClubLatestDate: () => api.get('/sys_club/latest_date')
}