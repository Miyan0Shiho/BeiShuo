#!/usr/bin/env python3
"""
完整测试OCR功能的脚本，使用vertical_1.png图片
"""
import asyncio
import traceback
import hashlib
from app.client.mysql_client import mysql_client
from app.client.kandianguji_ocr_client import KandiangujiOCRClient

async def test_ocr_full():
    """完整测试OCR功能"""
    print("开始完整测试OCR功能")
    
    try:
        # 1. 读取测试图片
        print("\n测试1: 读取测试图片")
        image_path = "/Users/liuminxuan/Desktop/团队项目/vertical_1.png"
        print(f"读取图片: {image_path}")
        
        with open(image_path, "rb") as f:
            content = f.read()
        
        # 2. 生成图片哈希值
        print("\n测试2: 生成图片哈希值")
        image_hash = hashlib.md5(content).hexdigest()
        print(f"生成图片哈希值: {image_hash}")
        
        # 3. 连接数据库
        print("\n测试3: 连接数据库")
        await mysql_client.connect()
        print("数据库连接成功")
        
        # 4. 检查数据库缓存
        print("\n测试4: 检查数据库缓存")
        ocr_result = await mysql_client.get_ocr_result_by_image_hash(image_hash)
        if ocr_result:
            print(f"数据库缓存命中成功: {ocr_result}")
        else:
            print("数据库缓存未命中，将执行OCR识别")
            
            # 5. 执行OCR识别
            print("\n测试5: 执行OCR识别")
            client = KandiangujiOCRClient()
            
            # 将图片转换为base64
            import base64
            image_base64 = base64.b64encode(content).decode("utf-8")
            
            # 执行OCR识别
            print("执行OCR识别...")
            ocr_resp = await client.recognize(image_base64, {
                "version": "v2",
                "det_mode": "sp",
                "return_position": True,
                "return_choices": False,
                "det_layout": False,
                "only_plain_text": False,
                "return_layout": False,
                "auto_insert_space": False,
                "hp_line_words_angel": "left2right",
                "sp_line_words_angel": "top2bottom"
            })
            print(f"OCR识别成功: {ocr_resp}")
            
            # 6. 保存OCR结果到数据库
            print("\n测试6: 保存OCR结果到数据库")
            result_data = {
                "result": ocr_resp.get("data", {})
            }
            saved_result = await mysql_client.save_ocr_result("test_task_123", result_data, image_hash, content)
            print(f"保存OCR结果成功: {saved_result}")
            
            # 7. 再次检查数据库缓存
            print("\n测试7: 再次检查数据库缓存")
            ocr_result_again = await mysql_client.get_ocr_result_by_image_hash(image_hash)
            if ocr_result_again:
                print(f"数据库缓存命中成功: {ocr_result_again}")
            else:
                print("数据库缓存未命中，测试失败")
        
        print("\n完整OCR功能测试完成")
        
    except Exception as e:
        print(f"测试OCR功能失败: {e}")
        traceback.print_exc()
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await mysql_client.disconnect()
        print("数据库连接关闭成功")

if __name__ == "__main__":
    asyncio.run(test_ocr_full())