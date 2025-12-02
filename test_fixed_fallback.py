#!/usr/bin/env python3
"""
测试修复后的备用模式调用
"""

import os
import sys
import asyncio
import base64
import requests

# 设置当前目录为python目录
os.chdir('/Users/liuminxuan/Desktop/团队项目/python')

# 添加项目路径
sys.path.insert(0, os.getcwd())

async def test_fixed_fallback():
    """测试修复后的备用模式调用"""
    print("=== 测试修复后的备用模式调用 ===\n")
    
    # 读取测试图片
    test_image_path = "uploads/017cc466-48f0-4b98-98e4-79c91fcff6bc.jpeg"
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图片不存在: {test_image_path}")
        return
    
    with open(test_image_path, "rb") as f:
        image_data = f.read()
    
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    print(f"✅ 加载测试图片: {test_image_path} (大小: {len(image_data)}字节)\n")
    
    # 调用后端API进行测试
    url = "http://localhost:8080/api/v1/recognition/start"
    headers = {
        "Content-Type": "application/json",
        "X-User-Id": "1"
    }
    
    payload = {
        "image_url": None,
        "image_base64": image_base64,
        "filename": "test_image.jpeg"
    }
    
    print("=== 调用后端API进行OCR识别 ===")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据: {result}")
            
            if result.get("success"):
                recognition_result = result.get("data", {}).get("result", {})
                text = recognition_result.get("text", "")
                confidence = recognition_result.get("confidence", 0.0)
                word_count = recognition_result.get("word_count", 0)
                
                print(f"\n✅ OCR识别成功!")
                print(f"识别文字: {text}")
                print(f"文字长度: {len(text)}")
                print(f"置信度: {confidence}")
                print(f"字数统计: {word_count}")
                
                if len(text) > 0:
                    print("\n🎉 备用模式修复成功！图片中的文字被正确识别！")
                else:
                    print("\n❌ 备用模式仍然失败，文字为空")
            else:
                print(f"❌ 识别失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

async def main():
    """主函数"""
    await test_fixed_fallback()

if __name__ == "__main__":
    asyncio.run(main())