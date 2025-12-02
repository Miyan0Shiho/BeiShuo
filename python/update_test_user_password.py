#!/usr/bin/env python3
"""
更新测试用户密码
"""

import hashlib
import asyncio
from app.client.database_client import DatabaseClient

async def update_test_user_password():
    """更新测试用户密码"""
    
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
        
        # 更新密码
        new_password = "test123"
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        update_data = {
            "password_hash": password_hash
        }
        
        updated_user = await db_client.update_user(user['id'], update_data)
        if updated_user:
            print("✅ 密码更新成功")
            print(f"   新密码: {new_password}")
            print(f"   新密码哈希: {password_hash}")
            return True
        else:
            print("❌ 密码更新失败")
            return False
            
    except Exception as e:
        print(f"❌ 更新测试用户密码时发生错误: {e}")
        return False
    finally:
        await db_client.close()

if __name__ == "__main__":
    print("开始更新测试用户密码...")
    success = asyncio.run(update_test_user_password())
    if success:
        print("✅ 测试用户密码更新完成")
    else:
        print("❌ 测试用户密码更新失败")