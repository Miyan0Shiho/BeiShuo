from typing import Optional
from app.common.result_code import ResultCode

class BusinessException(Exception):
    """业务异常"""
    def __init__(self, result_code: ResultCode, message: Optional[str] = None):
        self.code = result_code.code
        self.message = message or result_code.message
        super().__init__(self.message)

class UnauthorizedException(Exception):
    """未授权异常"""
    def __init__(self, message: str = "未授权，请先登录"):
        self.message = message
        super().__init__(self.message)

