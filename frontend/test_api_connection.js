// 测试脚本：验证前端与后端API的连接

/**
 * 测试健康检查API
 */
async function testHealthCheck() {
  console.log('正在测试健康检查API...');
  try {
    // 直接使用fetch调用健康检查端点
    const response = await fetch('http://localhost:8000/health', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ 健康检查API连接成功！返回:', data);
      return true;
    } else {
      console.error('❌ 健康检查API返回非成功状态:', response.status);
      return false;
    }
  } catch (error) {
    console.error('❌ 健康检查API调用失败:', error);
    return false;
  }
}

/**
 * 直接测试根路径
 */
async function testRootEndpoint() {
  console.log('正在测试根路径...');
  try {
    const response = await fetch('http://localhost:8000/');
    if (response.ok) {
      const data = await response.json();
      console.log('✅ 根路径访问成功:', data);
      return true;
    } else {
      console.error('❌ 根路径返回非成功状态:', response.status);
      return false;
    }
  } catch (error) {
    console.error('❌ 根路径访问失败:', error);
    return false;
  }
}

/**
 * 运行所有测试
 */
async function runAllTests() {
  console.log('开始测试前端与后端API连接...');
  console.log('====================================');
  
  const healthResult = await testHealthCheck();
  console.log('');
  const rootResult = await testRootEndpoint();
  
  console.log('====================================');
  console.log('测试完成！');
  
  if (healthResult && rootResult) {
    console.log('🎉 所有API连接测试通过！');
    return true;
  } else {
    console.log('❌ 部分API连接测试失败，请检查配置。');
    return false;
  }
}

// 如果直接运行脚本，则执行测试
if (import.meta.url === new URL(import.meta.url).href) {
  runAllTests();
}

export { testHealthCheck, testRootEndpoint, runAllTests };
