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
    const token = localStorage.getItem('access_token')
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
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
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

export const api = {
  healthCheck,
  getRoot,
  login,
  register,
  getCurrentUser
}