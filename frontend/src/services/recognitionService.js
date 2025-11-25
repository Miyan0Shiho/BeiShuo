/**
 * 碑文识别相关API服务
 */

import { http } from '../utils/httpClient';
import { isMockEnabled } from '../utils/mockService.js';
import mockApi from '../mock/mockApi.js';

/**
 * 生成分享令牌
 * @param {string} recognitionId - 识别ID
 * @returns {string} 分享令牌
 */
function generateShareToken(recognitionId) {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 10);
  return `${recognitionId}_${timestamp}_${random}`;
}

/**
 * 上传图片
 * @param {File} imageFile - 图片文件
 * @param {Object} options - 上传选项
 * @param {string} options.filename - 文件名（可选）
 * @returns {Promise}
 */
export const uploadImage = async (imageFile, options = {}) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式上传图片');
    return await mockApi.mockUploadImage();
  }
  
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    if (options.filename) {
      formData.append('filename', options.filename);
    }
    
    const response = await http.upload('/upload/image', formData, {
      onUploadProgress: (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        console.log(`📤 Upload Progress: ${progress}%`);
        // 这里可以触发上传进度事件
      }
    });
    
    return response;
  } catch (error) {
    console.error('❌ 图片上传API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式上传图片');
    return await mockApi.mockUploadImage();
  }
};

/**
 * 开始碑文识别
 * @param {Object} recognitionData - 识别数据
 * @param {string} recognitionData.image_id - 图片ID
 * @param {string} recognitionData.language - 语言类型 (classical/modern)
 * @param {Object} recognitionData.options - 识别选项
 * @returns {Promise}
 */
export const startRecognition = async (recognitionData) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式开始识别');
    return await mockApi.mockStartRecognition(recognitionData);
  }
  
  try {
    const response = await http.post('/recognition/start', recognitionData);
    return response;
  } catch (error) {
    console.error('❌ 开始识别API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式开始识别');
    return await mockApi.mockStartRecognition(recognitionData);
  }
};

/**
 * 查询识别进度
 * @param {string} taskId - 任务ID
 * @returns {Promise}
 */
export const getRecognitionProgress = async (taskId) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式查询识别进度');
    return await mockApi.mockCheckRecognitionProgress(taskId);
  }
  
  try {
    const response = await http.get(`/recognition/progress/${taskId}`);
    return response;
  } catch (error) {
    console.error('❌ 查询识别进度API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式查询识别进度');
    return await mockApi.mockCheckRecognitionProgress(taskId);
  }
};

/**
 * 获取识别历史记录
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.dynasty - 筛选朝代
 * @param {string} params.sort - 排序方式
 * @returns {Promise}
 */
export const getRecognitionHistory = async (params = {}) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式获取历史记录');
    return await mockApi.mockGetRecognitionHistory(params);
  }
  
  try {
    const response = await http.get('/recognition/history', { params });
    return response;
  } catch (error) {
    console.error('❌ 获取历史记录API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取历史记录');
    return await mockApi.mockGetRecognitionHistory(params);
  }
};

/**
 * 获取识别结果详情
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const getRecognitionDetail = async (recognitionId) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式获取识别详情');
    return await mockApi.mockGetRecognitionDetail(recognitionId);
  }
  
  try {
    // 根据后端文档，使用正确的API路径
    const response = await http.get(`/inscription/${recognitionId}`);
    return response;
  } catch (error) {
    console.error('❌ 获取识别详情API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取识别详情');
    return await mockApi.mockGetRecognitionDetail(recognitionId);
  }
};

/**
 * 删除识别记录
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const deleteRecognition = async (recognitionId) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式删除识别记录');
    return await mockApi.mockDeleteRecognition(recognitionId);
  }
  
  try {
    // 根据后端文档，使用正确的API路径
    const response = await http.delete(`/inscription/${recognitionId}`);
    return response;
  } catch (error) {
    console.error('❌ 删除识别记录API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式删除识别记录');
    return await mockApi.mockDeleteRecognition(recognitionId);
  }
};

/**
 * 批量删除识别记录
 * @param {Array} recognitionIds - 识别记录ID数组
 * @returns {Promise}
 */
export const batchDeleteRecognitions = async (recognitionIds) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式批量删除识别记录');
    return await mockApi.mockBatchDeleteRecognitions(recognitionIds);
  }
  
  try {
    // 根据后端文档，没有批量删除接口，使用循环调用单条删除
    for (const id of recognitionIds) {
      await http.delete(`/inscription/${id}`);
    }
    return { success: true, message: '批量删除成功' };
  } catch (error) {
    console.error('❌ 批量删除识别记录API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式批量删除识别记录');
    return await mockApi.mockBatchDeleteRecognitions(recognitionIds);
  }
};

/**
 * 导出识别结果
 * @param {Object} params - 导出参数
 * @param {Array} params.ids - 要导出的识别记录ID数组
 * @param {string} params.format - 导出格式 (txt/pdf/docx)
 * @param {string} params.include_image - 是否包含图片 (true/false)
 * @returns {Promise}
 */
export const exportRecognitions = async (params) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式导出识别结果');
    return await mockApi.mockExportRecognitions(params);
  }
  
  try {
    // 根据后端文档，没有直接的导出接口，使用getRecognitionDetail获取数据后前端处理
    const results = [];
    for (const id of params.ids) {
      const detail = await getRecognitionDetail(id);
      results.push(detail);
    }
    
    // 前端处理导出逻辑
    const exportData = { results, format: params.format, include_image: params.include_image };
    return { success: true, data: exportData };
  } catch (error) {
    console.error('❌ 导出识别结果API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式导出识别结果');
    return await mockApi.mockExportRecognitions(params);
  }
};

/**
 * 分享识别结果
 * @param {Object} shareData - 分享数据
 * @param {string} shareData.recognition_id - 识别记录ID
 * @param {string} shareData.share_type - 分享类型 (public/private/link)
 * @param {string} shareData.expire_time - 过期时间（可选）
 * @returns {Promise}
 */
export const shareRecognition = async (shareData) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式分享识别结果');
    return await mockApi.mockShareRecognition(shareData);
  }
  
  try {
    // 根据后端文档，没有直接的分享接口，使用前端生成分享链接
    const shareToken = generateShareToken(shareData.recognition_id);
    const shareUrl = `${window.location.origin}/shared/${shareToken}`;
    
    // 保存分享记录到本地存储
    const shareRecords = JSON.parse(localStorage.getItem('shareRecords') || '[]');
    shareRecords.push({
      ...shareData,
      shareToken,
      shareUrl,
      createdAt: new Date().toISOString()
    });
    localStorage.setItem('shareRecords', JSON.stringify(shareRecords));
    
    return { success: true, data: { shareToken, shareUrl } };
  } catch (error) {
    console.error('❌ 分享识别结果API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式分享识别结果');
    return await mockApi.mockShareRecognition(shareData);
  }
};

/**
 * 获取分享链接信息
 * @param {string} shareToken - 分享token
 * @returns {Promise}
 */
export const getSharedRecognition = async (shareToken) => {
  // 如果启用了Mock模式，直接使用Mock数据
  if (isMockEnabled()) {
    console.log('[Recognition Service] 使用Mock模式获取分享链接信息');
    return await mockApi.mockGetSharedRecognition(shareToken);
  }
  
  try {
    // 根据后端文档，没有直接的获取分享信息接口，从本地存储读取
    const shareRecords = JSON.parse(localStorage.getItem('shareRecords') || '[]');
    const shareRecord = shareRecords.find(record => record.shareToken === shareToken);
    
    if (!shareRecord) {
      throw new Error('分享记录不存在');
    }
    
    // 获取对应的识别详情
    const recognitionDetail = await getRecognitionDetail(shareRecord.recognition_id);
    
    return { success: true, data: { ...recognitionDetail.data, shareInfo: shareRecord } };
  } catch (error) {
    console.error('❌ 获取分享链接信息API调用失败:', error);
    // 失败后降级到Mock数据
    console.warn('⚠️ 降级到Mock模式获取分享链接信息');
    return await mockApi.mockGetSharedRecognition(shareToken);
  }
};

export default {
  uploadImage,
  startRecognition,
  getRecognitionProgress,
  getRecognitionHistory,
  getRecognitionDetail,
  deleteRecognition,
  batchDeleteRecognitions,
  exportRecognitions,
  shareRecognition,
  getSharedRecognition
};