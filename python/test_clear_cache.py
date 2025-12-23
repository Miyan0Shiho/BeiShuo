#!/usr/bin/env python3
"""
测试OCR缓存清除功能
直接测试API端点的功能
"""

import requests

def test_clear_cache():
    """测试清除OCR缓存功能"""
    print("开始测试OCR缓存清除功能")
    
    # 1. 调用清除缓存API
    print("1. 调用清除缓存API")
    response = requests.delete("http://localhost:8080/api/v1/recognition/cache/clear")
    print(f"API响应状态码: {response.status_code}")
    print(f"API响应内容: {response.text}")
    
    # 2. 验证响应是否正确
    print("\n2. 验证响应是否正确")
    response_json = response.json()
    if response_json.get("success"):
        print("✓ API调用成功")
        print(f"  消息: {response_json.get('message')}")
        print(f"  清除的缓存数量: {response_json.get('data', {}).get('cleared_count')}")
    else:
        print("✗ API调用失败")
        print(f"  错误: {response_json.get('error')}")
    
    print("\nOCR缓存清除功能测试完成")

if __name__ == "__main__":
    test_clear_cache()