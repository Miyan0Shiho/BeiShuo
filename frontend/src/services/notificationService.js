/**
 * 通知消息相关API服务
 */

import { http } from '../utils/httpClient';

/**
 * 获取通知列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 * @param {string} params.type - 通知类型筛选
 * @param {boolean} params.unread_only - 仅未读
 * @returns {Promise}
 */
export const getNotifications = async (params = {}) => {
  const response = await http.get('/notifications', { params });
  return response;
};

/**
 * 标记通知为已读
 * @param {string} notificationId - 通知ID
 * @returns {Promise}
 */
export const markAsRead = async (notificationId) => {
  const response = await http.put(`/notifications/${notificationId}/read`);
  return response;
};

/**
 * 批量标记为已读
 * @param {Array} notificationIds - 通知ID数组
 * @returns {Promise}
 */
export const markMultipleAsRead = async (notificationIds) => {
  const response = await http.put('/notifications/mark-read', {
    notification_ids: notificationIds
  });
  return response;
};

/**
 * 标记所有通知为已读
 * @returns {Promise}
 */
export const markAllAsRead = async () => {
  const response = await http.put('/notifications/mark-all-read');
  return response;
};

/**
 * 删除通知
 * @param {string} notificationId - 通知ID
 * @returns {Promise}
 */
export const deleteNotification = async (notificationId) => {
  const response = await http.delete(`/notifications/${notificationId}`);
  return response;
};

/**
 * 批量删除通知
 * @param {Array} notificationIds - 通知ID数组
 * @returns {Promise}
 */
export const deleteMultipleNotifications = async (notificationIds) => {
  const response = await http.delete('/notifications/batch-delete', {
    data: { notification_ids: notificationIds }
  });
  return response;
};

/**
 * 获取未读通知数量
 * @returns {Promise}
 */
export const getUnreadCount = async () => {
  const response = await http.get('/notifications/unread-count');
  return response;
};

/**
 * 创建通知（管理员功能）
 * @param {Object} notificationData - 通知数据
 * @returns {Promise}
 */
export const createNotification = async (notificationData) => {
  const response = await http.post('/notifications', notificationData);
  return response;
};

/**
 * 更新通知设置
 * @param {Object} settingsData - 设置数据
 * @returns {Promise}
 */
export const updateNotificationSettings = async (settingsData) => {
  const response = await http.put('/notifications/settings', settingsData);
  return response;
};

/**
 * 获取通知设置
 * @returns {Promise}
 */
export const getNotificationSettings = async () => {
  const response = await http.get('/notifications/settings');
  return response;
};

/**
 * 发送推送通知
 * @param {Object} pushData - 推送数据
 * @returns {Promise}
 */
export const sendPushNotification = async (pushData) => {
  const response = await http.post('/notifications/push', pushData);
  return response;
};

export default {
  getNotifications,
  markAsRead,
  markMultipleAsRead,
  markAllAsRead,
  deleteNotification,
  deleteMultipleNotifications,
  getUnreadCount,
  createNotification,
  updateNotificationSettings,
  getNotificationSettings,
  sendPushNotification
};