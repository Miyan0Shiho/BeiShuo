#!/usr/bin/env python3
"""
测试OCR内存缓存功能，特别是字符位置信息格式
"""
import asyncio
import traceback
import hashlib
from app.client.mysql_client import mysql_client
from app.client.kandianguji_ocr_client import KandiangujiOCRClient

async def test_ocr_memory_cache():
    """测试OCR内存缓存功能，特别是字符位置信息格式"""
    print("开始测试OCR内存缓存功能")
    
    try:
        # 1. 模拟OCR结果，包含字符位置信息
        print("\n1. 创建模拟OCR结果")
        
        # 模拟OCR结果，包含详细的字符位置信息
        ocr_result = {
            "task_id": "test_task_123",
            "status": "completed",
            "progress": 100,
            "estimated_time": 0,
            "result": {
                "recognition_id": "test_recognition_123",
                "width": 1000,
                "height": 500,
                "text_angel": 0,
                "texts": ["测试文本第一行", "测试文本第二行"],
                "text_lines": [
                    {
                        "text": "测试文本第一行",
                        "position": [[100, 100], [500, 100], [500, 150], [100, 150]],
                        "words": [
                            {"text": "测", "confidence": 0.95, "position": [[100, 100], [150, 100], [150, 150], [100, 150]]},
                            {"text": "试", "confidence": 0.96, "position": [[150, 100], [200, 100], [200, 150], [150, 150]]},
                            {"text": "文", "confidence": 0.97, "position": [[200, 100], [250, 100], [250, 150], [200, 150]]},
                            {"text": "本", "confidence": 0.98, "position": [[250, 100], [300, 100], [300, 150], [250, 150]]},
                            {"text": "第", "confidence": 0.99, "position": [[300, 100], [350, 100], [350, 150], [300, 150]]},
                            {"text": "一", "confidence": 0.95, "position": [[350, 100], [400, 100], [400, 150], [350, 150]]},
                            {"text": "行", "confidence": 0.96, "position": [[400, 100], [450, 100], [450, 150], [400, 150]]}
                        ]
                    },
                    {
                        "text": "测试文本第二行",
                        "position": [[100, 200], [500, 200], [500, 250], [100, 250]],
                        "words": [
                            {"text": "测", "confidence": 0.97, "position": [[100, 200], [150, 200], [150, 250], [100, 250]]},
                            {"text": "试", "confidence": 0.98, "position": [[150, 200], [200, 200], [200, 250], [150, 250]]},
                            {"text": "文", "confidence": 0.99, "position": [[200, 200], [250, 200], [250, 250], [200, 250]]},
                            {"text": "本", "confidence": 0.95, "position": [[250, 200], [300, 200], [300, 250], [250, 250]]},
                            {"text": "第", "confidence": 0.96, "position": [[300, 200], [350, 200], [350, 250], [300, 250]]},
                            {"text": "二", "confidence": 0.97, "position": [[350, 200], [400, 200], [400, 250], [350, 250]]},
                            {"text": "行", "confidence": 0.98, "position": [[400, 200], [450, 200], [450, 250], [400, 250]]}
                        ]
                    }
                ],
                "texts": ["测试文本第一行", "测试文本第二行"],
                "layout": None
            }
        }
        
        # 2. 生成图片哈希值
        print("\n2. 生成图片哈希值")
        # 生成一个测试用的哈希值
        image_hash = hashlib.md5(b"test_image_content").hexdigest()
        print(f"生成图片哈希值: {image_hash}")
        
        # 3. 连接数据库
        print("\n3. 连接数据库")
        await mysql_client.connect()
        print("数据库连接成功")
        
        # 4. 保存OCR结果到数据库
        print("\n4. 保存OCR结果到数据库")
        saved_result = await mysql_client.save_ocr_result("test_task_123", ocr_result, image_hash)
        print(f"保存OCR结果成功")
        
        # 5. 从数据库读取OCR结果
        print("\n5. 从数据库读取OCR结果")
        db_result = await mysql_client.get_ocr_result_by_image_hash(image_hash)
        if db_result and db_result.get("result"):
            print(f"从数据库读取OCR结果成功")
            
            # 检查结果中的字符位置格式
            text_lines = db_result["result"]["result"].get("text_lines", [])
            print(f"读取到 {len(text_lines)} 行文本")
            
            has_correct_format = True
            for i, line in enumerate(text_lines[:2]):  # 只显示前2行
                words = line.get("words", [])
                print(f"第 {i+1} 行: {line.get('text')[:20]}...")
                print(f"   包含 {len(words)} 个字符")
                if words and isinstance(words, list) and len(words) > 0:
                    first_word = words[0]
                    pos = first_word["position"]
                    print(f"   第1个字符位置: {pos}")
                    
                    # 检查格式是否正确：前端期望 [x1, y1, x2, y2] 格式
                    if len(pos) == 4 and all(isinstance(p, (int, float)) for p in pos):
                        print(f"   ✓ 位置格式正确: [x1, y1, x2, y2]")
                    elif len(pos) >= 2 and all(isinstance(p, list) for p in pos):
                        print(f"   ✗ 位置格式不正确: 期望 [x1, y1, x2, y2]，实际是四边形格式")
                        has_correct_format = False
                    else:
                        print(f"   ✗ 位置格式不正确: 未知格式")
                        has_correct_format = False
            
            if has_correct_format:
                print("\n✓ 测试成功: 数据库缓存中的字符位置格式正确")
            else:
                print("\n✗ 测试失败: 数据库缓存中的字符位置格式不正确")
        else:
            print("\n✗ 测试失败: 无法从数据库读取OCR结果")
        
        print("\nOCR内存缓存测试完成")
        
    except Exception as e:
        print(f"测试OCR内存缓存失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await mysql_client.disconnect()
        print("数据库连接关闭成功")

if __name__ == "__main__":
    asyncio.run(test_ocr_memory_cache())
