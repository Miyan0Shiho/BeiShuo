#!/usr/bin/env python3
"""
测试OCR缓存重启后命中情况

该脚本用于测试：
1. 上传图片并进行OCR识别
2. 确保OCR结果被正确保存到数据库
3. 重启后端服务
4. 再次上传同样的图片，验证是否能从数据库缓存中获取结果
5. 验证image_url字段是否被正确保存和返回
"""

import os
import sys
import requests
import time
import hashlib
import base64
import json

# 配置
BASE_URL = "http://localhost:8080"
TEST_IMAGE_PATH = "/Users/liuminxuan/Desktop/团队项目/vertical_1.png"


def read_image(image_path):
    """读取测试图片"""
    print(f"读取图片: {image_path}")
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        return None
    
    with open(image_path, "rb") as f:
        return f.read()


def generate_image_hash(image_content):
    """生成图片哈希值"""
    image_hash = hashlib.md5(image_content).hexdigest()
    print(f"生成图片哈希值: {image_hash}")
    return image_hash


def upload_image(image_content):
    """上传图片"""
    print("\n测试1: 上传图片")
    url = f"{BASE_URL}/api/v1/upload/image"
    files = {
        "file": ("test.png", image_content, "image/png")
    }
    
    response = requests.post(url, files=files)
    print(f"上传图片响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"上传图片响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data.get("image_url")
    else:
        print(f"上传图片失败: {response.text}")
        return None


def start_recognition(image_url, image_hash):
    """开始OCR识别"""
    print(f"\n测试2: 开始OCR识别 (image_hash: {image_hash})")
    url = f"{BASE_URL}/api/v1/recognition/start"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "image_url": image_url,
        "options": {
            "det_mode": "sp",
            "return_position": True,
            "return_choices": True,
            "version": "beta",
            "det_layout": False,
            "only_plain_text": False,
            "return_layout": False,
            "hp_line_words_angel": "left2right",
            "sp_line_words_angel": "top2bottom"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"OCR识别响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"OCR识别响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 检查image_url字段
        if data.get("success") and data.get("data") and data["data"].get("result"):
            image_url_from_result = data["data"]["result"].get("image_url")
            print(f"\n=== 检查image_url字段 ===")
            print(f"从结果中获取的image_url: {image_url_from_result}")
            if image_url_from_result:
                print("✓ image_url字段存在")
                if image_url_from_result.startswith("/uploads/"):
                    print("✓ image_url格式正确，以/uploads/开头")
                else:
                    print(f"✗ image_url格式不正确，预期以/uploads/开头，实际: {image_url_from_result}")
            else:
                print("✗ image_url字段不存在或为空")
        
        return data
    else:
        print(f"OCR识别失败: {response.text}")
        return None


def restart_backend():
    """重启后端服务"""
    print("\n测试3: 重启后端服务")
    # 停止当前运行的后端服务
    os.system("pkill -9 -f 'uvicorn app.main:app'")
    time.sleep(2)
    
    # 启动新的后端服务
    import subprocess
    subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"],
        cwd="/Users/liuminxuan/Desktop/团队项目/python",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待后端服务启动
    print("等待后端服务启动...")
    time.sleep(5)


def main():
    """主函数"""
    print("开始测试OCR缓存重启后命中情况")
    print("=" * 60)
    
    # 1. 读取测试图片
    image_content = read_image(TEST_IMAGE_PATH)
    if not image_content:
        return
    
    # 2. 生成图片哈希值
    image_hash = generate_image_hash(image_content)
    
    # 3. 上传图片
    image_url = upload_image(image_content)
    if not image_url:
        return
    
    # 4. 第一次OCR识别（应该直接识别，不命中缓存）
    first_result = start_recognition(image_url, image_hash)
    if not first_result or not first_result.get("success"):
        return
    
    # 5. 重启后端服务
    restart_backend()
    
    # 6. 上传同一张图片
    image_url = upload_image(image_content)
    if not image_url:
        return
    
    # 7. 第二次OCR识别（应该命中数据库缓存）
    second_result = start_recognition(image_url, image_hash)
    if not second_result or not second_result.get("success"):
        return
    
    # 8. 检查是否是缓存命中
    print("\n测试4: 检查是否命中缓存")
    if "缓存命中" in second_result.get("message", ""):
        print("✓ OCR缓存命中成功!")
    else:
        print("✗ OCR缓存未命中")
    
    print("\n" + "=" * 60)
    print("OCR缓存重启后命中测试完成")


if __name__ == "__main__":
    main()
