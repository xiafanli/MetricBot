import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Dashboard from '@/views/Dashboard.vue'

describe('Dashboard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders properly', () => {
    const wrapper = mount(Dashboard)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays alert statistics', () => {
    const wrapper = mount(Dashboard)
    
    expect(wrapper.find('.stats-row').exists()).toBe(true)
    expect(wrapper.findAll('.stat-card').length).toBe(4)
  })

  it('shows critical alerts card', () => {
    const wrapper = mount(Dashboard)
    
    const criticalCard = wrapper.find('.stat-card.critical')
    expect(criticalCard.exists()).toBe(true)
    expect(criticalCard.find('.stat-label').text()).toContain('严重告警')
  })

  it('shows warning alerts card', () => {
    const wrapper = mount(Dashboard)
    
    const warningCard = wrapper.find('.stat-card.warning')
    expect(warningCard.exists()).toBe(true)
    expect(warningCard.find('.stat-label').text()).toContain('警告告警')
  })

  it('shows info alerts card', () => {
    const wrapper = mount(Dashboard)
    
    const infoCard = wrapper.find('.stat-card.info')
    expect(infoCard.exists()).toBe(true)
    expect(infoCard.find('.stat-label').text()).toContain('信息告警')
  })

  it('shows total alerts card', () => {
    const wrapper = mount(Dashboard)
    
    const totalCard = wrapper.find('.stat-card.total')
    expect(totalCard.exists()).toBe(true)
    expect(totalCard.find('.stat-label').text()).toContain('今日告警')
  })
})
