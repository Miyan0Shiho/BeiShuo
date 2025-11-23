from typing import List, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class PageResult(BaseModel, Generic[T]):
    """分页结果"""
    list: List[T]
    total: int
    page: int
    size: int
    totalPages: int

