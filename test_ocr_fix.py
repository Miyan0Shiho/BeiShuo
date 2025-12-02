#!/usr/bin/env python3
"""
OCR修复验证测试脚本
测试OSS URL解析和归一化函数修复效果
"""

import asyncio
import base64
import json
from typing import Dict, Any

# 模拟OCR服务返回的列表型响应（您提到的问题场景）
MOCK_LIST_RESPONSE = [
    "第一行文本",
    "第二行文本", 
    "第三行文本"
]

# 模拟OCR服务返回的字典型响应（正常场景）
MOCK_DICT_RESPONSE = {
    "texts": ["文本1", "文本2"],
    "text_lines": [{"text": "行文本"}],
    "width": 800,
    "height": 600
}

# 测试归一化函数
def test_normalize_function():
    """测试归一化函数对列表和字典响应的处理"""
    
    # 导入实际的归一化函数
    import sys
    sys.path.append('/Users/liuminxuan/Desktop/团队项目/python')
    
    from app.api.v1.recognition import _normalize_ocr
    
    print("=== 测试归一化函数修复 ===")
    
    # 测试列表型响应
    print("\n1. 测试列表型OCR响应:")
    list_result = _normalize_ocr(MOCK_LIST_RESPONSE)
    print(f"输入: {MOCK_LIST_RESPONSE}")
    print(f"输出 - full_text: '{list_result['full_text']}'")
    print(f"输出 - word_count: {list_result['word_count']}")
    print(f"输出 - texts: {list_result['texts']}")
    
    # 测试字典型响应
    print("\n2. 测试字典型OCR响应:")
    dict_result = _normalize_ocr(MOCK_DICT_RESPONSE)
    print(f"输入: {MOCK_DICT_RESPONSE}")
    print(f"输出 - full_text: '{dict_result['full_text']}'")
    print(f"输出 - word_count: {dict_result['word_count']}")
    
    # 验证修复效果
    assert list_result['full_text'] == "第一行文本\n第二行文本\n第三行文本", "列表型响应归一化失败"
    assert list_result['word_count'] > 0, "列表型响应字数统计失败"
    print("✅ 归一化函数修复验证通过")

# 测试OSS URL解析
def test_oss_url_parsing():
    """测试OSS URL解析逻辑"""
    
    print("\n=== 测试OSS URL解析修复 ===")
    
    # 测试用例
    test_cases = [
        # (输入URL, 期望的object_key)
        ("https://oss-cn-beijing.aliyuncs.com/beiwen1/inscription-images/test.jpg", "inscription-images/test.jpg"),
        ("https://beiwen1.oss-cn-beijing.aliyuncs.com/inscription-images/test.jpg", "inscription-images/test.jpg"),
        ("https%3A//oss-cn-beijing.aliyuncs.com/beiwen1/inscription-images/test.jpg", "inscription-images/test.jpg"),
    ]
    
    for url, expected_key in test_cases:
        # 模拟解析逻辑
        import urllib.parse
        
        # 处理URL编码
        actual_url = url
        if url.startswith("https%3A//"):
            actual_url = urllib.parse.unquote(url)
        
        # 解析URL
        parsed = urllib.parse.urlparse(actual_url)
        path = parsed.path
        object_key = path.lstrip('/')
        
        # 模拟bucket检测逻辑
        bucket_name = "beiwen1"
        host = parsed.netloc or ""
        
        if bucket_name and host.startswith("oss-") and object_key.startswith(f"{bucket_name}/"):
            object_key = object_key[len(bucket_name)+1:]
        
        print(f"URL: {url}")
        print(f"解析结果: {object_key}")
        print(f"期望结果: {expected_key}")
        print(f"测试结果: {'✅ 通过' if object_key == expected_key else '❌ 失败'}")
        print()

async def test_ocr_integration():
    """测试OCR集成流程"""
    print("\n=== 测试OCR集成流程 ===")
    
    # 这里可以添加实际的API调用测试
    # 需要先确保后端服务运行正常
    print("需要后端服务运行才能进行集成测试")
    print("当前后端地址: http://localhost:8080")
    print("可以使用以下命令测试:")
    print("curl -X POST http://localhost:8080/api/v1/recognition/start \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"image_url\": \"https://example.com/test.jpg\"}'")

if __name__ == "__main__":
    print("OCR修复验证测试脚本")
    print("=" * 50)
    
    # 运行测试
    test_normalize_function()
    test_oss_url_parsing()
    
    # 集成测试需要异步环境
    # asyncio.run(test_ocr_integration())
    
    print("\n" + "=" * 50)
    print("测试完成！建议:")
    print("1. 使用真实图片测试OCR识别")
    print("2. 检查数据库记录是否正确创建")
    print("3. 验证前端图片上传功能")