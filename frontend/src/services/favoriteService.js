/**
 * 收藏管理相关API服务
 */

import { http } from '../utils/httpClient';

/**
 * 获取收藏列表
 * @param {Object} params - 查询参数
 * @param {string} params.type - 收藏类型筛选 (inscriptions/articles)
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.sort - 排序方式
 * @returns {Promise}
 */
export const getFavorites = async (params = {}) => {
  const response = await http.get('/favorites', { params });
  return response;
};

/**
 * 添加收藏
 * @param {Object} favoriteData - 收藏数据
 * @param {string} favoriteData.type - 收藏类型 (inscription/article)
 * @param {string} favoriteData.item_id - 收藏项目ID
 * @param {string} favoriteData.notes - 收藏备注
 * @param {Array} favoriteData.tags - 标签数组
 * @returns {Promise}
 */
export const addFavorite = async (favoriteData) => {
  const response = await http.post('/favorites', favoriteData);
  return response;
};

/**
 * 更新收藏
 * @param {string} favoriteId - 收藏ID
 * @param {Object} updateData - 更新数据
 * @param {string} updateData.notes - 收藏备注
 * @param {Array} updateData.tags - 标签数组
 * @returns {Promise}
 */
export const updateFavorite = async (favoriteId, updateData) => {
  const response = await http.put(`/favorites/${favoriteId}`, updateData);
  return response;
};

/**
 * 删除收藏
 * @param {string} favoriteId - 收藏ID
 * @returns {Promise}
 */
export const deleteFavorite = async (favoriteId) => {
  const response = await http.delete(`/favorites/${favoriteId}`);
  return response;
};

/**
 * 批量删除收藏
 * @param {Array} favoriteIds - 收藏ID数组
 * @returns {Promise}
 */
export const batchDeleteFavorites = async (favoriteIds) => {
  const response = await http.delete('/favorites/batch', {
    data: { favorite_ids: favoriteIds }
  });
  return response;
};

/**
 * 检查是否已收藏
 * @param {string} itemId - 项目ID
 * @param {string} itemType - 项目类型
 * @returns {Promise}
 */
export const checkFavoriteStatus = async (itemId, itemType) => {
  const response = await http.get(`/favorites/check/${itemType}/${itemId}`);
  return response;
};

/**
 * 移动收藏到文件夹
 * @param {string} favoriteId - 收藏ID
 * @param {string} folderId - 文件夹ID
 * @returns {Promise}
 */
export const moveFavoriteToFolder = async (favoriteId, folderId) => {
  const response = await http.post(`/favorites/${favoriteId}/move`, {
    folder_id: folderId
  });
  return response;
};

/**
 * 获取收藏统计
 * @returns {Promise}
 */
export const getFavoriteStats = async () => {
  const response = await http.get('/favorites/stats');
  return response;
};

/**
 * 导出收藏
 * @param {Object} params - 导出参数
 * @param {Array} params.favorite_ids - 收藏ID数组（空则导出全部）
 * @param {string} params.format - 导出格式 (csv/json)
 * @param {string} params.include_notes - 是否包含备注 (true/false)
 * @returns {Promise}
 */
export const exportFavorites = async (params) => {
  const response = await http.post('/favorites/export', params, {
    responseType: 'blob'
  });
  return response;
};

/**
 * 导入收藏
 * @param {FormData} formData - 导入数据
 * @returns {Promise}
 */
export const importFavorites = async (formData) => {
  const response = await http.upload('/favorites/import', formData);
  return response;
};

/**
 * 获取收藏文件夹列表
 * @returns {Promise}
 */
export const getFavoriteFolders = async () => {
  const response = await http.get('/favorites/folders');
  return response;
};

/**
 * 创建收藏文件夹
 * @param {Object} folderData - 文件夹数据
 * @param {string} folderData.name - 文件夹名称
 * @param {string} folderData.description - 文件夹描述
 * @returns {Promise}
 */
export const createFavoriteFolder = async (folderData) => {
  const response = await http.post('/favorites/folders', folderData);
  return response;
};

/**
 * 更新收藏文件夹
 * @param {string} folderId - 文件夹ID
 * @param {Object} updateData - 更新数据
 * @returns {Promise}
 */
export const updateFavoriteFolder = async (folderId, updateData) => {
  const response = await http.put(`/favorites/folders/${folderId}`, updateData);
  return response;
};

/**
 * 删除收藏文件夹
 * @param {string} folderId - 文件夹ID
 * @returns {Promise}
 */
export const deleteFavoriteFolder = async (folderId) => {
  const response = await http.delete(`/favorites/folders/${folderId}`);
  return response;
};

export default {
  getFavorites,
  addFavorite,
  updateFavorite,
  deleteFavorite,
  batchDeleteFavorites,
  checkFavoriteStatus,
  moveFavoriteToFolder,
  getFavoriteStats,
  exportFavorites,
  importFavorites,
  getFavoriteFolders,
  createFavoriteFolder,
  updateFavoriteFolder,
  deleteFavoriteFolder
};