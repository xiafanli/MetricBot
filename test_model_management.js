const axios = require('axios');
const fs = require('fs');

// 测试配置
const API_BASE_URL = 'http://localhost:8000/api/v1';
const TEST_MODEL_NAME = '测试模型 ' + Date.now();
const TEST_MODEL_PROVIDER = 'OpenAI';
const TEST_MODEL_BASE_MODEL = 'gpt-4-test';

// 测试结果存储
const testResults = {
  passed: 0,
  failed: 0,
  errors: []
};

// 登录配置 - 使用默认管理员凭据
const LOGIN_CREDENTIALS = {
  username: 'admin',
  password: 'admin123'
};

// 记录测试结果
function logTest(name, success, error = null) {
  if (success) {
    console.log(`✅ ${name}: 通过`);
    testResults.passed++;
  } else {
    console.log(`❌ ${name}: 失败 - ${error || '未知错误'}`);
    testResults.failed++;
    testResults.errors.push({ name, error: error || '未知错误' });
  }
}

// 登录函数
async function login() {
  try {
    console.log('\n=== 登录认证 ===');
    const formData = new URLSearchParams();
    formData.append('username', LOGIN_CREDENTIALS.username);
    formData.append('password', LOGIN_CREDENTIALS.password);

    const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const token = response.data.access_token;
    if (!token) {
      throw new Error('未获取到认证token');
    }

    // 设置axios默认请求头
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    console.log('✅ 登录成功');
    return token;
  } catch (error) {
    logTest('登录', false, error.message);
    throw error;
  }
}

// 测试1: 获取模型列表
async function testGetModels() {
  try {
    console.log('\n=== 测试1: 获取模型列表 ===');
    const response = await axios.get(`${API_BASE_URL}/models`);
    console.log('✅ 获取模型列表成功');
    console.log('模型数量:', response.data.length);
    return response.data;
  } catch (error) {
    logTest('获取模型列表', false, error.message);
    return [];
  }
}

// 测试2: 创建新模型
async function testCreateModel() {
  try {
    console.log('\n=== 测试2: 创建新模型 ===');
    const modelData = {
      name: TEST_MODEL_NAME,
      provider: TEST_MODEL_PROVIDER,
      base_model: TEST_MODEL_BASE_MODEL,
      protocol: 'openai',
      api_key: 'test_key_' + Date.now(),
      api_domain: 'https://api.openai.com/v1',
      is_enabled: true,
      is_default: false
    };

    const response = await axios.post(`${API_BASE_URL}/models`, modelData);
    console.log('✅ 创建模型成功');
    console.log('模型ID:', response.data.id);
    return response.data;
  } catch (error) {
    logTest('创建模型', false, error.message);
    return null;
  }
}

// 测试3: 更新模型
async function testUpdateModel(modelId) {
  try {
    console.log('\n=== 测试3: 更新模型 ===');
    const updateData = {
      name: TEST_MODEL_NAME + ' - 已更新',
      is_enabled: false
    };

    const response = await axios.put(`${API_BASE_URL}/models/${modelId}`, updateData);
    console.log('✅ 更新模型成功');
    console.log('更新后的名称:', response.data.name);
    return response.data;
  } catch (error) {
    logTest('更新模型', false, error.message);
    return null;
  }
}

// 测试4: 设置默认模型
async function testSetDefaultModel(modelId) {
  try {
    console.log('\n=== 测试4: 设置默认模型 ===');
    const response = await axios.put(`${API_BASE_URL}/models/${modelId}/default`);
    console.log('✅ 设置默认模型成功');
    console.log('默认模型ID:', response.data.id);
    return response.data;
  } catch (error) {
    logTest('设置默认模型', false, error.message);
    return null;
  }
}

// 测试5: 删除模型
async function testDeleteModel(modelId) {
  try {
    console.log('\n=== 测试5: 删除模型 ===');
    await axios.delete(`${API_BASE_URL}/models/${modelId}`);
    console.log('✅ 删除模型成功');
    return true;
  } catch (error) {
    logTest('删除模型', false, error.message);
    return false;
  }
}

// 运行所有测试
async function runTests() {
  console.log('🚀 开始模型管理功能自动测试...\n');

  try {
    // 先登录
    await login();

    // 测试1: 获取模型列表
    const models = await testGetModels();

    // 测试2: 创建新模型
    const createdModel = await testCreateModel();
    if (!createdModel) return;

    const createdModelId = createdModel.id;

    // 测试3: 更新模型
    await testUpdateModel(createdModelId);

    // 测试4: 设置默认模型
    await testSetDefaultModel(createdModelId);

    // 测试5: 删除模型
    await testDeleteModel(createdModelId);

  } catch (error) {
    console.error('测试过程中发生错误:', error);
  } finally {
    // 输出测试结果
    console.log('\n📊 测试结果总结:');
    console.log(`✅ 通过: ${testResults.passed}`);
    console.log(`❌ 失败: ${testResults.failed}`);

    if (testResults.errors.length > 0) {
      console.log('\n❌ 错误详情:');
      testResults.errors.forEach(error => {
        console.log(`- ${error.name}: ${error.error}`);
      });
    }

    // 保存测试结果到文件
    const resultData = {
      timestamp: new Date().toISOString(),
      results: testResults,
      errors: testResults.errors
    };

    fs.writeFileSync('test_results.json', JSON.stringify(resultData, null, 2));
    console.log('\n📄 测试结果已保存到 test_results.json');
  }
}

// 检查是否安装了axios
async function checkDependencies() {
  try {
    await axios.get('http://localhost:8000/api/v1/health');
    console.log('✅ 后端服务正常');
    runTests();
  } catch (error) {
    console.error('❌ 后端服务未启动或不可访问');
    console.error('请确保后端服务已启动在 http://localhost:8000');
  }
}

// 检查Node.js环境
if (require.main === module) {
  checkDependencies();
}

module.exports = { runTests, testGetModels, testCreateModel, testUpdateModel, testSetDefaultModel, testDeleteModel };