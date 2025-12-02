#!/usr/bin/env python3
"""
实际调试备用模式调用情况
检查备用模式是否真的被调用，以及调用结果
"""

import os
import sys
import asyncio
import base64

# 设置当前目录为python目录
os.chdir('/Users/liuminxuan/Desktop/团队项目/python')

# 添加项目路径
sys.path.insert(0, os.getcwd())

from app.client.kandianguji_ocr_client import KandiangujiOCRClient
from app.api.v1.recognition import _normalize_ocr

async def test_ocr_with_fallback():
    """测试OCR识别和备用模式调用"""
    print("=== OCR识别和备用模式调用测试 ===\n")
    
    # 读取测试图片
    test_image_path = "uploads/017cc466-48f0-4b98-98e4-79c91fcff6bc.jpeg"
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        return
    
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    print(f"✅ 加载测试图片: {test_image_path} (大小: {len(image_data)}字节)\n")
    
    client = KandiangujiOCRClient()
    
    # 主模式参数
    primary_options = {
        "version": "v2",
        "det_mode": "auto",
        "return_position": True
    }
    
    print("=== 主模式测试 ===")
    try:
        ocr_resp = await client.recognize(image_base64, primary_options)
        data = ocr_resp.get("data") or {}
        norm = _normalize_ocr(data)
        
        print(f"主模式原始响应: {ocr_resp}")
        print(f"主模式归一化结果: {norm}")
        print(f"主模式文字长度: {len(norm['full_text'])}")
        print(f"主模式置信度: {norm['confidence']}")
        
        # 检查备用模式触发条件
        should_fallback = not norm["full_text"] and (not norm["text_lines"] or norm["word_count"] == 0)
        print(f"是否应该触发备用模式: {should_fallback}\n")
        
    except Exception as e:
        print(f"主模式失败: {e}\n")
        should_fallback = True
    
    # 如果应该触发备用模式，测试所有备用模式
    if should_fallback:
        print("=== 备用模式测试 ===")
        
        # SP模式
        print("\n1. SP模式测试:")
        sp_options = {**primary_options, "det_mode": "sp", "sp_line_words_angel": "top2bottom"}
        try:
            ocr_resp = await client.recognize(image_base64, sp_options)
            data = ocr_resp.get("data") or {}
            norm = _normalize_ocr(data)
            
            print(f"SP模式原始响应: {ocr_resp}")
            print(f"SP模式归一化结果: {norm}")
            print(f"SP模式文字长度: {len(norm['full_text'])}")
            print(f"SP模式置信度: {norm['confidence']}")
            
        except Exception as e:
            print(f"SP模式失败: {e}")
        
        # HP模式
        print("\n2. HP模式测试:")
        hp_options = {**primary_options, "det_mode": "hp", "hp_line_words_angel": "left2right"}
        try:
            ocr_resp = await client.recognize(image_base64, hp_options)
            data = ocr_resp.get("data") or {}
            norm = _normalize_ocr(data)
            
            print(f"HP模式原始响应: {ocr_resp}")
            print(f"HP模式归一化结果: {norm}")
            print(f"HP模式文字长度: {len(norm['full_text'])}")
            print(f"HP模式置信度: {norm['confidence']}")
            
        except Exception as e:
            print(f"HP模式失败: {e}")
        
        # Beta+SP模式
        print("\n3. Beta+SP模式测试:")
        beta_sp_options = {**primary_options, "version": "beta", "det_mode": "sp", "sp_line_words_angel": "top2bottom"}
        try:
            ocr_resp = await client.recognize(image_base64, beta_sp_options)
            data = ocr_resp.get("data") or {}
            norm = _normalize_ocr(data)
            
            print(f"Beta+SP模式原始响应: {ocr_resp}")
            print(f"Beta+SP模式归一化结果: {norm}")
            print(f"Beta+SP模式文字长度: {len(norm['full_text'])}")
            print(f"Beta+SP模式置信度: {norm['confidence']}")
            
        except Exception as e:
            print(f"Beta+SP模式失败: {e}")
    
    print("\n=== 测试完成 ===")

async def main():
    """主函数"""
    await test_ocr_with_fallback()

if __name__ == "__main__":
    asyncio.run(main())