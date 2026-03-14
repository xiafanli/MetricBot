<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-right">
        <div class="login-logo-icon">
          <span style="font-size: 34px; font-weight: 900; color: #485559">PrometheusBot</span>
        </div>
        <div class="welcome">欢迎使用 PrometheusBot</div>
        <div class="login-form">
          <div class="default-login-tabs">
            <h2 class="title">登录</h2>
            <el-form
              ref="loginFormRef"
              class="form-content_error"
              :model="loginForm"
              :rules="rules"
              @keyup.enter="submitForm"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  clearable
                  placeholder="请输入用户名或邮箱"
                  size="large"
                ></el-input>
              </el-form-item>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  placeholder="请输入密码"
                  type="password"
                  show-password
                  clearable
                  size="large"
                ></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" class="login-btn" @click="submitForm">登录</el-button>
              </el-form-item>
            </el-form>
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

const router = useRouter()
const loginForm = ref({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const loginFormRef = ref()

const submitForm = () => {
  loginFormRef.value.validate((valid: boolean) => {
    if (valid) {
      // 这里暂时只做简单的登录验证，实际项目中应该调用API
      ElMessage.success('登录成功！')
      // 登录成功后跳转到首页
      router.push('/')
    }
  })
}
</script>

<style lang="less" scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;

  .login-content {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;

    .login-right {
      display: flex;
      align-items: center;
      flex-direction: column;
      position: relative;
      background: white;
      padding: 60px 40px;
      border-radius: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);

      .login-logo-icon {
        width: auto;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
      }
      .welcome {
        margin: 8px 0 40px 0;
        font-weight: 400;
        font-size: 16px;
        line-height: 20px;
        color: #646a73;
      }

      .login-form {
        width: 400px;

        .title {
          font-weight: 500;
          font-style: Medium;
          font-size: 24px;
          line-height: 28px;
          margin-bottom: 32px;
          text-align: center;
        }

        .login-btn {
          width: 100%;
          height: 44px;
          font-size: 16px;
          border-radius: 6px;
        }
      }
    }
  }
}
</style>