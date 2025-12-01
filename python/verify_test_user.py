#!/usr/bin/env python3
"""
验证测试用户密码
"""

import hashlib
import asyncio
from app.client.database_client import DatabaseClient

async def verify_test_user():
    """验证测试用户密码"""
    
    # 创建数据库客户端
    db_client = DatabaseClient()
    
    try:
        # 连接数据库
        await db_client.connect()
        
        # 查询测试用户
        user = await db_client.get_user_by_email("test@example.com")
        if not user:
            print("❌ 测试用户不存在")
            return False
        
        print(f"✅ 找到测试用户: ID={user['id']}, 邮箱={user['email']}")
        print(f"   用户名: {user.get('name', 'N/A')}")
        print(f"   密码哈希: {user.get('password_hash', 'N/A')}")
        
        # 验证密码
        test_password = "test123"
        password_hash = hashlib.sha256(test_password.encode()).hexdigest()
        
        if user.get('password_hash') == password_hash:
            print("✅ 密码验证成功")
            return True
        else:
            print("❌ 密码验证失败")
            print(f"   数据库中的哈希: {user.get('password_hash')}")
            print(f"   测试密码的哈希: {password_hash}")
            return False
            
    except Exception as e:
        print(f"❌ 验证测试用户时发生错误: {e}")
        return False
    finally:
        await db_client.close()

if __name__ == "__main__":
    print("开始验证测试用户...")
    success = asyncio.run(verify_test_user())
    if success:
        print("✅ 测试用户验证完成")
    else:
        print("❌ 测试用户验证失败")