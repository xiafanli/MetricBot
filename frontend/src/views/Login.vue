<template>
  <div class="login-container">
    <div class="login-content cyber-card">
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
                      <stop offset="0%" style="stop-color:#0088ff"/>
                      <stop offset="50%" style="stop-color:#9900ff"/>
                      <stop offset="100%" style="stop-color:#e60073"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
            </div>
            <h1 class="brand-title neon-glow">Metric Bot</h1>
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
                  class="login-btn cyber-button" 
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

        await new Promise(resolve => setTimeout(resolve, 100))

        if (userStore.isLoggedIn) {
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
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  position: relative;
  overflow: hidden;
}

.login-content {
  display: flex;
  width: 950px;
  max-width: 95vw;
  height: 580px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  position: relative;
  z-index: 1;
}

.brand-panel {
  flex: 1;
  background: linear-gradient(135deg, rgba(0, 136, 255, 0.03) 0%, rgba(153, 0, 255, 0.03) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid var(--border-light);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: var(--gradient-neon);
  }
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
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.logo-icon {
  width: 120px;
  height: 120px;
  filter: drop-shadow(0 0 20px rgba(0, 136, 255, 0.5));
}

.brand-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: var(--gradient-neon);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.brand-subtitle {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
  letter-spacing: 1px;
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
  color: var(--neon-blue);
  font-size: 10px;
}

.feature-text {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-secondary);
}

.login-panel {
  flex: 1;
  background: var(--bg-secondary);
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
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--neon-blue);
  background: rgba(0, 136, 255, 0.1);
  padding: 5px 14px;
  border: 1px solid var(--neon-blue);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 18px;
}

.login-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.login-desc {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-tertiary);
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
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
}

.custom-input {
  :deep(.el-input__wrapper) {
    border-radius: 8px;
    background: var(--bg-primary);
    border: 2px solid var(--border-light);
    box-shadow: none;
    transition: all 0.3s ease;

    &:hover {
      border-color: var(--border-medium);
    }

    &.is-focus {
      border-color: var(--neon-blue);
      box-shadow: 0 0 0 3px rgba(0, 136, 255, 0.1), 0 0 20px rgba(0, 136, 255, 0.2);
    }
  }

  :deep(.el-input__inner) {
    color: var(--text-primary);
    font-family: var(--font-body);
    font-size: 14px;

    &::placeholder {
      color: var(--text-tertiary);
    }
  }
}

.form-actions {
  margin-top: 32px;
}

.login-btn {
  width: 100%;
  height: 48px;
  background: var(--gradient-neon);
  border: none;
  color: white;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 2px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0, 136, 255, 0.5), 0 0 40px rgba(153, 0, 255, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  border-top: 1px solid var(--border-light);
  padding-top: 20px;
}

.demo-creds {
  display: flex;
  gap: 6px;
  align-items: center;
}

.demo-label {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-tertiary);
}

.demo-value {
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--neon-blue);
  font-weight: 600;
}

@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
    height: auto;
  }
  
  .brand-panel {
    border-right: none;
    border-bottom: 1px solid var(--border-light);
  }
  
  .login-inner {
    padding: 30px;
  }
}
</style>
