import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('displays login page', async ({ page }) => {
    await expect(page.locator('h2')).toContainText('登录')
  })

  test('shows error with invalid credentials', async ({ page }) => {
    await page.fill('input[type="text"]', 'invaliduser')
    await page.fill('input[type="password"]', 'wrongpass')
    await page.click('button[type="submit"]')
    
    await expect(page.locator('.el-message--error')).toBeVisible()
  })

  test('redirects to dashboard after successful login', async ({ page }) => {
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL(/.*dashboard/)
    await expect(page.locator('.dashboard-container')).toBeVisible()
  })
})

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    await expect(page).toHaveURL(/.*dashboard/)
  })

  test('displays alert statistics', async ({ page }) => {
    await expect(page.locator('.stats-row')).toBeVisible()
    await expect(page.locator('.stat-card.critical')).toBeVisible()
    await expect(page.locator('.stat-card.warning')).toBeVisible()
    await expect(page.locator('.stat-card.info')).toBeVisible()
  })

  test('shows alert list', async ({ page }) => {
    await expect(page.locator('.alert-table')).toBeVisible()
  })

  test('can refresh alerts', async ({ page }) => {
    await page.click('.card-header .el-button:has-text("刷新")')
    await expect(page.locator('.el-message--success')).toBeVisible()
  })
})

test.describe('Navigation', () => {
  test('can navigate to different pages', async ({ page }) => {
    await page.goto('/')
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    await page.click('text=智能对话')
    await expect(page).toHaveURL(/.*chat/)
    
    await page.click('text=数据源')
    await expect(page).toHaveURL(/.*datasource/)
    
    await page.click('text=模拟器')
    await expect(page).toHaveURL(/.*simulator/)
  })
})
