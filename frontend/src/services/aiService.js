/**
 * AI功能相关API服务
 */

import { http } from '../utils/httpClient';
import { isMockEnabled } from '../utils/mockService.js';
import mockApi from '../mock/mockApi.js';

/**
 * 获取AI阐释
 * @param {Object} interpretationData - 阐释数据
 * @param {string} interpretationData.recognition_id - 识别记录ID
 * @param {Array} interpretationData.aspects - 要分析的方面
 * @param {string} interpretationData.depth - 分析深度
 * @returns {Promise}
 */
export const getInterpretation = async (interpretationData) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式获取AI阐释');
    return await mockApi.mockGetAIInterpretation(interpretationData.recognition_id);
  }
  
  try {
    const response = await http.post('/ai/interpretation', interpretationData);
    return response;
  } catch (error) {
    console.error('❌ AI阐释API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取AI阐释');
    return await mockApi.mockGetAIInterpretation(interpretationData.recognition_id);
  }
};

/**
 * AI对话
 * @param {Object} chatData - 对话数据
 * @param {string} chatData.recognition_id - 识别记录ID
 * @param {string} chatData.message - 用户消息
 * @param {string} chatData.context - 对话上下文
 * @param {string} chatData.conversation_id - 对话ID（可选）
 * @returns {Promise}
 */
export const aiChat = async (chatData) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式进行AI对话');
    return await mockApi.mockChatWithAI(chatData.message, chatData.conversation_id);
  }
  
  try {
    const response = await http.post('/ai/chat', chatData);
    return response;
  } catch (error) {
    console.error('❌ AI对话API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式进行AI对话');
    return await mockApi.mockChatWithAI(chatData.message, chatData.conversation_id);
  }
};

/**
 * 获取相关推荐
 * @param {Object} params - 推荐参数
 * @param {string} params.type - 推荐类型 (inscriptions/articles/questions)
 * @param {number} params.limit - 数量限制
 * @returns {Promise}
 */
export const getRecommendations = async (params) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式获取推荐');
    return await mockApi.mockGetRecommendations(params);
  }
  
  try {
    const response = await http.get('/ai/recommendations', { params });
    return response;
  } catch (error) {
    console.error('❌ 推荐API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取推荐');
    return await mockApi.mockGetRecommendations(params);
  }
};

/**
 * 批量AI阐释
 * @param {Array} recognitionIds - 识别记录ID数组
 * @param {Object} options - 批处理选项
 * @returns {Promise}
 */
export const batchInterpretation = async (recognitionIds, options = {}) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式进行批量阐释');
    return await mockApi.mockBatchInterpretation(recognitionIds);
  }
  
  try {
    // 根据后端文档，没有批量阐释接口，使用循环调用单个阐释
    const results = [];
    for (const id of recognitionIds) {
      const interpretation = await getInterpretation({
        recognition_id: id,
        aspects: options.aspects || ['history', 'culture'],
        depth: options.depth || 'detailed'
      });
      results.push(interpretation);
    }
    return { success: true, data: { results } };
  } catch (error) {
    console.error('❌ 批量阐释API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式进行批量阐释');
    return await mockApi.mockBatchInterpretation(recognitionIds);
  }
};

/**
 * 获取AI问答历史
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.recognition_id - 筛选特定碑文
 * @returns {Promise}
 */
export const getChatHistory = async (params) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式获取对话历史');
    return await mockApi.mockGetChatHistory(params);
  }
  
  try {
    // 根据后端文档，没有专门的对话历史接口，从本地存储获取
    const chatHistory = JSON.parse(localStorage.getItem('aiChatHistory') || '[]');
    return { success: true, data: { chatHistory } };
  } catch (error) {
    console.error('❌ 获取对话历史API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取对话历史');
    return await mockApi.mockGetChatHistory(params);
  }
};

/**
 * 删除对话记录
 * @param {string} conversationId - 对话ID
 * @returns {Promise}
 */
export const deleteChat = async (conversationId) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式删除对话');
    return await mockApi.mockDeleteChat(conversationId);
  }
  
  try {
    // 根据后端文档，没有删除对话接口，从本地存储删除
    const chatHistory = JSON.parse(localStorage.getItem('aiChatHistory') || '[]');
    const filteredHistory = chatHistory.filter(chat => chat.conversation_id !== conversationId);
    localStorage.setItem('aiChatHistory', JSON.stringify(filteredHistory));
    return { success: true, message: '对话删除成功' };
  } catch (error) {
    console.error('❌ 删除对话API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式删除对话');
    return await mockApi.mockDeleteChat(conversationId);
  }
};

/**
 * 导出对话记录
 * @param {string} conversationId - 对话ID
 * @param {string} format - 导出格式 (txt/pdf)
 * @returns {Promise}
 */
export const exportChat = async (conversationId, format = 'txt') => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式导出对话');
    return await mockApi.mockExportChat(conversationId, format);
  }
  
  try {
    // 根据后端文档，没有导出对话接口，从本地存储获取并前端处理
    const chatHistory = JSON.parse(localStorage.getItem('aiChatHistory') || '[]');
    const conversation = chatHistory.find(chat => chat.conversation_id === conversationId);
    
    if (!conversation) {
      throw new Error('对话不存在');
    }
    
    // 前端处理导出逻辑
    return { success: true, data: { conversation, format } };
  } catch (error) {
    console.error('❌ 导出对话API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式导出对话');
    return await mockApi.mockExportChat(conversationId, format);
  }
};

/**
 * 获取AI使用统计
 * @returns {Promise}
 */
export const getAIUsageStats = async () => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式获取AI使用统计');
    return await mockApi.mockGetAIUsageStats();
  }
  
  try {
    // 根据后端文档，没有AI使用统计接口，使用模拟数据
    return { success: true, data: {
      total_interpretations: 0,
      total_chat_messages: 0,
      usage_this_month: 0
    }};
  } catch (error) {
    console.error('❌ 获取AI使用统计API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取AI使用统计');
    return await mockApi.mockGetAIUsageStats();
  }
};

/**
 * 反馈AI回答质量
 * @param {Object} feedbackData - 反馈数据
 * @param {string} feedbackData.response_id - AI回答ID
 * @param {number} feedbackData.rating - 评分 (1-5)
 * @param {string} feedbackData.feedback - 反馈内容
 * @returns {Promise}
 */
export const provideFeedback = async (feedbackData) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式提交反馈');
    return await mockApi.mockProvideFeedback(feedbackData);
  }
  
  try {
    // 根据后端文档，没有反馈接口，保存到本地存储
    const feedbacks = JSON.parse(localStorage.getItem('aiFeedbacks') || '[]');
    feedbacks.push({
      ...feedbackData,
      createdAt: new Date().toISOString()
    });
    localStorage.setItem('aiFeedbacks', JSON.stringify(feedbacks));
    return { success: true, message: '反馈提交成功' };
  } catch (error) {
    console.error('❌ 提交反馈API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式提交反馈');
    return await mockApi.mockProvideFeedback(feedbackData);
  }
};

/**
 * 获取常见问题FAQ
 * @param {Object} params - 查询参数
 * @param {string} params.category - 问题分类
 * @param {string} params.dynasty - 特定朝代
 * @returns {Promise}
 */
export const getFAQ = async (params) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式获取FAQ');
    return await mockApi.mockGetFAQ(params);
  }
  
  try {
    // 根据后端文档，没有FAQ接口，使用模拟数据
    return { success: true, data: { faqs: [] } };
  } catch (error) {
    console.error('❌ 获取FAQAPI调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取FAQ');
    return await mockApi.mockGetFAQ(params);
  }
};

/**
 * 搜索AI知识库
 * @param {Object} searchData - 搜索数据
 * @param {string} searchData.query - 搜索关键词
 * @param {Array} searchData.sources - 搜索来源
 * @param {number} searchData.limit - 结果数量
 * @returns {Promise}
 */
export const searchAIKnowledge = async (searchData) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[AI Service] 使用Mock模式搜索AI知识库');
    return await mockApi.mockSearchAIKnowledge(searchData);
  }
  
  try {
    // 根据后端文档，使用正确的API路径
    const response = await http.get('/knowledge/search', { 
      params: {
        q: searchData.query,
        type: 'all',
        page: 1,
        per_page: searchData.limit || 20
      }
    });
    return response;
  } catch (error) {
    console.error('❌ 搜索AI知识库API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式搜索AI知识库');
    return await mockApi.mockSearchAIKnowledge(searchData);
  }
};

export default {
  getInterpretation,
  aiChat,
  getRecommendations,
  batchInterpretation,
  getChatHistory,
  deleteChat,
  exportChat,
  getAIUsageStats,
  provideFeedback,
  getFAQ,
  searchAIKnowledge
};