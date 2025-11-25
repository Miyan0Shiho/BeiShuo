from typing import Optional, Any, Generic, TypeVar, Dict
from pydantic import BaseModel
from app.common.result_code import ResultCode
from datetime import datetime, timezone

T = TypeVar('T')

class ErrorInfo(BaseModel):
    """错误信息"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class Result(BaseModel, Generic[T]):
    """统一响应格式"""
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[ErrorInfo] = None
    timestamp: str
    
    @classmethod
    def ok(cls, data: Optional[T] = None, message: str = "操作成功") -> "Result[T]":
        """成功响应"""
        return cls(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    @classmethod
    def fail(cls, result_code: ResultCode, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> "Result[None]":
        """错误响应"""
        error_info = ErrorInfo(
            code=str(result_code.code),
            message=message or result_code.message,
            details=details
        )
        return cls(
            success=False,
            message=message or result_code.message,
            error=error_info,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    @classmethod
    def fail_with_code(cls, code: int, message: str, details: Optional[Dict[str, Any]] = None) -> "Result[None]":
        """自定义错误响应"""
        error_info = ErrorInfo(
            code=str(code),
            message=message,
            details=details
        )
        return cls(
            success=False,
            message=message,
            error=error_info,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

