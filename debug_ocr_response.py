#!/usr/bin/env python3
"""
OCR服务响应深度调试脚本
用于分析OCR服务的实际响应数据，找出识别失败的根本原因
"""

import asyncio
import base64
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入OCR客户端
import sys
sys.path.append('/Users/liuminxuan/Desktop/团队项目/python')

from app.client.kandianguji_ocr_client import KandiangujiOCRClient
from app.api.v1.recognition import _normalize_ocr

def load_image_as_base64(image_path):
    """加载图片并转换为base64"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

async def test_ocr_with_real_image():
    """使用真实图片测试OCR服务"""
    
    # 选择一个包含文字的图片进行测试
    test_images = [
        "/Users/liuminxuan/Desktop/团队项目/uploads/多宝塔碑.jpg",
        "/Users/liuminxuan/Desktop/团队项目/uploads/乙瑛碑.jpg",
        "/Users/liuminxuan/Desktop/团队项目/uploads/曹全碑.jpg"
    ]
    
    client = KandiangujiOCRClient()
    
    for image_path in test_images:
        if not Path(image_path).exists():
            logger.warning(f"图片不存在: {image_path}")
            continue
            
        logger.info(f"\n=== 测试图片: {image_path} ===")
        
        # 加载图片
        image_base64 = load_image_as_base64(image_path)
        logger.info(f"图片大小: {len(image_base64)} 字节")
        
        # 测试不同的OCR模式
        ocr_modes = [
            {"version": "v2", "det_mode": "auto"},  # 主模式
            {"version": "v2", "det_mode": "sp"},   # SP模式
            {"version": "v2", "det_mode": "hp"},   # HP模式
            {"version": "beta", "det_mode": "sp"}, # Beta+SP模式
        ]
        
        for mode in ocr_modes:
            logger.info(f"\n--- 测试模式: {mode} ---")
            
            try:
                # 调用OCR服务
                response = await client.recognize(image_base64, mode)
                
                logger.info("=== OCR服务原始响应 ===")
                logger.info(f"响应状态码: {response.get('status_code', 'N/A')}")
                logger.info(f"响应数据: {json.dumps(response, ensure_ascii=False, indent=2)}")
                
                # 检查响应结构
                if 'data' in response:
                    data = response['data']
                    logger.info("=== 响应数据结构分析 ===")
                    logger.info(f"数据类型: {type(data)}")
                    logger.info(f"数据内容: {data}")
                    
                    # 检查是否为列表类型
                    if isinstance(data, list):
                        logger.info("✅ 响应数据是列表类型")
                        logger.info(f"列表长度: {len(data)}")
                        for i, item in enumerate(data):
                            logger.info(f"列表项 {i}: {item}")
                    elif isinstance(data, dict):
                        logger.info("✅ 响应数据是字典类型")
                        logger.info(f"字典键: {list(data.keys())}")
                    
                    # 归一化处理
                    normalized = _normalize_ocr(data)
                    logger.info("=== 归一化结果 ===")
                    logger.info(f"归一化结果: {json.dumps(normalized, ensure_ascii=False, indent=2)}")
                    
                    # 分析结果
                    if normalized['full_text']:
                        logger.info(f"✅ 识别成功! 文字长度: {len(normalized['full_text'])}")
                        logger.info(f"识别文字: {normalized['full_text'][:100]}...")
                    else:
                        logger.warning("❌ 识别失败，无文字内容")
                        
                        # 深入分析失败原因
                        if normalized['text_lines']:
                            logger.info(f"有文字行但无完整文本: {normalized['text_lines']}")
                        if normalized['texts']:
                            logger.info(f"有文字块但无完整文本: {normalized['texts']}")
                        
                else:
                    logger.error("❌ 响应中缺少data字段")
                    
            except Exception as e:
                logger.error(f"❌ OCR调用失败: {e}")
                import traceback
                traceback.print_exc()

async def test_normalize_function():
    """测试归一化函数的各种情况"""
    logger.info("\n=== 测试归一化函数 ===")
    
    # 测试用例
    test_cases = [
        {
            "name": "空数据",
            "data": {}
        },
        {
            "name": "列表型数据",
            "data": ["文字1", "文字2", "文字3"]
        },
        {
            "name": "字典型数据（有full_text）",
            "data": {
                "full_text": "这是完整的文字",
                "confidence": 0.95,
                "width": 640,
                "height": 480
            }
        },
        {
            "name": "字典型数据（无full_text）",
            "data": {
                "text_lines": ["第一行", "第二行"],
                "confidence": 0.8,
                "width": 640,
                "height": 480
            }
        }
    ]
    
    for case in test_cases:
        logger.info(f"\n--- 测试: {case['name']} ---")
        try:
            result = _normalize_ocr(case['data'])
            logger.info(f"输入: {case['data']}")
            logger.info(f"输出: {result}")
            logger.info(f"文字长度: {len(result['full_text'])}")
        except Exception as e:
            logger.error(f"归一化失败: {e}")

async def main():
    """主函数"""
    logger.info("开始OCR服务响应深度调试...")
    
    # 测试归一化函数
    await test_normalize_function()
    
    # 测试真实图片OCR
    await test_ocr_with_real_image()
    
    logger.info("\n=== 调试完成 ===")

if __name__ == "__main__":
    asyncio.run(main())