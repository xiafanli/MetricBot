<template>
  <div class="login-container">
    <div class="login-content">
      <div class="brand-panel">
        <div class="brand-inner">
          <div class="logo-section">
            <div class="logo-wrapper">
              <div class="logo-icon">
                <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="50" cy="50" r="45" stroke="url(#grad1)" stroke-width="2" fill="none"/>
                  <circle cx="50" cy="50" r="35" stroke="url(#grad1)" stroke-width="1.5" fill="none" opacity="0.7"/>
                  <circle cx="50" cy="50" r="25" stroke="url(#grad1)" stroke-width="1" fill="none" opacity="0.5"/>
                  <path d="M20 50 L40 50 M60 50 L80 50 M50 20 L50 40 M50 60 L50 80" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
                  <circle cx="50" cy="50" r="8" fill="url(#grad1)"/>
                  <defs>
                    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style="stop-color:#ffd700"/>
                      <stop offset="50%" style="stop-color:#ff6b35"/>
                      <stop offset="100%" style="stop-color:#f72585"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            <h1 class="brand-title">Metric Bot</h1>
            <p class="brand-subtitle">监控智能系统</p>
          </div>
          
          <div class="features-list">
            <div class="feature-item">
              <span class="feature-bullet">◆</span>
              <span class="feature-text">自然语言查询</span>
            </div>
            <div class="feature-item">
              <span class="feature-bullet">◆</span>
              <span class="feature-text">高级数据分析</span>
            </div>
            <div class="feature-item">
              <span class="feature-bullet">◆</span>
              <span class="feature-text">实时告警系统</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="login-panel">
        <div class="login-inner">
          <div class="login-header">
            <div class="login-tag">身份验证</div>
            <h2 class="login-title">欢迎回来</h2>
            <p class="login-desc">请输入您的账户信息</p>
          </div>
          
          <div class="login-form">
            <el-form
              ref="loginFormRef"
              class="form-content"
              :model="loginForm"
              :rules="rules"
              @keyup.enter="submitForm"
            >
              <div class="form-group">
                <label class="form-label">用户名</label>
                <div class="input-wrapper">
                  <el-input
                    v-model="loginForm.username"
                    clearable
                    placeholder="请输入用户名"
                    size="large"
                    class="custom-input"
                  ></el-input>
                </div>
              </div>
              
              <div class="form-group">
                <label class="form-label">密码</label>
                <div class="input-wrapper">
                  <el-input
                    v-model="loginForm.password"
                    placeholder="请输入密码"
                    type="password"
                    show-password
                    clearable
                    size="large"
                    class="custom-input"
                  ></el-input>
                </div>
              </div>
              
              <div class="form-actions">
                <el-button 
                  type="primary" 
                  class="login-btn" 
                  :loading="loading"
                  @click="submitForm"
                >
                  <span v-if="!loading">登 录</span>
                  <span v-else>登录中...</span>
                </el-button>
              </div>
            </el-form>
          </div>
          
          <div class="login-footer">
            <div class="demo-creds">
              <span class="demo-label">测试账号：</span>
              <span class="demo-value">admin / admin123</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { toLoginSuccess } from '@/utils/utils'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const loginForm = ref({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const loginFormRef = ref()

const submitForm = async () => {
  loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm.value)
        ElMessage.success('登录成功！')

        // 确保状态完全同步后再跳转
        await new Promise(resolve => setTimeout(resolve, 100))

        // 检查登录状态是否正确设置
        if (userStore.isLoggedIn) {
          // 使用工具函数处理跳转，支持重定向参数
          toLoginSuccess(router)
        } else {
          ElMessage.error('登录状态异常，请重试')
        }
      } catch (error: any) {
        const errorMsg = error.response?.data?.detail || '登录失败'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style lang="less" scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.login-content {
  display: flex;
  width: 950px;
  max-width: 95vw;
  height: 580px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.brand-panel {
  flex: 1;
  background: linear-gradient(180deg, #0f0f0f 0%, #1a1a1a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid rgba(255, 215, 0, 0.1);
}

.brand-inner {
  text-align: center;
  padding: 50px 40px;
}

.logo-section {
  margin-bottom: 40px;
}

.logo-wrapper {
  display: inline-block;
  margin-bottom: 24px;
}

.logo-icon {
  width: 120px;
  height: 120px;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.feature-bullet {
  color: #ffd700;
  font-size: 10px;
}

.feature-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.login-panel {
  flex: 1;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-inner {
  width: 100%;
  padding: 50px 45px;
}

.login-header {
  margin-bottom: 40px;
}

.login-tag {
  display: inline-block;
  font-size: 11px;
  color: #ffd700;
  background: rgba(255, 215, 0, 0.1);
  padding: 5px 14px;
  border: 1px solid rgba(255, 215, 0, 0.3);
  margin-bottom: 18px;
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #fff;
}

.login-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.login-form {
  margin-bottom: 30px;
}

.form-content {
  .el-form-item {
    margin-bottom: 24px;
  }
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
}

.input-wrapper {
  position: relative;
}

.custom-input {
  :deep(.el-input__wrapper) {
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 215, 0, 0.2);
    box-shadow: none;
    transition: all 0.2s;

    &:hover {
      border-color: rgba(255, 107, 53, 0.5);
    }

    &.is-focus {
      border-color: #ffd700;
      box-shadow: 0 0 15px rgba(255, 215, 0, 0.15);
    }
  }

  :deep(.el-input__inner) {
    color: #fff;
    font-size: 14px;

    &::placeholder {
      color: rgba(255, 255, 255, 0.3);
    }
  }
}

.form-actions {
  margin-top: 32px;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b35 50%, #f72585 100%);
  border: none;
  color: #0a0a0a;
  font-weight: 600;
  font-size: 15px;
  border-radius: 8px;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    color: #0a0a0a;
  }

  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  border-top: 1px solid rgba(255, 215, 0, 0.1);
  padding-top: 20px;
}

.demo-creds {
  display: flex;
  gap: 6px;
  align-items: center;
}

.demo-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.demo-value {
  font-size: 13px;
  color: #ffd700;
}
</style>
