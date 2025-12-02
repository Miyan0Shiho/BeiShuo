"""
更新测试用户密码为bcrypt加密
"""
import asyncio
import bcrypt
from app.client.database_client import DatabaseClient

async def update_test_user_password():
    """更新测试用户密码为bcrypt加密"""
    db_client = DatabaseClient()
    
    try:
        # 查询测试用户
        user = await db_client.get_user_by_email("test@example.com")
        if not user:
            print("测试用户不存在")
            return False
        
        print(f"找到测试用户: ID={user['id']}, 邮箱={user['email']}")
        print(f"当前密码哈希: {user['password_hash']}")
        
        # 生成bcrypt哈希
        hashed_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(f"新的bcrypt哈希: {hashed_password}")
        
        # 更新用户密码
        update_data = {
            "password_hash": hashed_password
        }
        
        updated_user = await db_client.update_user(user['id'], update_data)
        if updated_user:
            print("测试用户密码已成功更新为bcrypt加密")
            print(f"更新后的密码哈希: {updated_user['password_hash']}")
            return True
        else:
            print("更新用户密码失败")
            return False
        
    except Exception as e:
        print(f"更新测试用户密码时出错: {e}")
        return False
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
    print("=== 更新测试用户密码 ===")
    success = asyncio.run(update_test_user_password())
    
    if success:
        print("\n=== 验证测试用户 ===")
        asyncio.run(verify_test_user())