import request from './index'

export interface AlertRule {
  id: number
  name: string
  description: string | null
  datasource_id: number
  datasource_type: string
  metric_query: string
  condition_type: string
  threshold: number | null
  severity: string
  evaluation_interval: number
  enabled: boolean
  created_at: string
  updated_at: string | null
}

export interface AlertRuleCreate {
  name: string
  description?: string
  datasource_id: number
  datasource_type: string
  metric_query: string
  condition_type?: string
  threshold?: number
  severity?: string
  evaluation_interval?: number
  enabled?: boolean
}

export interface AlertRuleUpdate {
  name?: string
  description?: string
  datasource_id?: number
  datasource_type?: string
  metric_query?: string
  condition_type?: string
  threshold?: number
  severity?: string
  evaluation_interval?: number
  enabled?: boolean
}

export interface Alert {
  id: number
  rule_id: number
  rule_name: string | null
  severity: string
  metric_value: number | null
  threshold: number | null
  message: string | null
  resolved: boolean
  resolved_at: string | null
  datasource_id: number | null
  created_at: string
}

export interface AlertStats {
  total: number
  critical: number
  warning: number
  info: number
  resolved: number
  active: number
}

export interface DiagnosisReport {
  id: number
  alert_id: number
  report: string | null
  created_at: string
}

export interface DiagnosisChatRequest {
  message: string
}

export interface DiagnosisChatResponse {
  id: number
  alert_id: number
  message: string
  created_at: string
}

export interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
}

export function getAlertRules(enabledOnly: boolean = false) {
  return request.get<AlertRule[]>('/alerts/rules', {
    params: { enabled_only: enabledOnly }
  })
}

export function getAlertRule(ruleId: number) {
  return request.get<AlertRule>(`/alerts/rules/${ruleId}`)
}

export function createAlertRule(data: AlertRuleCreate) {
  return request.post<AlertRule>('/alerts/rules', data)
}

export function updateAlertRule(ruleId: number, data: AlertRuleUpdate) {
  return request.put<AlertRule>(`/alerts/rules/${ruleId}`, data)
}

export function deleteAlertRule(ruleId: number) {
  return request.delete(`/alerts/rules/${ruleId}`)
}

export function testAlertRule(ruleId: number, testValue: number) {
  return request.post(`/alerts/rules/${ruleId}/test`, { test_value: testValue })
}

export function getAlerts(params?: { resolved_only?: boolean; active_only?: boolean; limit?: number }) {
  return request.get<Alert[]>('/alerts', { params })
}

export function getAlert(alertId: number) {
  return request.get<Alert>(`/alerts/${alertId}`)
}

export function resolveAlert(alertId: number) {
  return request.put<Alert>(`/alerts/${alertId}/resolve`)
}

export function getAlertStats() {
  return request.get<AlertStats>('/alerts/stats')
}

export function generateDiagnosis(alertId: number) {
  return request.post<DiagnosisReport>(`/alerts/${alertId}/diagnosis`)
}

export function getDiagnosis(alertId: number) {
  return request.get<DiagnosisReport>(`/alerts/${alertId}/diagnosis`)
}

export function diagnosisChat(alertId: number, message: string) {
  return request.post<DiagnosisChatResponse>(`/alerts/${alertId}/chat`, { message })
}

export function getConversations(alertId: number) {
  return request.get<{ messages: ConversationMessage[] }>(`/alerts/${alertId}/conversations`)
}
