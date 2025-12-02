"""
创建测试用户脚本 - 使用bcrypt加密
"""
import asyncio
import bcrypt
from app.client.database_client import DatabaseClient
from app.config import settings

async def create_test_user():
    """创建测试用户"""
    db_client = DatabaseClient()
    
    try:
        # 检查用户是否已存在
        existing_user = await db_client.get_user_by_email("test@example.com")
        if existing_user:
            print(f"测试用户已存在: ID={existing_user['id']}, 邮箱={existing_user['email']}")
            
            # 更新密码为正确的bcrypt哈希
            hashed_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # 更新用户密码
            await db_client.execute_query(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (hashed_password, "test@example.com")
            )
            print("测试用户密码已更新为bcrypt加密")
            return existing_user
        
        # 创建新用户
        hashed_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_data = {
            "email": "test@example.com",
            "password_hash": hashed_password,
            "username": "testuser"
        }
        
        user = await db_client.create_user(user_data)
        if user:
            print(f"测试用户创建成功: ID={user['id']}, 邮箱={user['email']}")
        else:
            print("测试用户创建失败")
        
        return user
        
    except Exception as e:
        print(f"创建测试用户时出错: {e}")
        return None
    finally:
        await db_client.close()

async def verify_test_user():
    """验证测试用户密码"""
    db_client = DatabaseClient()
    
    try:
        # 查询测试用户
        user = await db_client.get_user_by_email("test@example.com")
        if not user:
            print("测试用户不存在")
            return False
        
        print(f"找到测试用户: ID={user['id']}, 邮箱={user['email']}")
        print(f"密码哈希: {user['password_hash']}")
        
        # 验证密码
        is_valid = bcrypt.checkpw("test123".encode('utf-8'), user['password_hash'].encode('utf-8'))
        print(f"密码验证结果: {'成功' if is_valid else '失败'}")
        
        return is_valid
        
    except Exception as e:
        print(f"验证测试用户时出错: {e}")
        return False
    finally:
        await db_client.close()

if __name__ == "__main__":
    print("=== 创建测试用户 ===")
    user = asyncio.run(create_test_user())
    
    print("\n=== 验证测试用户 ===")
    asyncio.run(verify_test_user())