#!/usr/bin/env python3
"""
OCR缓存功能测试脚本
测试连续上传相同图片时是否能够正确缓存和复用OCR结果
"""

import requests
import base64
import time
import json
from app.config import settings

# 构建数据库配置
DATABASE_CONFIG = {
    "host": settings.mysql_host,
    "port": settings.mysql_port,
    "user": settings.mysql_user,
    "password": settings.mysql_password,
    "database": settings.mysql_database
}

def get_auth_token():
    """获取认证token"""
    base_url = "http://localhost:8080/api/v1"
    
    # 使用测试账号登录
    login_data = {
        "email": "test@example.com",
        "password": "test123",
        "remember_me": False
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                token = result["data"]["token"]
                print(f"✅ 登录成功，获取到Token: {token[:20]}...")
                return token
            else:
                print(f"❌ 登录失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 登录异常: {e}")
    
    return None

def test_ocr_cache():
    """测试OCR缓存功能"""
    
    # 后端API地址
    base_url = "http://localhost:8080/api/v1"
    
    # 获取认证token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证token，测试终止")
        return
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 准备测试图片（使用一个简单的base64编码的测试图片）
    # 这里使用一个1x1像素的PNG图片作为测试
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # 第一次OCR请求
    print("=== 第一次OCR请求 ===")
    response1 = requests.post(
        f"{base_url}/recognition/start",
        headers=headers,
        json={
            "image_base64": test_image_base64,
            "options": {
                "det_mode": "auto",
                "return_position": True
            }
        }
    )
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"第一次请求结果: {json.dumps(result1, ensure_ascii=False, indent=2)}")
        
        # 检查是否命中缓存
        cache_hit1 = result1.get('cache_hit', False)
        print(f"第一次请求缓存命中: {cache_hit1}")
        
        # 等待1秒
        time.sleep(1)
        
        # 第二次OCR请求（相同图片）
        print("\n=== 第二次OCR请求（相同图片） ===")
        response2 = requests.post(
            f"{base_url}/recognition/start",
            headers=headers,
            json={
                "image_base64": test_image_base64,
                "options": {
                    "det_mode": "auto",
                    "return_position": True
                }
            }
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"第二次请求结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
            
            # 检查是否命中缓存
            cache_hit2 = result2.get('cache_hit', False)
            print(f"第二次请求缓存命中: {cache_hit2}")
            
            # 验证缓存功能
            if cache_hit1 == False and cache_hit2 == True:
                print("\n✅ 缓存功能正常：第一次请求未命中缓存，第二次请求命中缓存")
                
                # 验证结果一致性
                if result1.get('full_text') == result2.get('full_text'):
                    print("✅ 缓存结果一致性验证通过")
                else:
                    print("❌ 缓存结果不一致")
                    
            elif cache_hit1 == True and cache_hit2 == True:
                print("\n⚠️ 第一次请求就命中缓存，可能图片已存在于缓存中")
                
            else:
                print(f"\n❌ 缓存功能异常：第一次命中={cache_hit1}, 第二次命中={cache_hit2}")
                
        else:
            print(f"第二次请求失败: {response2.status_code} - {response2.text}")
            
    else:
        print(f"第一次请求失败: {response1.status_code} - {response1.text}")

def check_cache_data():
    """检查缓存数据"""
    print("\n=== 检查缓存数据 ===")
    
    # 查询数据库中的缓存记录
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.client.database_client import DatabaseClient
    from app.config import settings
    
    # 构建数据库配置
    DATABASE_CONFIG = {
        'host': settings.mysql_host,
        'port': settings.mysql_port,
        'user': settings.mysql_user,
        'password': settings.mysql_password,
        'database': settings.mysql_database
    }
    
    try:
        db_client = DatabaseClient(DATABASE_CONFIG)
        
        # 查询ocr_images表
        ocr_images_query = "SELECT * FROM ocr_images ORDER BY created_at DESC LIMIT 5"
        ocr_images_result = db_client.execute_query(ocr_images_query)
        
        print(f"ocr_images表记录数: {len(ocr_images_result)}")
        for i, record in enumerate(ocr_images_result):
            print(f"记录 {i+1}: {record}")
        
        # 查询ocr_jobs表
        ocr_jobs_query = "SELECT * FROM ocr_jobs ORDER BY created_at DESC LIMIT 5"
        ocr_jobs_result = db_client.execute_query(ocr_jobs_query)
        
        print(f"\nocr_jobs表记录数: {len(ocr_jobs_result)}")
        for i, record in enumerate(ocr_jobs_result):
            print(f"记录 {i+1}: {record}")
            # 解析params字段
            if record[3]:  # params字段
                try:
                    params = json.loads(record[3])
                    print(f"    params: {json.dumps(params, ensure_ascii=False)}")
                except:
                    print(f"    params: {record[3]}")
        
        db_client.close()
        
    except Exception as e:
        print(f"检查缓存数据失败: {e}")

if __name__ == "__main__":
    print("开始测试OCR缓存功能...")
    
    try:
        # 测试缓存功能
        test_ocr_cache()
        
        # 检查缓存数据
        check_cache_data()
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()