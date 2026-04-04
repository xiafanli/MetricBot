import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default apiClient

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

// 主机管理相关API
function getHosts(enabledOnly: boolean = false) {
  return apiClient.get('/hosts', { params: { enabled_only: enabledOnly } })
}

function getHost(id: number) {
  return apiClient.get(`/hosts/${id}`)
}

function createHost(data: any) {
  return apiClient.post('/hosts', data)
}

function updateHost(id: number, data: any) {
  return apiClient.put(`/hosts/${id}`, data)
}

function deleteHost(id: number) {
  return apiClient.delete(`/hosts/${id}`)
}

function syncHostsFromPrometheus(data: any) {
  return apiClient.post('/hosts/sync/prometheus', data)
}

// 关系管理相关API
function getHostRelations(hostId: number) {
  return apiClient.get(`/hosts/${hostId}/relations`)
}

function getAllRelations() {
  return apiClient.get('/hosts/relations/all')
}

function createRelation(data: any) {
  return apiClient.post('/hosts/relations', data)
}

function updateRelation(id: number, data: any) {
  return apiClient.put(`/hosts/relations/${id}`, data)
}

function deleteRelation(id: number) {
  return apiClient.delete(`/hosts/relations/${id}`)
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

function getSimulationEnvironments() {
  return apiClient.get('/simulator/environments')
}

function getSimulationEnvironment(id: number) {
  return apiClient.get(`/simulator/environments/${id}`)
}

function createSimulationEnvironment(data: any) {
  return apiClient.post('/simulator/environments', data)
}

function updateSimulationEnvironment(id: number, data: any) {
  return apiClient.put(`/simulator/environments/${id}`, data)
}

function deleteSimulationEnvironment(id: number) {
  return apiClient.delete(`/simulator/environments/${id}`)
}

function activateSimulationEnvironment(id: number, data: any) {
  return apiClient.post(`/simulator/environments/${id}/activate`, data)
}

function deactivateSimulationEnvironment(id: number) {
  return apiClient.post(`/simulator/environments/${id}/deactivate`)
}

function syncEnvironmentToHosts(id: number) {
  return apiClient.post(`/simulator/environments/${id}/sync-to-hosts`)
}

function getComponents(envId: number) {
  return apiClient.get(`/simulator/environments/${envId}/components`)
}

function createComponent(envId: number, data: any) {
  return apiClient.post(`/simulator/environments/${envId}/components`, data)
}

function updateComponent(id: number, data: any) {
  return apiClient.put(`/simulator/components/${id}`, data)
}

function deleteComponent(id: number) {
  return apiClient.delete(`/simulator/components/${id}`)
}

function getSimulatorRelations(envId: number) {
  return apiClient.get(`/simulator/environments/${envId}/relations`)
}

function createSimulatorRelation(envId: number, data: any) {
  return apiClient.post(`/simulator/environments/${envId}/relations`, data)
}

function deleteSimulatorRelation(id: number) {
  return apiClient.delete(`/simulator/relations/${id}`)
}

function getMetricTemplates() {
  return apiClient.get('/simulator/metric-templates')
}

function createMetricTemplate(data: any) {
  return apiClient.post('/simulator/metric-templates', data)
}

function updateMetricTemplate(id: number, data: any) {
  return apiClient.put(`/simulator/metric-templates/${id}`, data)
}

function deleteMetricTemplate(id: number) {
  return apiClient.delete(`/simulator/metric-templates/${id}`)
}

function getLogTemplates() {
  return apiClient.get('/simulator/log-templates')
}

function createLogTemplate(data: any) {
  return apiClient.post('/simulator/log-templates', data)
}

function updateLogTemplate(id: number, data: any) {
  return apiClient.put(`/simulator/log-templates/${id}`, data)
}

function deleteLogTemplate(id: number) {
  return apiClient.delete(`/simulator/log-templates/${id}`)
}

function getFaultScenarios() {
  return apiClient.get('/simulator/fault-scenarios')
}

function createFaultScenario(data: any) {
  return apiClient.post('/simulator/fault-scenarios', data)
}

function updateFaultScenario(id: number, data: any) {
  return apiClient.put(`/simulator/fault-scenarios/${id}`, data)
}

function deleteFaultScenario(id: number) {
  return apiClient.delete(`/simulator/fault-scenarios/${id}`)
}

function triggerFault(id: number, componentId: number) {
  return apiClient.post(`/simulator/fault-scenarios/${id}/trigger`, null, { params: { component_id: componentId } })
}

function getFaultInstances() {
  return apiClient.get('/simulator/fault-instances')
}

function getFaultInstance(id: number) {
  return apiClient.get(`/simulator/fault-instances/${id}`)
}

function getEnvironmentStatus(id: number) {
  return apiClient.get(`/simulator/environments/${id}/status`)
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
  testLogSourceConnection,
  getHosts,
  getHost,
  createHost,
  updateHost,
  deleteHost,
  syncHostsFromPrometheus,
  getHostRelations,
  getAllRelations,
  createRelation,
  updateRelation,
  deleteRelation,
  getSimulationEnvironments,
  getSimulationEnvironment,
  createSimulationEnvironment,
  updateSimulationEnvironment,
  deleteSimulationEnvironment,
  activateSimulationEnvironment,
  deactivateSimulationEnvironment,
  syncEnvironmentToHosts,
  getComponents,
  createComponent,
  updateComponent,
  deleteComponent,
  getSimulatorRelations,
  createSimulatorRelation,
  deleteSimulatorRelation,
  getMetricTemplates,
  createMetricTemplate,
  updateMetricTemplate,
  deleteMetricTemplate,
  getLogTemplates,
  createLogTemplate,
  updateLogTemplate,
  deleteLogTemplate,
  getFaultScenarios,
  createFaultScenario,
  updateFaultScenario,
  deleteFaultScenario,
  triggerFault,
  getFaultInstances,
  getFaultInstance,
  getEnvironmentStatus
}