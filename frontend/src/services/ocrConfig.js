// OCR服务配置管理器
import { configureKandianAPI, getKandianAPIStatus } from './ocrService.js';

class OCRConfigManager {
  constructor() {
    this.storageKey = 'ocr_config';
    this.defaultConfig = {
      // 看典古籍OCR配置
      kandian: {
        apiKey: '',
        baseUrl: 'https://api.kandianguji.com/ocr',
        timeout: 30000,
        retryAttempts: 3,
        rateLimit: {
          requestsPerMinute: 60,
          burstLimit: 10
        }
      },
      
      // OCR服务偏好设置
      preferences: {
        defaultService: 'kandian',
        fallbackServices: ['baidu', 'tesseract'],
        enableLogging: true,
        autoRetry: true,
        confidenceThreshold: 0.8
      },
      
      // 识别参数设置
      recognition: {
        inscription: {
          language: 'ancient_chinese',
          features: ['ancient', 'traditional', 'punctuation', 'layout'],
          confidenceThreshold: 0.8,
          postProcessing: true
        },
        classical: {
          language: 'classical',
          features: ['classical', 'traditional', 'punctuation'],
          confidenceThreshold: 0.75,
          postProcessing: true
        }
      }
    };
    
    this.loadConfig();
  }

  // 加载配置
  loadConfig() {
    try {
      const savedConfig = localStorage.getItem(this.storageKey);
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        this.config = { ...this.defaultConfig, ...parsed };
      } else {
        this.config = { ...this.defaultConfig };
      }
    } catch (error) {
      console.error('加载OCR配置失败:', error);
      this.config = { ...this.defaultConfig };
    }
    
    return this.config;
  }

  // 保存配置
  saveConfig() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.config));
      return true;
    } catch (error) {
      console.error('保存OCR配置失败:', error);
      return false;
    }
  }

  // 获取完整配置
  getConfig() {
    return { ...this.config };
  }

  // 获取看典古籍API配置
  getKandianConfig() {
    return { ...this.config.kandian };
  }

  // 更新看典古籍API配置
  updateKandianConfig(newConfig) {
    this.config.kandian = { ...this.config.kandian, ...newConfig };
    
    // 更新服务配置
    configureKandianAPI({
      apiKey: this.config.kandian.apiKey,
      baseUrl: this.config.kandian.baseUrl,
      timeout: this.config.kandian.timeout
    });
    
    return this.saveConfig();
  }

  // 更新识别偏好设置
  updatePreferences(newPreferences) {
    this.config.preferences = { ...this.config.preferences, ...newPreferences };
    return this.saveConfig();
  }

  // 更新识别参数设置
  updateRecognitionSettings(type, settings) {
    if (this.config.recognition[type]) {
      this.config.recognition[type] = { ...this.config.recognition[type], ...settings };
      return this.saveConfig();
    }
    return false;
  }

  // 获取API状态
  getAPIStatus() {
    const status = getKandianAPIStatus();
    const config = this.config.kandian;
    
    return {
      ...status,
      configured: !!config.apiKey,
      baseUrl: config.baseUrl,
      timeout: config.timeout,
      rateLimit: config.rateLimit
    };
  }

  // 检查配置完整性
  validateConfig() {
    const issues = [];
    
    // 检查看典古籍API配置
    if (!this.config.kandian.apiKey) {
      issues.push('看典古籍API密钥未配置');
    }
    
    if (!this.config.kandian.baseUrl) {
      issues.push('看典古籍API基础URL未配置');
    }
    
    // 检查网络连接配置
    if (this.config.kandian.timeout < 5000) {
      issues.push('API超时时间过短，建议至少5000ms');
    }
    
    if (this.config.kandian.retryAttempts < 1) {
      issues.push('重试次数应至少为1次');
    }
    
    return {
      valid: issues.length === 0,
      issues
    };
  }

  // 重置为默认配置
  resetToDefault() {
    this.config = { ...this.defaultConfig };
    return this.saveConfig();
  }

  // 导出配置（不包含敏感信息）
  exportConfig() {
    const exportConfig = { ...this.config };
    
    // 隐藏API密钥
    if (exportConfig.kandian.apiKey) {
      exportConfig.kandian.apiKey = '***隐藏***';
    }
    
    return exportConfig;
  }

  // 导入配置
  importConfig(configData) {
    try {
      // 验证配置格式
      if (!configData.kandian || !configData.preferences || !configData.recognition) {
        throw new Error('配置格式不正确');
      }
      
      // 保留现有API密钥
      const currentApiKey = this.config.kandian.apiKey;
      if (configData.kandian.apiKey === '***隐藏***') {
        configData.kandian.apiKey = currentApiKey;
      }
      
      this.config = { ...this.defaultConfig, ...configData };
      
      // 更新服务配置
      configureKandianAPI({
        apiKey: this.config.kandian.apiKey,
        baseUrl: this.config.kandian.baseUrl,
        timeout: this.config.kandian.timeout
      });
      
      return this.saveConfig();
    } catch (error) {
      console.error('导入配置失败:', error);
      return false;
    }
  }
}

// 创建单例实例
const ocrConfigManager = new OCRConfigManager();

export default ocrConfigManager;

// 导出便捷方法
export const getOCRConfig = () => ocrConfigManager.getConfig();
export const getKandianAPIConfig = () => ocrConfigManager.getKandianConfig();
export const updateKandianAPIConfig = (config) => ocrConfigManager.updateKandianConfig(config);
export const getOCRAPIStatus = () => ocrConfigManager.getAPIStatus();
export const validateOCRConfig = () => ocrConfigManager.validateConfig();
export const resetOCRConfig = () => ocrConfigManager.resetToDefault();