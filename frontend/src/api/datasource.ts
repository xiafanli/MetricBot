import request from './index'

export interface Datasource {
  id: number
  name: string
  type: string
  url: string
  description: string | null
  is_enabled: boolean
  created_at: string
  updated_at: string | null
}

export interface DatasourceCreate {
  name: string
  type: string
  url: string
  description?: string
  is_enabled?: boolean
}

export interface DatasourceUpdate {
  name?: string
  type?: string
  url?: string
  description?: string
  is_enabled?: boolean
}

export function getDatasources(enabledOnly: boolean = false) {
  return request.get<Datasource[]>('/datasources', {
    params: { enabled_only: enabledOnly }
  })
}

export function getDatasource(id: number) {
  return request.get<Datasource>(`/datasources/${id}`)
}

export function createDatasource(data: DatasourceCreate) {
  return request.post<Datasource>('/datasources', data)
}

export function updateDatasource(id: number, data: DatasourceUpdate) {
  return request.put<Datasource>(`/datasources/${id}`, data)
}

export function deleteDatasource(id: number) {
  return request.delete(`/datasources/${id}`)
}

export function testDatasourceConnection(data: DatasourceCreate) {
  return request.post('/datasources/test', data)
}
