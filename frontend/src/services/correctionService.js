/**
 * 校对编辑相关API服务
 */

import { http } from '../utils/httpClient';

/**
 * 更新识别结果
 * @param {string} recognitionId - 识别记录ID
 * @param {Object} correctionData - 校对数据
 * @param {string} correctionData.corrected_text - 校对后的文本
 * @param {Array} correctionData.corrections - 校对记录
 * @param {string} correctionData.notes - 校对备注
 * @returns {Promise}
 */
export const updateRecognitionResult = async (recognitionId, correctionData) => {
  const response = await http.put(`/recognition/${recognitionId}/correct`, correctionData);
  return response;
};

/**
 * 获取校对建议
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const getCorrectionSuggestions = async (recognitionId) => {
  const response = await http.get(`/recognition/${recognitionId}/suggestions`);
  return response;
};

/**
 * 保存校对记录
 * @param {string} recognitionId - 识别记录ID
 * @param {Object} historyData - 校对历史数据
 * @param {string} historyData.action - 操作类型
 * @param {Array} historyData.changes - 变更记录
 * @param {string} historyData.notes - 备注
 * @returns {Promise}
 */
export const saveCorrectionHistory = async (recognitionId, historyData) => {
  const response = await http.post(`/recognition/${recognitionId}/history`, historyData);
  return response;
};

/**
 * 获取校对历史
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const getCorrectionHistory = async (recognitionId) => {
  const response = await http.get(`/recognition/${recognitionId}/history`);
  return response;
};

/**
 * 撤销校对操作
 * @param {string} recognitionId - 识别记录ID
 * @param {string} versionId - 版本ID
 * @returns {Promise}
 */
export const revertToVersion = async (recognitionId, versionId) => {
  const response = await http.post(`/recognition/${recognitionId}/revert`, { version_id: versionId });
  return response;
};

/**
 * 比较两个版本
 * @param {string} recognitionId - 识别记录ID
 * @param {Object} comparisonData - 比较数据
 * @param {string} comparisonData.version1 - 第一个版本ID
 * @param {string} comparisonData.version2 - 第二个版本ID
 * @returns {Promise}
 */
export const compareVersions = async (recognitionId, comparisonData) => {
  const response = await http.post(`/recognition/${recognitionId}/compare`, comparisonData);
  return response;
};

/**
 * 获取可用版本列表
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const getVersionHistory = async (recognitionId) => {
  const response = await http.get(`/recognition/${recognitionId}/versions`);
  return response;
};

/**
 * 保存当前编辑状态
 * @param {string} recognitionId - 识别记录ID
 * @param {Object} draftData - 草稿数据
 * @param {string} draftData.content - 编辑内容
 * @param {Object} draftData.metadata - 元数据
 * @returns {Promise}
 */
export const saveDraft = async (recognitionId, draftData) => {
  const response = await http.post(`/recognition/${recognitionId}/draft`, draftData);
  return response;
};

/**
 * 加载草稿
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const loadDraft = async (recognitionId) => {
  const response = await http.get(`/recognition/${recognitionId}/draft`);
  return response;
};

/**
 * 删除草稿
 * @param {string} recognitionId - 识别记录ID
 * @returns {Promise}
 */
export const deleteDraft = async (recognitionId) => {
  const response = await http.delete(`/recognition/${recognitionId}/draft`);
  return response;
};

export default {
  updateRecognitionResult,
  getCorrectionSuggestions,
  saveCorrectionHistory,
  getCorrectionHistory,
  revertToVersion,
  compareVersions,
  getVersionHistory,
  saveDraft,
  loadDraft,
  deleteDraft
};