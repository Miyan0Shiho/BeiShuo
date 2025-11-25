/**
 * 工具类API服务
 */

import { http } from '../utils/httpClient';

/**
 * 文本转换工具
 * @param {Object} convertData - 转换数据
 * @param {string} convertData.text - 原文
 * @param {string} convertData.convert_type - 转换类型
 * @param {Object} convertData.options - 转换选项
 * @returns {Promise}
 */
export const textConvert = async (convertData) => {
  const response = await http.post('/tools/text-convert', convertData);
  return response;
};

/**
 * 字体识别工具
 * @param {Object} fontData - 字体识别数据
 * @param {string} fontData.image_id - 图片ID
 * @param {Object} fontData.sample_area - 样本区域
 * @returns {Promise}
 */
export const identifyFont = async (fontData) => {
  const response = await http.post('/tools/font-identify', fontData);
  return response;
};

/**
 * 文本纠错
 * @param {Object} correctionData - 纠错数据
 * @param {string} correctionData.text - 原文
 * @param {string} correctionData.language - 语言 (ancient/modern)
 * @returns {Promise}
 */
export const spellCheck = async (correctionData) => {
  const response = await http.post('/tools/spell-check', correctionData);
  return response;
};

/**
 * 文字分割
 * @param {Object} segmentationData - 分割数据
 * @param {string} segmentationData.text - 原文
 * @param {string} segmentationData.method - 分割方法
 * @returns {Promise}
 */
export const textSegmentation = async (segmentationData) => {
  const response = await http.post('/tools/text-segmentation', segmentationData);
  return response;
};

/**
 * 繁简转换
 * @param {Object} conversionData - 转换数据
 * @param {string} conversionData.text - 原文
 * @param {string} conversionData.direction - 转换方向 (traditional_to_simplified/simplified_to_traditional)
 * @returns {Promise}
 */
export const characterConversion = async (conversionData) => {
  const response = await http.post('/tools/character-conversion', conversionData);
  return response;
};

/**
 * 拼音标注
 * @param {Object} pinyinData - 拼音数据
 * @param {string} pinyinData.text - 原文
 * @param {string} pinyinData.style - 标注风格 (tone_marks/diacritics/numbers)
 * @returns {Promise}
 */
export const addPinyin = async (pinyinData) => {
  const response = await http.post('/tools/pinyin', pinyinData);
  return response;
};

/**
 * 文字统计
 * @param {Object} statsData - 统计数据
 * @param {string} statsData.text - 原文
 * @param {Array} statsData.metrics - 要统计的指标
 * @returns {Promise}
 */
export const textStatistics = async (statsData) => {
  const response = await http.post('/tools/text-statistics', statsData);
  return response;
};

/**
 * 图像增强
 * @param {Object} enhancementData - 增强数据
 * @param {string} enhancementData.image_id - 图片ID
 * @param {Array} enhancementData.operations - 增强操作
 * @returns {Promise}
 */
export const imageEnhancement = async (enhancementData) => {
  const response = await http.post('/tools/image-enhancement', enhancementData);
  return response;
};

/**
 * OCR文本提取
 * @param {Object} ocrData - OCR数据
 * @param {string} ocrData.image_id - 图片ID
 * @param {Object} ocrData.options - OCR选项
 * @returns {Promise}
 */
export const extractText = async (ocrData) => {
  const response = await http.post('/tools/ocr', ocrData);
  return response;
};

/**
 * 语音转文字
 * @param {FormData} audioData - 音频数据
 * @returns {Promise}
 */
export const speechToText = async (audioData) => {
  const response = await http.upload('/tools/speech-to-text', audioData);
  return response;
};

export default {
  textConvert,
  identifyFont,
  spellCheck,
  textSegmentation,
  characterConversion,
  addPinyin,
  textStatistics,
  imageEnhancement,
  extractText,
  speechToText
};