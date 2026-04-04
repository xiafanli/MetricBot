import apiClient from './index'

export interface TopologyGenerateRequest {
  name: string
  description?: string
  topology_type: string
  scale: string
  ip_prefix: string
  pushgateway_url: string
  log_path: string
  include_components?: string[]
}

export interface TopologyComponent {
  id: number
  name: string
  type: string
  ip: string | null
  layer: number
}

export interface TopologyRelation {
  id: number
  source_id: number
  target_id: number
  type: string
}

export interface TopologyEnvironment {
  id: number
  name: string
  description: string | null
  is_active: boolean
}

export interface TopologyGenerateSummary {
  total_components: number
  total_relations: number
  topology_type: string
  scale: string
  ip_prefix: string
}

export interface TopologyGenerateResponse {
  environment: TopologyEnvironment
  components: TopologyComponent[]
  relations: TopologyRelation[]
  summary: TopologyGenerateSummary
}

export interface TopologyType {
  type: string
  name: string
  description: string
  layers: string[]
}

export interface TopologyScale {
  scale: string
  name: string
  description: string
  config: Record<string, number>
}

export interface TopologyComponentType {
  type: string
  name: string
  layer: number
  port: number | null
}

export interface TopologyIPCheckResponse {
  ip_prefix: string
  has_conflict: boolean
  existing_count: number
  message: string
}

export interface SimulationEnvironment {
  id: number
  name: string
  description: string | null
  topology_data: Record<string, unknown> | null
  is_active: boolean
  pushgateway_url: string | null
  log_path: string | null
  created_at: string
  updated_at: string
}

export interface SimulationComponent {
  id: number
  env_id: number
  component_type: string
  name: string
  properties: Record<string, unknown> | null
  position_x: number | null
  position_y: number | null
  created_at: string
}

export interface ComponentRelation {
  id: number
  env_id: number
  source_id: number
  target_id: number
  relation_type: string
  created_at: string
}

export const simulatorApi = {
  generateTopology(data: TopologyGenerateRequest): Promise<TopologyGenerateResponse> {
    return apiClient.post('/simulator/environments/generate', data)
  },

  getTopologyTypes(): Promise<TopologyType[]> {
    return apiClient.get('/simulator/topology/types')
  },

  getTopologyScales(): Promise<TopologyScale[]> {
    return apiClient.get('/simulator/topology/scales')
  },

  getTopologyComponents(): Promise<TopologyComponentType[]> {
    return apiClient.get('/simulator/topology/components')
  },

  checkIPPrefix(ipPrefix: string): Promise<TopologyIPCheckResponse> {
    return apiClient.post(`/simulator/topology/check-ip?ip_prefix=${ipPrefix}`)
  },

  getEnvironments(): Promise<SimulationEnvironment[]> {
    return apiClient.get('/simulator/environments')
  },

  getEnvironment(id: number): Promise<SimulationEnvironment> {
    return apiClient.get(`/simulator/environments/${id}`)
  },

  deleteEnvironment(id: number): Promise<void> {
    return apiClient.delete(`/simulator/environments/${id}`)
  },

  activateEnvironment(id: number, data?: { pushgateway_url?: string; log_path?: string }): Promise<{ message: string; id: number }> {
    return apiClient.post(`/simulator/environments/${id}/activate`, data || {})
  },

  deactivateEnvironment(id: number): Promise<{ message: string; id: number }> {
    return apiClient.post(`/simulator/environments/${id}/deactivate`)
  },

  getEnvironmentStatus(id: number): Promise<{
    total_components: number
    active_components: number
    inactive_components: number
    active_faults: number
    components: Array<{
      id: number
      name: string
      type: string
      status: string
      ip_address: string
    }>
    faults: Array<{
      id: number
      component_id: number
      component_name: string | null
      scenario_name: string | null
      start_time: string | null
      end_time: string | null
    }>
  }> {
    return apiClient.get(`/simulator/environments/${id}/status`)
  },

  getComponents(envId: number): Promise<SimulationComponent[]> {
    return apiClient.get(`/simulator/environments/${envId}/components`)
  },

  getRelations(envId: number): Promise<ComponentRelation[]> {
    return apiClient.get(`/simulator/environments/${envId}/relations`)
  },

  syncToHosts(envId: number): Promise<Record<string, unknown>> {
    return apiClient.post(`/simulator/environments/${envId}/sync-to-hosts`)
  },
}
