// 测试脚本：验证登录API连接

/**
 * 测试登录API
 */
async function testLoginAPI() {
  console.log('正在测试登录API...');
  try {
    // 使用后端提供的测试用户账号
    const loginData = {
      email: 'test_user',  // 后端支持的测试用户名
      password: 'password123'  // 对应的测试密码
    };
    
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(loginData)
    });
    
    console.log('登录请求状态码:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ 登录API调用成功！返回数据:', data);
      
      // 检查返回的数据结构
      if (data.success && data.data && data.data.tokens) {
        console.log('✅ 登录成功，获取到访问令牌:', data.data.tokens.access_token.substring(0, 20) + '...');
        return { success: true, token: data.data.tokens.access_token };
      } else {
        console.error('❌ 登录API返回格式不符合预期:', data);
        return { success: false, error: '返回格式不正确' };
      }
    } else {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ 登录API调用失败:', { status: response.status, data: errorData });
      return { success: false, error: `状态码: ${response.status}`, data: errorData };
    }
  } catch (error) {
    console.error('❌ 登录API调用异常:', error);
    return { success: false, error: error.message };
  }
}

/**
 * 测试错误登录场景（错误密码）
 */
async function testLoginError() {
  console.log('\n正在测试错误登录场景...');
  try {
    const invalidLoginData = {
      email: 'test_user',
      password: 'wrongpassword'  // 错误密码
    };
    
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(invalidLoginData)
    });
    
    console.log('错误登录请求状态码:', response.status);
    
    // 错误登录应该返回401或400状态码
    if (response.status === 401 || response.status === 400) {
      const data = await response.json();
      console.log('✅ 错误登录处理正确，返回预期错误:', data);
      return true;
    } else {
      console.error('❌ 错误登录处理异常，状态码不符合预期:', response.status);
      return false;
    }
  } catch (error) {
    console.error('❌ 错误登录测试异常:', error);
    return false;
  }
}

/**
 * 运行所有登录相关测试
 */
async function runLoginTests() {
  console.log('开始测试登录API连接...');
  console.log('====================================');
  
  const loginResult = await testLoginAPI();
  const errorTestResult = await testLoginError();
  
  console.log('\n====================================');
  console.log('登录API测试完成！');
  
  if (loginResult.success && errorTestResult) {
    console.log('🎉 所有登录API测试通过！');
    return { success: true, token: loginResult.token };
  } else {
    console.log('❌ 部分登录API测试失败，请检查配置。');
    return { success: false };
  }
}

// 运行测试
runLoginTests();

export { testLoginAPI, testLoginError, runLoginTests };
