import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('user.token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    // 只在非登录请求时处理 401 错误，避免影响登录流程
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      // 清除用户相关的存储
      const keys = ['user.token', 'user.uid', 'user.username', 'user.email', 'user.isActive', 'user.isSuperuser', 'user.exp']
      keys.forEach(key => localStorage.removeItem(key))

      // 只有在当前不在登录页时才重定向
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// 健康检查API
function healthCheck() {
  return apiClient.get('/health')
}

function getRoot() {
  return apiClient.get('/')
}

// 认证相关API
function login(username: string, password: string) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return apiClient.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

function register(username: string, email: string, password: string) {
  return apiClient.post('/auth/register', {
    username,
    email,
    password
  })
}

function getCurrentUser() {
  return apiClient.get('/auth/me')
}

// 模型管理相关API
function getModels(enabledOnly: boolean = false) {
  return apiClient.get('/models', { params: { enabled_only: enabledOnly } })
}

function getModel(id: number) {
  return apiClient.get(`/models/${id}`)
}

function createModel(data: any) {
  return apiClient.post('/models', data)
}

function updateModel(id: number, data: any) {
  return apiClient.put(`/models/${id}`, data)
}

function setDefaultModel(id: number) {
  return apiClient.put(`/models/${id}/default`)
}

function deleteModel(id: number) {
  return apiClient.delete(`/models/${id}`)
}

// 监控数据源相关API
function getDatasources(enabledOnly: boolean = false) {
  return apiClient.get('/datasources', { params: { enabled_only: enabledOnly } })
}

function getDatasource(id: number) {
  return apiClient.get(`/datasources/${id}`)
}

function createDatasource(data: any) {
  return apiClient.post('/datasources', data)
}

function updateDatasource(id: number, data: any) {
  return apiClient.put(`/datasources/${id}`, data)
}

function deleteDatasource(id: number) {
  return apiClient.delete(`/datasources/${id}`)
}

function testDatasourceConnection(data: any) {
  return apiClient.post('/datasources/test', data)
}

// 日志管理相关API
function getLogSources(enabledOnly: boolean = false) {
  return apiClient.get('/logs', { params: { enabled_only: enabledOnly } })
}

function getLogSource(id: number) {
  return apiClient.get(`/logs/${id}`)
}

function createLogSource(data: any) {
  return apiClient.post('/logs', data)
}

function updateLogSource(id: number, data: any) {
  return apiClient.put(`/logs/${id}`, data)
}

function deleteLogSource(id: number) {
  return apiClient.delete(`/logs/${id}`)
}

function testLogSourceConnection(data: any) {
  return apiClient.post('/logs/test', data)
}

export const api = {
  healthCheck,
  getRoot,
  login,
  register,
  getCurrentUser,
  getModels,
  getModel,
  createModel,
  updateModel,
  setDefaultModel,
  deleteModel,
  getDatasources,
  getDatasource,
  createDatasource,
  updateDatasource,
  deleteDatasource,
  testDatasourceConnection,
  getLogSources,
  getLogSource,
  createLogSource,
  updateLogSource,
  deleteLogSource,
  testLogSourceConnection
}