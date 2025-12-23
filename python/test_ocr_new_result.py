#!/usr/bin/env python3
"""
测试新的OCR结果保存和读取，确保字符位置信息被正确保存
"""
import asyncio
import traceback
import hashlib
import base64
from app.client.mysql_client import mysql_client
from app.client.kandianguji_ocr_client import KandiangujiOCRClient

async def test_new_ocr_result():
    """测试新的OCR结果保存和读取"""
    print("开始测试新的OCR结果保存和读取")
    
    try:
        # 1. 读取测试图片
        print("\n1. 读取测试图片")
        image_path = "/Users/liuminxuan/Desktop/团队项目/vertical_1.png"
        print(f"读取图片: {image_path}")
        
        with open(image_path, "rb") as f:
            content = f.read()
        
        # 2. 生成图片哈希值
        print("\n2. 生成图片哈希值")
        image_hash = hashlib.md5(content).hexdigest()
        print(f"生成图片哈希值: {image_hash}")
        
        # 3. 连接数据库
        print("\n3. 连接数据库")
        await mysql_client.connect()
        print("数据库连接成功")
        
        # 4. 使用模拟OCR结果，包含字符位置信息
        print("\n4. 使用模拟OCR结果")
        print("创建包含字符位置信息的模拟OCR结果...")
        
        # 模拟OCR结果，包含详细的字符位置信息
        data = {
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
            ]
        }
        
        # 打印OCR模拟结果，查看字符位置信息
        print("\n5. 查看OCR模拟结果")
        text_lines = data.get("text_lines", [])
        print(f"识别到 {len(text_lines)} 行文本")
        
        # 检查原始结果中是否包含字符位置信息
        has_word_positions = False
        for i, line in enumerate(text_lines[:2]):  # 只显示前2行
            words = line.get("words", [])
            print(f"第 {i+1} 行: {line.get('text')[:20]}...")
            print(f"   包含 {len(words)} 个字符")
            if words and isinstance(words, list) and len(words) > 0:
                first_word = words[0]
                if "position" in first_word and isinstance(first_word["position"], list):
                    print(f"   第1个字符位置: {first_word['position']}")
                    has_word_positions = True
        
        if has_word_positions:
            print("✓ 原始OCR结果包含字符位置信息")
        else:
            print("✗ 原始OCR结果不包含字符位置信息")
        
        # 5. 保存OCR结果到数据库
        print("\n6. 保存OCR结果到数据库")
        result_data = {
            "request": {
                "image_url": "/uploads/test_image.png",
                "options": {}
            },
            "result": data
        }
        saved_result = await mysql_client.save_ocr_result("test_task_new", result_data, image_hash, content)
        print(f"保存OCR结果成功: {saved_result}")
        
        # 6. 从数据库读取OCR结果
        print("\n7. 从数据库读取OCR结果")
        ocr_result = await mysql_client.get_ocr_result_by_image_hash(image_hash)
        if ocr_result:
            print(f"✓ 从数据库读取OCR结果成功")
            
            # 检查读取的结果中是否包含字符位置信息
            result = ocr_result.get("result", {})
            text_lines_result = result.get("result", {}).get("text_lines", [])
            print(f"读取到 {len(text_lines_result)} 行文本")
            
            has_word_positions_in_result = False
            has_correct_format = False
            for i, line in enumerate(text_lines_result[:2]):  # 只显示前2行
                words = line.get("words", [])
                print(f"第 {i+1} 行: {line.get('text')[:20]}...")
                print(f"   包含 {len(words)} 个字符")
                if words and isinstance(words, list) and len(words) > 0:
                    first_word = words[0]
                    if "position" in first_word and isinstance(first_word["position"], list):
                        pos = first_word["position"]
                        print(f"   第1个字符位置: {pos}")
                        has_word_positions_in_result = True
                        
                        # 检查格式是否正确：前端期望 [x1, y1, x2, y2] 格式
                        if len(pos) == 4 and all(isinstance(p, (int, float)) for p in pos):
                            print(f"   ✓ 位置格式正确: [x1, y1, x2, y2]")
                            has_correct_format = True
                        elif len(pos) >= 2 and all(isinstance(p, list) for p in pos):
                            print(f"   ✗ 位置格式不正确: 期望 [x1, y1, x2, y2]，实际是四边形格式")
                        else:
                            print(f"   ✗ 位置格式不正确: 未知格式")
            
            if has_word_positions_in_result:
                if has_correct_format:
                    print("\n✓ 测试成功: 字符位置信息已正确保存和转换为前端期望格式")
                else:
                    print("\n✗ 测试失败: 字符位置信息保存成功，但格式不符合前端期望")
            else:
                print("\n✗ 测试失败: 字符位置信息丢失")
        else:
            print("\n✗ 测试失败: 无法从数据库读取OCR结果")
        
        print("\n测试完成")
        
    except Exception as e:
        print(f"测试失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await mysql_client.disconnect()
        print("数据库连接关闭成功")

if __name__ == "__main__":
    asyncio.run(test_new_ocr_result())
