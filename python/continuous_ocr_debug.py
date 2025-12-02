#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续OCR调试脚本
用于持续调用OCR API识别多宝塔碑.jpg，找出无法识别文本的根本原因
"""

import asyncio
import base64
import json
import time
import aiohttp
import os
from pathlib import Path

# 配置参数
CONFIG = {
    "image_path": "/Users/liuminxuan/Desktop/团队项目/uploads/多宝塔碑.jpg",
    "ocr_token": "c6204f29-da89-4e36-8762-8fc1528f89d2",
    "ocr_email": "13764120319",
    "base_url": "https://ocr-api.kandianguji.com",
    "timeout": 30,
    "max_retries": 3
}

async def call_ocr_api(image_base64, options, session, attempt=1):
    """调用OCR API"""
    url = f"{CONFIG['base_url']}/api/ocr"
    
    payload = {
        "token": CONFIG['ocr_token'],
        "email": CONFIG['ocr_email'],
        "image": image_base64,
        **options
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=CONFIG['timeout'])) as response:
            status = response.status
            response_text = await response.text()
            
            try:
                response_data = json.loads(response_text)
            except:
                response_data = {"error": "Invalid JSON response", "raw": response_text}
            
            return {
                "status": status,
                "data": response_data,
                "headers": dict(response.headers),
                "attempt": attempt
            }
    except asyncio.TimeoutError:
        return {"error": "Timeout", "attempt": attempt}
    except Exception as e:
        return {"error": str(e), "attempt": attempt}

async def test_ocr_with_options(image_base64, options_list, session):
    """使用不同选项测试OCR"""
    results = {}
    
    for i, options in enumerate(options_list):
        print(f"\n=== 测试组合 {i+1}/{len(options_list)} ===")
        print(f"选项: {options}")
        
        # 重试机制
        for attempt in range(1, CONFIG['max_retries'] + 1):
            result = await call_ocr_api(image_base64, options, session, attempt)
            
            if "error" not in result:
                break
            
            if attempt < CONFIG['max_retries']:
                print(f"第{attempt}次尝试失败: {result['error']}, 重试...")
                await asyncio.sleep(1)
        
        # 分析结果
        if "error" in result:
            print(f"❌ 所有尝试均失败: {result['error']}")
            results[f"组合{i+1}"] = {"error": result["error"]}
            continue
        
        status = result["status"]
        data = result["data"]
        
        print(f"状态码: {status}")
        print(f"响应消息: {data.get('message', 'N/A')}")
        print(f"响应码: {data.get('code', 'N/A')}")
        
        # 检查数据
        ocr_data = data.get("data", {})
        if isinstance(ocr_data, list):
            data_length = len(ocr_data)
            print(f"数据长度: {data_length}")
            
            if data_length > 0:
                print("✅ 数据不为空，检查内容...")
                for idx, item in enumerate(ocr_data):
                    print(f"  项目 {idx+1}:")
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key in ["text", "texts", "text_lines", "full_text"]:
                                if value:
                                    print(f"    {key}: {value}")
                                else:
                                    print(f"    {key}: 空")
                            elif key in ["height", "width", "confidence"]:
                                print(f"    {key}: {value}")
            else:
                print("❌ 数据为空列表")
        else:
            print("⚠️ 数据格式不是列表")
            print(f"数据内容: {ocr_data}")
        
        results[f"组合{i+1}"] = {
            "status": status,
            "message": data.get("message"),
            "code": data.get("code"),
            "data_length": len(ocr_data) if isinstance(ocr_data, list) else 0,
            "data_sample": ocr_data[:1] if isinstance(ocr_data, list) and len(ocr_data) > 0 else None
        }
        
        # 保存详细结果
        with open(f"ocr_debug_result_{i+1}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        await asyncio.sleep(0.5)  # 避免请求过快
    
    return results

def load_image():
    """加载图片并转换为base64"""
    image_path = Path(CONFIG['image_path'])
    if not image_path.exists():
        print(f"❌ 图片不存在: {image_path}")
        return None
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    print(f"✅ 图片加载成功，大小: {len(image_data)} bytes")
    return image_base64

def generate_test_options():
    """生成测试选项组合"""
    base_options = {
        "return_position": True,
        "image_size": 2000
    }
    
    # 测试不同的检测模式
    test_combinations = [
        # 基础模式
        {"det_mode": "auto", "version": "v2"},
        
        # SP模式（竖排）
        {"det_mode": "sp", "sp_line_words_angel": "top2bottom", "version": "v2"},
        {"det_mode": "sp", "sp_line_words_angel": "top2bottom", "version": "beta"},
        
        # HP模式（横排）
        {"det_mode": "hp", "hp_line_words_angel": "left2right", "version": "v2"},
        {"det_mode": "hp", "hp_line_words_angel": "left2right", "version": "beta"},
        
        # 文档模式
        {"det_mode": "document", "version": "v2"},
        {"det_mode": "document", "version": "beta"},
        
        # 手写模式
        {"det_mode": "handwriting", "version": "v2"},
        {"det_mode": "handwriting", "version": "beta"},
        
        # 古籍模式
        {"det_mode": "ancient", "version": "v2"},
        {"det_mode": "ancient", "version": "beta"},
        
        # 高级选项
        {"det_mode": "sp", "return_choices": True, "det_layout": True, "version": "v2"},
        {"det_mode": "sp", "only_plain_text": True, "version": "v2"},
        {"det_mode": "sp", "return_layout": True, "version": "v2"},
        {"det_mode": "sp", "auto_insert_space": True, "version": "v2"},
        
        # 不同图像尺寸
        {"det_mode": "sp", "image_size": 1000, "version": "v2"},
        {"det_mode": "sp", "image_size": 3000, "version": "v2"},
        {"det_mode": "sp", "image_size": 4000, "version": "v2"},
    ]
    
    # 合并基础选项
    return [{**base_options, **combo} for combo in test_combinations]

async def main():
    """主函数"""
    print("🚀 开始连续OCR调试...")
    print(f"图片路径: {CONFIG['image_path']}")
    print(f"OCR服务: {CONFIG['base_url']}")
    
    # 加载图片
    image_base64 = load_image()
    if not image_base64:
        return
    
    # 生成测试选项
    test_options = generate_test_options()
    print(f"生成 {len(test_options)} 个测试组合")
    
    # 创建会话
    async with aiohttp.ClientSession() as session:
        # 多次测试
        for test_round in range(1, 4):  # 进行3轮测试
            print(f"\n{'='*60}")
            print(f"第 {test_round} 轮测试")
            print(f"{'='*60}")
            
            start_time = time.time()
            results = await test_ocr_with_options(image_base64, test_options, session)
            end_time = time.time()
            
            print(f"\n第 {test_round} 轮测试完成，耗时: {end_time - start_time:.2f}秒")
            
            # 分析结果
            successful_tests = 0
            for key, result in results.items():
                if "error" not in result and result.get("data_length", 0) > 0:
                    successful_tests += 1
            
            print(f"成功识别测试: {successful_tests}/{len(test_options)}")
            
            # 保存汇总结果
            with open(f"ocr_debug_summary_round_{test_round}.json", "w", encoding="utf-8") as f:
                json.dump({
                    "test_round": test_round,
                    "total_tests": len(test_options),
                    "successful_tests": successful_tests,
                    "results": results,
                    "timestamp": time.time()
                }, f, indent=2, ensure_ascii=False)
            
            if test_round < 3:
                print(f"等待5秒后进行下一轮测试...")
                await asyncio.sleep(5)
    
    print("\n🎉 所有测试完成！")
    print("检查生成的JSON文件以获取详细结果")

if __name__ == "__main__":
    asyncio.run(main())