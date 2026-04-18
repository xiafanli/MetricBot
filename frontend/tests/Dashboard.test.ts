import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import Dashboard from '@/views/Dashboard.vue'

global.WebSocket = vi.fn(() => ({
  onopen: null,
  onmessage: null,
  onerror: null,
  onclose: null,
  send: vi.fn(),
  close: vi.fn()
}))

describe('Dashboard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders properly', () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [ElementPlus]
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays alert statistics', () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [ElementPlus]
      }
    })
    
    expect(wrapper.find('.stats-row').exists()).toBe(true)
    expect(wrapper.findAll('.stat-card').length).toBe(4)
  })

  it('shows critical alerts card', () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [ElementPlus]
      }
    })
    
    const criticalCard = wrapper.find('.stat-card.critical')
    expect(criticalCard.exists()).toBe(true)
    expect(criticalCard.find('.stat-label').text()).toContain('严重告警')
  })

  it('shows warning alerts card', () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [ElementPlus]
      }
    })
    
    const warningCard = wrapper.find('.stat-card.warning')
    expect(warningCard.exists()).toBe(true)
    expect(warningCard.find('.stat-label').text()).toContain('警告告警')
  })

  it('shows info alerts card', () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [ElementPlus]
      }
    })
    
    const infoCard = wrapper.find('.stat-card.info')
    expect(infoCard.exists()).toBe(true)
    expect(infoCard.find('.stat-label').text()).toContain('信息告警')
  })

  it('shows total alerts card', () => {
    const wrapper = mount(Dashboard, {
      global: {
        plugins: [ElementPlus]
      }
    })
    
    const totalCard = wrapper.find('.stat-card.total')
    expect(totalCard.exists()).toBe(true)
    expect(totalCard.find('.stat-label').text()).toContain('今日告警')
  })
})
