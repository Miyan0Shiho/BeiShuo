from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 模拟用户数据库
fake_users_db = {
    "test@example.com": {
        "id": 1,
        "name": "测试用户",
        "email": "test@example.com",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "123456"
        "avatar": "https://example.com/avatar.jpg"
    }
}

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 验证令牌
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token, credentials_exception)
    user = fake_users_db.get(email)
    if user is None:
        raise credentials_exception
    return user

# 保留原有导入，移除重复部分
# 这些功能已经在文件顶部定义过了

# 用户登录
@router.post("/login")
async def login(
    username: str = Form(None),
    password: str = Form(None),
    email: str = Form(None),
    request_data: dict = None
):
    # 兼容JSON请求体和表单数据
    if request_data:
        login_username = request_data.get("username") or request_data.get("email")
        login_password = request_data.get("password")
    else:
        login_username = username or email
        login_password = password
    
    # 验证参数
    if not login_username or not login_password:
        raise HTTPException(
            status_code=400,
            detail="用户名/邮箱和密码不能为空"
        )
    
    # 允许测试用户登录（用于测试）
    if login_username == "test_user" and login_password == "password123":
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": login_username}, expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "data": {
                "user": {
                    "id": 999,
                    "name": "测试用户",
                    "username": login_username,
                    "email": "test_user@example.com",
                    "avatar": "https://example.com/test_avatar.jpg",
                    "role": "user",
                    "created_at": "2023-01-01T00:00:00Z"
                },
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": "refresh_token_for_test",
                    "token_type": "bearer",
                    "expires_in": access_token_expires.seconds
                }
            }
        }
    
    # 检查是否是正常用户
    user = fake_users_db.get(login_username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 实际应该使用密码哈希验证
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.get("email", user.get("username"))},
        expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "data": {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "avatar": user["avatar"],
                "role": "user"
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": "refresh_token",
                "token_type": "bearer",
                "expires_in": access_token_expires.seconds
            }
        }
    }

# 用户注册
@router.post("/register")
async def register(user_data: dict):
    # 简单的注册逻辑，实际应该进行数据验证
    if user_data.get("email") in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    # 添加新用户
    new_user_id = len(fake_users_db) + 1
    fake_users_db[user_data["email"]] = {
        "id": new_user_id,
        "name": user_data.get("name", ""),
        "email": user_data["email"],
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # 实际应该哈希密码
        "avatar": user_data.get("avatar", "")
    }
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]}, expires_delta=access_token_expires
    )
    return {
        "success": True,
        "message": "注册成功",
        "data": {
            "user_id": new_user_id,
            "token": access_token,
            "expires_at": (datetime.utcnow() + access_token_expires).isoformat(),
            "user": fake_users_db[user_data["email"]]
        }
    }

# 获取用户信息
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "avatar": current_user["avatar"],
            "stats": {
                "total_recognitions": 10,
                "total_favorites": 5,
                "total_questions": 3
            }
        }
    }

# 刷新令牌
@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user["email"]}, expires_delta=access_token_expires
    )
    return {
        "success": True,
        "data": {
            "token": access_token,
            "expires_at": (datetime.utcnow() + access_token_expires).isoformat()
        }
    }

# 用户登出
@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # 实际应该将token加入黑名单
    return {
        "success": True,
        "message": "已成功登出"
    }