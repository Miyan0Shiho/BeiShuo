#!/usr/bin/env python3
"""
OCR服务深度分析脚本
检查图片内容、OCR服务配置、以及可能的服务问题
"""

import asyncio
import base64
import json
import logging
from pathlib import Path
from PIL import Image
import io

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入OCR客户端
import sys
sys.path.append('/Users/liuminxuan/Desktop/团队项目/python')

from app.client.kandianguji_ocr_client import KandiangujiOCRClient

def analyze_image(image_path):
    """分析图片的基本信息"""
    try:
        with Image.open(image_path) as img:
            logger.info(f"图片格式: {img.format}")
            logger.info(f"图片尺寸: {img.size}")
            logger.info(f"图片模式: {img.mode}")
            
            # 检查图片是否包含文字（通过像素分析）
            # 简单的文字检测：检查是否有明显的黑白对比区域
            img_gray = img.convert('L')  # 转为灰度图
            pixels = list(img_gray.getdata())
            
            # 计算像素值的标准差，文字区域通常有较高的对比度
            import numpy as np
            std_dev = np.std(pixels)
            logger.info(f"像素标准差（对比度指标）: {std_dev:.2f}")
            
            if std_dev < 30:
                logger.warning("⚠️ 图片对比度较低，可能影响文字识别")
            else:
                logger.info("✅ 图片对比度正常")
                
    except Exception as e:
        logger.error(f"图片分析失败: {e}")

def load_image_as_base64_optimized(image_path):
    """优化图片加载和转换"""
    try:
        with Image.open(image_path) as img:
            # 如果图片太大，进行适当缩放
            max_size = (2000, 2000)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"图片已缩放至: {img.size}")
            
            # 转换为RGB模式（确保兼容性）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存为JPEG格式（OCR服务通常对JPEG支持更好）
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            image_data = buffer.getvalue()
            
            return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        logger.error(f"图片加载失败: {e}")
        # 回退到原始方法
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return base64.b64encode(image_data).decode('utf-8')

async def test_ocr_service_health():
    """测试OCR服务健康状态"""
    logger.info("\n=== 测试OCR服务健康状态 ===")
    
    client = KandiangujiOCRClient()
    
    # 创建一个简单的测试图片（包含文字）
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建一个包含文字的测试图片
    test_img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(test_img)
    
    try:
        # 尝试使用系统字体
        font = ImageFont.load_default()
    except:
        font = None
    
    # 绘制测试文字
    draw.text((10, 10), "测试文字OCR识别", fill='black', font=font)
    
    # 转换为base64
    buffer = io.BytesIO()
    test_img.save(buffer, format='JPEG')
    test_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    logger.info("使用包含文字的测试图片进行OCR服务健康检查")
    
    try:
        response = await client.recognize(test_image_base64, {"version": "v2", "det_mode": "auto"})
        
        logger.info("=== OCR服务健康检查响应 ===")
        logger.info(f"响应状态: {response.get('message', 'N/A')}")
        logger.info(f"响应ID: {response.get('id', 'N/A')}")
        
        data = response.get('data', [])
        if isinstance(data, list):
            logger.info(f"数据长度: {len(data)}")
            if data:
                logger.info("✅ OCR服务正常工作")
                logger.info(f"识别内容: {data}")
            else:
                logger.warning("⚠️ OCR服务返回空数据，可能需要检查服务状态")
        else:
            logger.info(f"数据类型: {type(data)}")
            
    except Exception as e:
        logger.error(f"❌ OCR服务健康检查失败: {e}")

async def test_real_images_with_detailed_analysis():
    """详细分析真实图片的OCR识别"""
    
    # 测试不同的图片
    test_images = [
        "/Users/liuminxuan/Desktop/团队项目/uploads/多宝塔碑.jpg",
        "/Users/liuminxuan/Desktop/团队项目/uploads/乙瑛碑.jpg", 
        "/Users/liuminxuan/Desktop/团队项目/uploads/曹全碑.jpg",
        "/Users/liuminxuan/Desktop/团队项目/多宝塔碑.jpg"
    ]
    
    client = KandiangujiOCRClient()
    
    for image_path in test_images:
        if not Path(image_path).exists():
            logger.warning(f"图片不存在: {image_path}")
            continue
            
        logger.info(f"\n{'='*60}")
        logger.info(f"分析图片: {image_path}")
        logger.info(f"{'='*60}")
        
        # 分析图片
        analyze_image(image_path)
        
        # 加载图片
        image_base64 = load_image_as_base64_optimized(image_path)
        logger.info(f"Base64数据大小: {len(image_base64)} 字符")
        
        # 测试OCR服务
        try:
            response = await client.recognize(image_base64, {"version": "v2", "det_mode": "auto"})
            
            logger.info("=== OCR服务响应详情 ===")
            logger.info(f"响应状态: {response.get('message', 'N/A')}")
            logger.info(f"响应ID: {response.get('id', 'N/A')}")
            logger.info(f"响应信息: {response.get('info', 'N/A')}")
            
            data = response.get('data', [])
            logger.info(f"数据类型: {type(data)}")
            logger.info(f"数据内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 深入分析响应
            if isinstance(data, list):
                if data:
                    logger.info("✅ 识别到文字内容")
                    for i, item in enumerate(data):
                        logger.info(f"文字块 {i}: {item}")
                else:
                    logger.warning("❌ 未识别到任何文字")
                    
                    # 尝试不同的OCR模式
                    logger.info("尝试其他OCR模式...")
                    modes = [
                        {"version": "v2", "det_mode": "sp"},
                        {"version": "v2", "det_mode": "hp"},
                        {"version": "beta", "det_mode": "sp"}
                    ]
                    
                    for mode in modes:
                        try:
                            response_alt = await client.recognize(image_base64, mode)
                            data_alt = response_alt.get('data', [])
                            if data_alt:
                                logger.info(f"✅ 模式 {mode} 识别到文字: {data_alt}")
                                break
                            else:
                                logger.info(f"❌ 模式 {mode} 也未识别到文字")
                        except Exception as e:
                            logger.error(f"模式 {mode} 失败: {e}")
                            
        except Exception as e:
            logger.error(f"❌ OCR识别失败: {e}")

async def main():
    """主函数"""
    logger.info("开始OCR服务深度分析...")
    
    # 测试OCR服务健康状态
    await test_ocr_service_health()
    
    # 分析真实图片
    await test_real_images_with_detailed_analysis()
    
    logger.info("\n=== 分析完成 ===")

if __name__ == "__main__":
    asyncio.run(main())