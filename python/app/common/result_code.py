from enum import Enum

class ResultCode(Enum):
    """响应码枚举"""
    SUCCESS = (200, "success")
    BAD_REQUEST = (400, "请求参数错误")
    UNAUTHORIZED = (401, "未授权，请先登录")
    FORBIDDEN = (403, "无权限访问")
    NOT_FOUND = (404, "资源不存在")
    INTERNAL_SERVER_ERROR = (500, "服务器内部错误")
    
    # 业务错误码
    USER_NOT_FOUND = (1001, "用户不存在")
    USER_ALREADY_EXISTS = (1002, "用户已存在")
    INVALID_CREDENTIALS = (1003, "邮箱或密码错误")
    TOKEN_INVALID = (1004, "Token无效或已过期")
    
    INSCRIPTION_NOT_FOUND = (2001, "碑文不存在")
    INSCRIPTION_ALREADY_EXISTS = (2002, "碑文已存在")
    
    KNOWLEDGE_NOT_FOUND = (3001, "知识库内容不存在")
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

