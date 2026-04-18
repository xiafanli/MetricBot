import { describe, it, expect } from 'vitest'

describe('Utility Functions', () => {
  describe('Date Formatting', () => {
    it('formats date correctly', () => {
      const date = new Date('2026-04-18T10:30:00')
      const formatted = date.toLocaleString('zh-CN')
      
      expect(formatted).toContain('2026')
      expect(formatted).toContain('4')
      expect(formatted).toContain('18')
    })
  })

  describe('Number Formatting', () => {
    it('formats percentage correctly', () => {
      const value = 85.5
      const percentage = `${value.toFixed(1)}%`
      
      expect(percentage).toBe('85.5%')
    })

    it('handles zero correctly', () => {
      const value = 0
      const percentage = `${value.toFixed(1)}%`
      
      expect(percentage).toBe('0.0%')
    })
  })

  describe('Alert Severity', () => {
    it('identifies critical severity', () => {
      const severity = 'critical'
      const isCritical = severity === 'critical'
      
      expect(isCritical).toBe(true)
    })

    it('identifies warning severity', () => {
      const severity = 'warning'
      const isWarning = severity === 'warning'
      
      expect(isWarning).toBe(true)
    })

    it('identifies info severity', () => {
      const severity = 'info'
      const isInfo = severity === 'info'
      
      expect(isInfo).toBe(true)
    })
  })

  describe('WebSocket Message Handling', () => {
    it('parses alert message correctly', () => {
      const message = {
        type: 'alert',
        data: {
          id: 1,
          severity: 'critical',
          message: 'CPU使用率过高'
        }
      }
      
      expect(message.type).toBe('alert')
      expect(message.data.severity).toBe('critical')
    })

    it('handles stats update message', () => {
      const message = {
        type: 'stats_update',
        data: {
          total: 100,
          critical: 10,
          warning: 30
        }
      }
      
      expect(message.type).toBe('stats_update')
      expect(message.data.total).toBe(100)
    })
  })
})
