/**
 * 知识库相关API服务
 */

import { http } from '../utils/httpClient';

/**
 * 获取知识库首页
 * @param {Object} params - 查询参数
 * @param {string} params.category - 分类筛选
 * @param {string} params.period - 时期筛选
 * @returns {Promise}
 */
export const getKnowledgeHome = async (params = {}) => {
  const response = await http.get('/knowledge/home', { params });
  return response;
};

/**
 * 获取文章详情
 * @param {string} articleId - 文章ID
 * @returns {Promise}
 */
export const getArticleDetail = async (articleId) => {
  const response = await http.get(`/knowledge/articles/${articleId}`);
  return response;
};

/**
 * 搜索知识库
 * @param {Object} searchParams - 搜索参数
 * @param {string} searchParams.q - 搜索关键词
 * @param {string} searchParams.type - 搜索类型 (all/articles/inscriptions)
 * @param {string} searchParams.category - 分类筛选
 * @param {string} searchParams.dynasty - 朝代筛选
 * @param {number} searchParams.page - 页码
 * @param {number} searchParams.per_page - 每页数量
 * @returns {Promise}
 */
export const searchKnowledge = async (searchParams) => {
  const response = await http.get('/knowledge/search', { params: searchParams });
  return response;
};

/**
 * 获取知识库分类列表
 * @returns {Promise}
 */
export const getCategories = async () => {
  const response = await http.get('/knowledge/categories');
  return response;
};

/**
 * 获取分类文章列表
 * @param {string} categoryId - 分类ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getCategoryArticles = async (categoryId, params = {}) => {
  const response = await http.get(`/knowledge/categories/${categoryId}/articles`, { params });
  return response;
};

/**
 * 获取朝代信息列表
 * @returns {Promise}
 */
export const getDynasties = async () => {
  const response = await http.get('/knowledge/dynasties');
  return response;
};

/**
 * 获取朝代详情
 * @param {string} dynastyId - 朝代ID
 * @returns {Promise}
 */
export const getDynastyDetail = async (dynastyId) => {
  const response = await http.get(`/knowledge/dynasties/${dynastyId}`);
  return response;
};

/**
 * 获取朝代相关碑文
 * @param {string} dynastyId - 朝代ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getDynastyInscriptions = async (dynastyId, params = {}) => {
  const response = await http.get(`/knowledge/dynasties/${dynastyId}/inscriptions`, { params });
  return response;
};

/**
 * 获取碑文详细信息
 * @param {string} inscriptionId - 碑文ID
 * @returns {Promise}
 */
export const getInscriptionDetail = async (inscriptionId) => {
  const response = await http.get(`/knowledge/inscriptions/${inscriptionId}`);
  return response;
};

/**
 * 获取相关文章推荐
 * @param {string} articleId - 文章ID
 * @param {number} limit - 推荐数量
 * @returns {Promise}
 */
export const getRelatedArticles = async (articleId, limit = 5) => {
  const response = await http.get(`/knowledge/articles/${articleId}/related`, {
    params: { limit }
  });
  return response;
};

/**
 * 点赞文章
 * @param {string} articleId - 文章ID
 * @returns {Promise}
 */
export const likeArticle = async (articleId) => {
  const response = await http.post(`/knowledge/articles/${articleId}/like`);
  return response;
};

/**
 * 取消点赞文章
 * @param {string} articleId - 文章ID
 * @returns {Promise}
 */
export const unlikeArticle = async (articleId) => {
  const response = await http.delete(`/knowledge/articles/${articleId}/like`);
  return response;
};

/**
 * 收藏文章
 * @param {string} articleId - 文章ID
 * @returns {Promise}
 */
export const bookmarkArticle = async (articleId) => {
  const response = await http.post(`/knowledge/articles/${articleId}/bookmark`);
  return response;
};

/**
 * 取消收藏文章
 * @param {string} articleId - 文章ID
 * @returns {Promise}
 */
export const unbookmarkArticle = async (articleId) => {
  const response = await http.delete(`/knowledge/articles/${articleId}/bookmark`);
  return response;
};

/**
 * 获取用户阅读历史
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getReadingHistory = async (params) => {
  const response = await http.get('/knowledge/user/reading-history', { params });
  return response;
};

/**
 * 记录阅读进度
 * @param {string} articleId - 文章ID
 * @param {Object} progressData - 进度数据
 * @returns {Promise}
 */
export const recordReadingProgress = async (articleId, progressData) => {
  const response = await http.post(`/knowledge/articles/${articleId}/reading-progress`, progressData);
  return response;
};

/**
 * 获取热门内容
 * @param {Object} params - 查询参数
 * @param {string} params.type - 内容类型 (articles/inscriptions)
 * @param {string} params.time_range - 时间范围 (today/week/month/year)
 * @param {number} params.limit - 数量限制
 * @returns {Promise}
 */
export const getHotContent = async (params = {}) => {
  const response = await http.get('/knowledge/hot-content', { params });
  return response;
};

/**
 * 获取精选内容
 * @param {Object} params - 查询参数
 * @param {string} params.type - 内容类型
 * @param {number} params.limit - 数量限制
 * @returns {Promise}
 */
export const getFeaturedContent = async (params = {}) => {
  const response = await http.get('/knowledge/featured', { params });
  return response;
};

/**
 * 反馈内容质量
 * @param {Object} feedbackData - 反馈数据
 * @param {string} feedbackData.content_id - 内容ID
 * @param {string} feedbackData.content_type - 内容类型 (article/inscription)
 * @param {string} feedbackData.feedback_type - 反馈类型 (error/suggestion/appreciation)
 * @param {string} feedbackData.content - 反馈内容
 * @returns {Promise}
 */
export const provideContentFeedback = async (feedbackData) => {
  const response = await http.post('/knowledge/feedback', feedbackData);
  return response;
};

export default {
  getKnowledgeHome,
  getArticleDetail,
  searchKnowledge,
  getCategories,
  getCategoryArticles,
  getDynasties,
  getDynastyDetail,
  getDynastyInscriptions,
  getInscriptionDetail,
  getRelatedArticles,
  likeArticle,
  unlikeArticle,
  bookmarkArticle,
  unbookmarkArticle,
  getReadingHistory,
  recordReadingProgress,
  getHotContent,
  getFeaturedContent,
  provideContentFeedback
};