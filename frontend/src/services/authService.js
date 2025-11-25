/**
 * 用户认证相关API服务
 */

import { http } from '../utils/httpClient';

/**
 * 用户注册
 * @param {Object} userData - 用户注册数据
 * @param {string} userData.name - 用户名
 * @param {string} userData.email - 邮箱
 * @param {string} userData.password - 密码
 * @param {string} userData.phone - 手机号（可选）
 * @param {string} userData.avatar - 头像（base64编码，可选）
 * @returns {Promise}
 */
export const register = async (userData) => {
  const response = await http.post('/auth/register', userData);
  return response;
};

/**
 * 用户登录
 * @param {Object} loginData - 登录数据
 * @param {string} loginData.email - 邮箱
 * @param {string} loginData.password - 密码
 * @param {boolean} loginData.remember_me - 记住我（可选）
 * @returns {Promise}
 */
export const login = async (loginData) => {
  const response = await http.post('/auth/login', loginData);
  return response;
};

/**
 * 刷新Token
 * @returns {Promise}
 */
export const refreshToken = async () => {
  const response = await http.post('/auth/refresh');
  return response;
};

/**
 * 用户登出
 * @returns {Promise}
 */
export const logout = async () => {
  const response = await http.post('/auth/logout');
  return response;
};

/**
 * 获取用户信息
 * @returns {Promise}
 */
export const getProfile = async () => {
  const response = await http.get('/auth/profile');
  return response;
};

/**
 * 更新用户信息
 * @param {Object} profileData - 用户信息数据
 * @returns {Promise}
 */
export const updateProfile = async (profileData) => {
  const response = await http.put('/auth/profile', profileData);
  return response;
};

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.old_password - 原密码
 * @param {string} passwordData.new_password - 新密码
 * @param {string} passwordData.confirm_password - 确认新密码
 * @returns {Promise}
 */
export const changePassword = async (passwordData) => {
  const response = await http.put('/auth/change-password', passwordData);
  return response;
};

/**
 * 验证邮箱
 * @param {string} token - 验证token
 * @returns {Promise}
 */
export const verifyEmail = async (token) => {
  const response = await http.post('/auth/verify-email', { token });
  return response;
};

/**
 * 重置密码请求
 * @param {string} email - 邮箱地址
 * @returns {Promise}
 */
export const requestPasswordReset = async (email) => {
  const response = await http.post('/auth/forgot-password', { email });
  return response;
};

/**
 * 重置密码
 * @param {Object} resetData - 重置密码数据
 * @param {string} resetData.token - 重置token
 * @param {string} resetData.password - 新密码
 * @param {string} resetData.confirm_password - 确认新密码
 * @returns {Promise}
 */
export const resetPassword = async (resetData) => {
  const response = await http.post('/auth/reset-password', resetData);
  return response;
};

export default {
  register,
  login,
  refreshToken,
  logout,
  getProfile,
  updateProfile,
  changePassword,
  verifyEmail,
  requestPasswordReset,
  resetPassword
};