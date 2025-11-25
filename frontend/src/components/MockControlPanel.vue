<template>
  <div class="mock-control-panel">
    <div class="panel-header">
      <h3 class="text-lg font-semibold text-gray-800">Mock数据管理面板</h3>
      <p class="text-sm text-gray-600 mt-1">开发环境下控制和测试API响应</p>
    </div>

    <!-- 响应控制 -->
    <div class="control-section">
      <h4 class="section-title">响应控制</h4>
      <div class="control-grid">
        <div class="control-item">
          <label class="control-label">响应场景</label>
          <select v-model="currentScenario" @change="updateScenario" class="control-select">
            <option value="normal">正常响应</option>
            <option value="slow">慢响应</option>
            <option value="error">错误响应</option>
            <option value="network">网络错误</option>
            <option value="offline">离线模式</option>
          </select>
        </div>
        
        <div class="control-item">
          <label class="control-label">响应延迟 (ms)</label>
          <input 
            v-model.number="responseDelay" 
            @change="updateDelay"
            type="number" 
            min="0" 
            max="5000" 
            class="control-input"
          />
        </div>
      </div>
      
      <div class="scenario-info">
        <div class="status-badge" :class="currentScenario">
          {{ getScenarioDescription() }}
        </div>
      </div>
    </div>

    <!-- 用户状态 -->
    <div class="control-section">
      <h4 class="section-title">用户状态</h4>
      <div class="user-actions">
        <button @click="generateRandomUser" class="btn btn-secondary">
          生成随机用户
        </button>
        <button @click="clearUser" class="btn btn-secondary">
          清除用户
        </button>
        <button @click="resetAllData" class="btn btn-warning">
          重置所有数据
        </button>
      </div>
      
      <div v-if="mockUser" class="user-info">
        <div class="user-avatar">
          <img :src="mockUser.avatar" :alt="mockUser.name" class="avatar-img" />
        </div>
        <div class="user-details">
          <h5 class="font-medium">{{ mockUser.name }}</h5>
          <p class="text-sm text-gray-600">{{ mockUser.email }}</p>
          <div class="user-stats">
            <span class="stat-item">识别: {{ mockUser.stats.total_recognitions }}</span>
            <span class="stat-item">收藏: {{ mockUser.stats.total_favorites }}</span>
            <span class="stat-item">提问: {{ mockUser.stats.total_questions }}</span>
          </div>
        </div>
      </div>
      
      <div v-else class="no-user">
        <p class="text-gray-500">未设置模拟用户</p>
      </div>
    </div>

    <!-- API测试面板 -->
    <div class="control-section">
      <h4 class="section-title">API测试</h4>
      <div class="api-tests">
        <div class="test-group">
          <h5 class="test-title">用户认证</h5>
          <div class="test-buttons">
            <button @click="testLogin" class="btn btn-small">登录测试</button>
            <button @click="testRegister" class="btn btn-small">注册测试</button>
            <button @click="testRefreshToken" class="btn btn-small">刷新Token</button>
          </div>
        </div>
        
        <div class="test-group">
          <h5 class="test-title">碑文识别</h5>
          <div class="test-buttons">
            <button @click="testRecognitionHistory" class="btn btn-small">获取历史</button>
            <button @click="testAIInterpretation" class="btn btn-small">AI阐释</button>
          </div>
        </div>
        
        <div class="test-group">
          <h5 class="test-title">知识库</h5>
          <div class="test-buttons">
            <button @click="testGetArticles" class="btn btn-small">获取文章</button>
            <button @click="testGetArticleDetail" class="btn btn-small">文章详情</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试结果 -->
    <div v-if="testResults.length > 0" class="control-section">
      <h4 class="section-title">测试结果</h4>
      <div class="test-results">
        <div 
          v-for="result in testResults.slice(-5)" 
          :key="result.id"
          class="test-result"
          :class="{ 'success': result.success, 'error': !result.success }"
        >
          <div class="result-header">
            <span class="result-title">{{ result.title }}</span>
            <span class="result-time">{{ formatTime(result.timestamp) }}</span>
          </div>
          <div class="result-content">
            <div class="result-status">
              {{ result.success ? '✅ 成功' : '❌ 失败' }}
            </div>
            <div v-if="result.data" class="result-data">
              <pre>{{ JSON.stringify(result.data, null, 2) }}</pre>
            </div>
            <div v-if="result.error" class="result-error">
              {{ result.error }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据统计 -->
    <div class="control-section">
      <h4 class="section-title">Mock数据统计</h4>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ mockDataCounts.recognitionRecords }}</div>
          <div class="stat-label">识别记录</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ mockDataCounts.articles }}</div>
          <div class="stat-label">知识库文章</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ mockDataCounts.favorites }}</div>
          <div class="stat-label">收藏项目</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ mockDataCounts.notifications }}</div>
          <div class="stat-label">通知消息</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { 
  getMockUser,
  setMockUser,
  clearMockUser,
  resetMockData,
  setResponseScenario,
  setResponseDelay,
  getActiveScenario,
  mockLogin,
  mockRegister,
  mockRefreshToken,
  mockGetRecognitionHistory,
  mockGetAIInterpretation,
  mockGetArticles,
  mockGetArticleDetail
} from '../mock/mockApi.js';

// 响应式数据
const currentScenario = ref('normal');
const responseDelay = ref(500);
const mockUser = ref(null);
const testResults = ref([]);

const mockDataCounts = reactive({
  recognitionRecords: 0,
  articles: 0,
  favorites: 0,
  notifications: 0
});

// 方法
const updateScenario = () => {
  setResponseScenario(currentScenario.value);
  addTestResult('设置响应场景', true, { scenario: currentScenario.value });
};

const updateDelay = () => {
  setResponseDelay(responseDelay.value);
  addTestResult('设置响应延迟', true, { delay: responseDelay.value });
};

const generateRandomUser = () => {
  const user = setMockUser();
  mockUser.value = user;
  addTestResult('生成随机用户', true, user);
};

const clearUser = () => {
  clearMockUser();
  mockUser.value = null;
  addTestResult('清除用户', true, null);
};

const resetAllData = () => {
  resetMockData();
  mockUser.value = getMockUser();
  addTestResult('重置所有数据', true, null);
};

const getScenarioDescription = () => {
  const descriptions = {
    normal: '正常响应 - 标准API响应速度',
    slow: '慢响应 - 模拟复杂查询情况',
    error: '错误响应 - 模拟服务器错误',
    network: '网络错误 - 模拟网络连接问题',
    offline: '离线模式 - 模拟无网络状态'
  };
  return descriptions[currentScenario.value] || '未知场景';
};

const addTestResult = (title, success, data, error = null) => {
  testResults.value.push({
    id: Date.now() + Math.random(),
    title,
    success,
    data,
    error,
    timestamp: new Date()
  });
  
  // 限制结果显示数量
  if (testResults.value.length > 20) {
    testResults.value.shift();
  }
};

const formatTime = (timestamp) => {
  return timestamp.toLocaleTimeString();
};

// API测试方法
const testLogin = async () => {
  try {
    const result = await mockLogin({
      email: 'test@example.com',
      password: '123456'
    });
    addTestResult('登录测试', true, result.data);
    mockUser.value = result.data.user;
  } catch (error) {
    addTestResult('登录测试', false, null, error.message);
  }
};

const testRegister = async () => {
  try {
    const result = await mockRegister({
      name: '测试用户',
      email: `test${Date.now()}@example.com`,
      password: '123456'
    });
    addTestResult('注册测试', true, result.data);
  } catch (error) {
    addTestResult('注册测试', false, null, error.message);
  }
};

const testRefreshToken = async () => {
  try {
    const result = await mockRefreshToken();
    addTestResult('刷新Token', true, result.data);
  } catch (error) {
    addTestResult('刷新Token', false, null, error.message);
  }
};

const testRecognitionHistory = async () => {
  try {
    const result = await mockGetRecognitionHistory({ page: 1, perPage: 10 });
    addTestResult('获取识别历史', true, result.data);
  } catch (error) {
    addTestResult('获取识别历史', false, null, error.message);
  }
};

const testAIInterpretation = async () => {
  try {
    const result = await mockGetAIInterpretation('test_recognition_id');
    addTestResult('AI阐释测试', true, result.data);
  } catch (error) {
    addTestResult('AI阐释测试', false, null, error.message);
  }
};

const testGetArticles = async () => {
  try {
    const result = await mockGetArticles({ page: 1, perPage: 5 });
    addTestResult('获取文章列表', true, result.data);
  } catch (error) {
    addTestResult('获取文章列表', false, null, error.message);
  }
};

const testGetArticleDetail = async () => {
  try {
    const result = await mockGetArticleDetail(100);
    addTestResult('获取文章详情', true, result.data);
  } catch (error) {
    addTestResult('获取文章详情', false, null, error.message);
  }
};

// 初始化
onMounted(() => {
  mockUser.value = getMockUser();
  const scenario = getActiveScenario();
  currentScenario.value = scenario === RESPONSE_SCENARIOS.normal ? 'normal' : 'slow';
  
  // 更新统计数据（这里需要从mockApi获取实际数据）
  mockDataCounts.recognitionRecords = 25;
  mockDataCounts.articles = 15;
  mockDataCounts.favorites = 18;
  mockDataCounts.notifications = 12;
});
</script>

<style scoped>
.mock-control-panel {
  @apply max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-lg;
}

.panel-header {
  @apply mb-6 border-b border-gray-200 pb-4;
}

.control-section {
  @apply mb-6 p-4 border border-gray-200 rounded-lg;
}

.section-title {
  @apply text-md font-semibold text-gray-800 mb-4;
}

.control-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4 mb-4;
}

.control-item {
  @apply flex flex-col space-y-2;
}

.control-label {
  @apply text-sm font-medium text-gray-700;
}

.control-select, .control-input {
  @apply px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.scenario-info {
  @apply mt-4;
}

.status-badge {
  @apply inline-block px-3 py-1 rounded-full text-sm font-medium;
}

.status-badge.normal {
  @apply bg-green-100 text-green-800;
}

.status-badge.slow {
  @apply bg-yellow-100 text-yellow-800;
}

.status-badge.error {
  @apply bg-red-100 text-red-800;
}

.status-badge.network {
  @apply bg-orange-100 text-orange-800;
}

.status-badge.offline {
  @apply bg-gray-100 text-gray-800;
}

.user-actions {
  @apply flex flex-wrap gap-2 mb-4;
}

.btn {
  @apply px-4 py-2 rounded-md font-medium transition-colors;
}

.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
}

.btn-warning {
  @apply bg-orange-200 text-orange-800 hover:bg-orange-300;
}

.btn-small {
  @apply px-3 py-1 text-sm;
}

.user-info {
  @apply flex items-start space-x-4 p-4 bg-gray-50 rounded-lg;
}

.user-avatar {
  @apply flex-shrink-0;
}

.avatar-img {
  @apply w-12 h-12 rounded-full object-cover;
}

.user-details {
  @apply flex-1;
}

.user-stats {
  @apply flex flex-wrap gap-4 mt-2 text-xs text-gray-600;
}

.stat-item {
  @apply bg-white px-2 py-1 rounded;
}

.no-user {
  @apply text-center py-4 text-gray-500;
}

.api-tests {
  @apply grid grid-cols-1 md:grid-cols-3 gap-4;
}

.test-group {
  @apply border border-gray-200 rounded-lg p-3;
}

.test-title {
  @apply font-medium text-gray-700 mb-2;
}

.test-buttons {
  @apply flex flex-wrap gap-1;
}

.test-results {
  @apply space-y-3 max-h-64 overflow-y-auto;
}

.test-result {
  @apply border rounded-lg p-3;
}

.test-result.success {
  @apply border-green-200 bg-green-50;
}

.test-result.error {
  @apply border-red-200 bg-red-50;
}

.result-header {
  @apply flex justify-between items-center mb-2;
}

.result-title {
  @apply font-medium;
}

.result-time {
  @apply text-xs text-gray-500;
}

.result-content {
  @apply space-y-2;
}

.result-data {
  @apply bg-white p-2 rounded border text-xs overflow-x-auto;
}

.result-error {
  @apply text-red-700 text-sm;
}

.stats-grid {
  @apply grid grid-cols-2 md:grid-cols-4 gap-4;
}

.stat-card {
  @apply text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg;
}

.stat-number {
  @apply text-2xl font-bold text-indigo-600;
}

.stat-label {
  @apply text-sm text-indigo-800 mt-1;
}
</style>