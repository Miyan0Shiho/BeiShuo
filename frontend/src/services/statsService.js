/**
 * 统计数据相关API服务
 */

import { http } from '../utils/httpClient';

/**
 * 获取用户统计
 * @returns {Promise}
 */
export const getUserStats = async () => {
  const response = await http.get('/stats/user');
  return response;
};

/**
 * 获取平台统计
 * @returns {Promise}
 */
export const getPlatformStats = async () => {
  const response = await http.get('/stats/platform');
  return response;
};

/**
 * 获取识别统计
 * @param {Object} params - 查询参数
 * @param {string} params.time_range - 时间范围 (today/week/month/year)
 * @param {string} params.group_by - 分组方式 (day/week/month)
 * @returns {Promise}
 */
export const getRecognitionStats = async (params = {}) => {
  const response = await http.get('/stats/recognitions', { params });
  return response;
};

/**
 * 获取AI使用统计
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getAIUsageStats = async (params = {}) => {
  const response = await http.get('/stats/ai-usage', { params });
  return response;
};

/**
 * 获取热门内容统计
 * @param {Object} params - 查询参数
 * @param {string} params.type - 内容类型 (articles/inscriptions)
 * @param {string} params.time_range - 时间范围
 * @param {number} params.limit - 数量限制
 * @returns {Promise}
 */
export const getPopularContentStats = async (params = {}) => {
  const response = await http.get('/stats/popular-content', { params });
  return response;
};

/**
 * 获取朝代分布统计
 * @returns {Promise}
 */
export const getDynastyDistribution = async () => {
  const response = await http.get('/stats/dynasty-distribution');
  return response;
};

/**
 * 获取用户活跃度统计
 * @param {Object} params - 查询参数
 * @param {string} params.time_range - 时间范围
 * @returns {Promise}
 */
export const getUserActivityStats = async (params = {}) => {
  const response = await http.get('/stats/user-activity', { params });
  return response;
};

/**
 * 获取错误统计
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getErrorStats = async (params = {}) => {
  const response = await http.get('/stats/errors', { params });
  return response;
};

/**
 * 获取系统性能统计
 * @returns {Promise}
 */
export const getPerformanceStats = async () => {
  const response = await http.get('/stats/performance');
  return response;
};

/**
 * 导出统计数据
 * @param {Object} params - 导出参数
 * @param {string} params.data_type - 数据类型
 * @param {string} params.format - 导出格式 (csv/excel/json)
 * @param {string} params.time_range - 时间范围
 * @returns {Promise}
 */
export const exportStats = async (params) => {
  const response = await http.post('/stats/export', params, {
    responseType: 'blob'
  });
  return response;
};

export default {
  getUserStats,
  getPlatformStats,
  getRecognitionStats,
  getAIUsageStats,
  getPopularContentStats,
  getDynastyDistribution,
  getUserActivityStats,
  getErrorStats,
  getPerformanceStats,
  exportStats
};