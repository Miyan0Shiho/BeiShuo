#!/usr/bin/env python3
"""
测试OCR缓存功能的脚本
"""
import asyncio
import traceback
from app.client.mysql_client import mysql_client

async def test_ocr_cache():
    """测试OCR缓存功能"""
    print("开始测试OCR缓存功能")
    
    try:
        # 连接数据库
        print("连接数据库...")
        await mysql_client.connect()
        print("数据库连接成功")
        
        # 1. 测试保存OCR结果
        print("\n测试1: 保存OCR结果")
        
        # 模拟OCR结果数据
        task_id = "test_task_123"
        # 模拟完整的OCR结果，包含image_url和request字段
        result_data = {
            "request": {
                "image_url": "/uploads/test_image.png",
                "options": {}
            },
            "result": {
                "recognition_id": "test_recognition_123",
                "text": "测试文本\n多行文本",
                "word_count": 2,
                "confidence": 0.95,
                "width": 1000,
                "height": 500,
                "text_angel": 0,
                "text_lines": [
                    {
                        "text": "测试文本",
                        "line_index": 0,
                        "words": [
                            {"text": "测试文本", "confidence": 0.95, "choices": ""}
                        ]
                    },
                    {
                        "text": "多行文本",
                        "line_index": 1,
                        "words": [
                            {"text": "多行文本", "confidence": 0.95, "choices": ""}
                        ]
                    }
                ],
                "texts": ["测试文本", "多行文本"],
                "layout": None,
                "image_url": "/uploads/test_image.png"
            }
        }
        image_hash = "test_image_hash_123"
        
        # 保存OCR结果
        print(f"保存OCR结果... image_hash={image_hash}")
        saved_result = await mysql_client.save_ocr_result(task_id, result_data, image_hash)
        print(f"保存OCR结果成功: {saved_result}")
        
        # 2. 测试查询OCR结果
        print("\n测试2: 查询OCR结果")
        print(f"查询OCR结果... image_hash={image_hash}")
        ocr_result = await mysql_client.get_ocr_result_by_image_hash(image_hash)
        if ocr_result:
            print(f"查询OCR结果成功: {ocr_result}")
        else:
            print("查询OCR结果失败: 未找到结果")
        
        # 3. 测试缓存命中（同一脚本内）
        print("\n测试3: 测试缓存命中（同一脚本内）")
        print(f"再次查询OCR结果... image_hash={image_hash}")
        ocr_result_again = await mysql_client.get_ocr_result_by_image_hash(image_hash)
        if ocr_result_again:
            print(f"缓存命中成功: {ocr_result_again}")
        else:
            print("缓存命中失败: 未找到结果")
        
        print("\nOCR缓存测试完成")
        
    except Exception as e:
        print(f"测试OCR缓存失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await mysql_client.disconnect()
        print("数据库连接关闭成功")

if __name__ == "__main__":
    asyncio.run(test_ocr_cache())