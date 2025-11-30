import bcrypt
from app.utils.logger import logger

class PasswordUtil:
    """密码工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        try:
            # 使用bcrypt直接加密密码
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"密码哈希失败: {e}")
            raise
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            # 使用bcrypt直接验证密码
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False

