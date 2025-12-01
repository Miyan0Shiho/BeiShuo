#!/usr/bin/env python3
"""
创建测试用户账号
"""

import hashlib
import asyncio
from app.client.database_client import DatabaseClient

async def create_test_user():
    """创建测试用户"""
    
    # 创建数据库客户端
    db_client = DatabaseClient()
    
    try:
        # 连接数据库
        await db_client.connect()
        
        # 检查用户是否已存在
        existing_user = await db_client.get_user_by_email("test@example.com")
        if existing_user:
            print(f"✅ 测试用户已存在: ID={existing_user['id']}, 邮箱={existing_user['email']}")
            return existing_user
        
        # 创建测试用户
        password = "test123"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user_data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password_hash": password_hash,
            "role": "user"
        }
        
        new_user = await db_client.create_user(user_data)
        if new_user:
            print(f"✅ 测试用户创建成功: ID={new_user['id']}, 邮箱={new_user['email']}")
            print(f"   用户名: testuser")
            print(f"   密码: test123")
            return new_user
        else:
            print("❌ 创建测试用户失败")
            return None
            
    except Exception as e:
        print(f"❌ 创建测试用户时发生错误: {e}")
        return None
    finally:
        await db_client.close()

if __name__ == "__main__":
    print("开始创建测试用户...")
    user = asyncio.run(create_test_user())
    if user:
        print("✅ 测试用户准备完成")
    else:
        print("❌ 测试用户创建失败")