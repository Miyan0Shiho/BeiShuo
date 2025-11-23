# 碑说后端 API 接口文档

## 📋 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Token (Bearer Token)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 🔐 认证说明

### Token 使用方式
1. 通过 `/auth/login` 或 `/auth/register` 获取 Token
2. 在请求头中添加: `Authorization: Bearer {token}`
3. Token 有效期: 24小时（登录时可选择7天）
4. 使用 `/auth/refresh` 刷新 Token

## 📦 统一响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误信息",
  "error": {
    "code": "400",
    "message": "请求参数错误",
    "details": {}
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

## 🔑 认证相关接口

### 1. 用户注册
```
POST /auth/register
```

**请求体:**
```json
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "password": "password123",
  "phone": "13800138000",
  "avatar": "base64_encoded_image"  // 可选
}
```

**响应:**
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_at": "2024-02-01T12:00:00Z",
    "user": {
      "id": 1,
      "name": "张三",
      "email": "zhangsan@example.com"
    }
  }
}
```

### 2. 用户登录
```
POST /auth/login
```

**请求体:**
```json
{
  "email": "zhangsan@example.com",
  "password": "password123",
  "remember_me": true  // 可选，默认false
}
```

**响应:**
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_at": "2024-02-01T12:00:00Z",
    "user": {
      "id": 1,
      "name": "张三",
      "email": "zhangsan@example.com"
    }
  }
}
```

### 3. 获取用户信息
```
GET /auth/profile
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "avatar": "https://cdn.example.com/avatars/1.jpg",
    "stats": {
      "total_recognitions": 45,
      "total_favorites": 12,
      "total_questions": 23
    }
  }
}
```

### 4. 刷新Token
```
POST /auth/refresh
Authorization: Bearer {token}
```

### 5. 用户登出
```
POST /auth/logout
Authorization: Bearer {token}
```

## 📸 图片上传接口

### 上传图片
```
POST /upload/image
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**请求参数:**
- `image`: File (必需)
- `filename`: String (可选)

**响应:**
```json
{
  "success": true,
  "message": "图片上传成功",
  "data": {
    "image_id": "img_123456789",
    "image_url": "https://cdn.example.com/images/img_123456789.jpg",
    "image_size": {
      "width": 2048,
      "height": 1536
    },
    "file_size": 1024000,
    "upload_time": "2024-01-20T10:30:00Z"
  }
}
```

## 🔍 识别相关接口

### 1. 开始识别
```
POST /recognition/start
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "image_id": "img_123456789",
  "language": "classical",
  "options": {
    "enhance_image": true,
    "auto_detect_orientation": true
  }
}
```

**响应:**
```json
{
  "success": true,
  "message": "识别任务已开始",
  "data": {
    "task_id": "task_987654321",
    "status": "processing",
    "estimated_time": 30,
    "progress": 0
  }
}
```

### 2. 查询识别进度
```
GET /recognition/progress/{task_id}
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "task_id": "task_987654321",
    "status": "completed",
    "progress": 100,
    "result": {
      "recognition_id": "rec_123456789",
      "original_text": "维大唐开元二十有九年...",
      "modern_text": "维大唐开元二十九年...",
      "confidence": 98.7,
      "dynasty": "唐代",
      "period": "开元年间"
    }
  }
}
```

### 3. 获取识别历史
```
GET /recognition/history?page=1&per_page=20&dynasty=唐代&sort=date_desc
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "recognition_list": [
      {
        "id": 1,
        "title": "李白墓碑文",
        "image_url": "https://cdn.example.com/images/img1.jpg",
        "original_text": "维大唐开元二十有九年...",
        "confidence": 98.7,
        "dynasty": "唐代",
        "created_at": "2024-01-20T10:30:00Z",
        "is_favorited": false,
        "tags": ["李白", "唐代", "墓碑"]
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_count": 45,
      "per_page": 20
    }
  }
}
```

### 4. 更新识别结果（校对）
```
PUT /recognition/{recognition_id}/correct
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "corrected_text": "维大唐开元二十有九年...",
  "corrections": [
    {
      "original_position": 10,
      "original_char": "有",
      "corrected_char": "",
      "confidence": 0.9
    }
  ],
  "notes": "修正了一些古字"
}
```

## 🤖 AI功能接口

### 1. 获取AI阐释
```
POST /ai/interpretation
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "recognition_id": "rec_123456789",
  "aspects": ["history", "culture", "literature"],
  "depth": "detailed"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "interpretation_id": "int_123456789",
    "results": {
      "history": {
        "title": "历史背景",
        "content": "这块碑文记录的是唐代诗人李白的生平...",
        "key_points": ["李白生平", "开元盛世"]
      },
      "culture": {
        "title": "文化意义",
        "content": "碑文体现了唐代的文化特色...",
        "keywords": ["唐代文化", "诗人地位"]
      }
    },
    "related_inscriptions": []
  }
}
```

### 2. AI对话
```
POST /ai/chat
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "recognition_id": "rec_123456789",
  "message": "这个'维'字是什么意思？",
  "context": "唐代碑文阅读",
  "conversation_id": "conv_123456789"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_123456789",
    "reply": {
      "content": "'维'在古文中是一个发语词...",
      "type": "text",
      "sources": [],
      "suggestions": []
    },
    "related_questions": []
  }
}
```

### 3. 获取相关推荐
```
GET /ai/recommendations?type=inscriptions&limit=5
Authorization: Bearer {token}
```

## 📚 知识库接口

### 1. 获取知识库首页
```
GET /knowledge/home?category=书法艺术&period=唐代
```

**响应:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": "calligraphy",
        "name": "书法艺术",
        "count": 125,
        "articles": []
      }
    ],
    "featured": [],
    "recent_articles": []
  }
}
```

### 2. 获取文章详情
```
GET /knowledge/articles/{article_id}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": 101,
    "title": "唐代楷书的发展与特点",
    "content": "# 唐代楷书的发展与特点\n\n...",
    "excerpt": "唐代楷书在中国书法史上占据重要地位...",
    "cover_image": "https://cdn.example.com/articles/101.jpg",
    "author": {
      "name": "王教授",
      "avatar": "https://cdn.example.com/authors/wang.jpg"
    },
    "metadata": {
      "category": "书法艺术",
      "tags": ["唐代", "楷书", "书法"],
      "read_time": 8,
      "publish_date": "2024-01-15"
    },
    "stats": {
      "views": 3420,
      "likes": 156
    }
  }
}
```

### 3. 搜索知识库
```
GET /knowledge/search?q=唐代楷书&type=all&category=书法艺术&dynasty=唐代&page=1&per_page=20
```

**响应:**
```json
{
  "success": true,
  "data": {
    "query": "唐代楷书",
    "total_results": 45,
    "results": [
      {
        "type": "article",
        "id": 101,
        "title": "唐代楷书的发展与特点",
        "excerpt": "唐代楷书在中国书法史上占据重要地位...",
        "relevance": 0.95
      }
    ],
    "suggestions": ["唐代书法", "颜真卿"],
    "facets": {
      "categories": [{"name": "书法艺术", "count": 15}],
      "dynasties": [{"name": "唐代", "count": 25}]
    }
  }
}
```

## ❤️ 收藏管理接口

### 1. 获取收藏列表
```
GET /favorites?type=inscriptions&page=1&per_page=20
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "favorites": [
      {
        "id": 1,
        "type": "inscription",
        "item": {
          "id": "rec_123456789",
          "title": "李白墓碑文",
          "dynasty": "唐代"
        },
        "notes": "很有价值的碑文",
        "tags": ["李白", "唐代"],
        "created_at": "2024-01-20T10:30:00Z"
      }
    ],
    "stats": {
      "total_count": 12,
      "inscriptions_count": 8,
      "articles_count": 4
    },
    "pagination": {
      "current_page": 1,
      "total_pages": 1,
      "total_count": 12
    }
  }
}
```

### 2. 添加收藏
```
POST /favorites
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "type": "inscription",
  "item_id": "rec_123456789",
  "notes": "很有价值的碑文",
  "tags": ["李白", "唐代", "重要"]
}
```

### 3. 更新收藏
```
PUT /favorites/{favorite_id}
Authorization: Bearer {token}
```

**请求体:**
```json
{
  "notes": "更新收藏笔记",
  "tags": ["李白", "唐代", "重要", "诗仙"]
}
```

### 4. 删除收藏
```
DELETE /favorites/{favorite_id}
Authorization: Bearer {token}
```

## 📝 碑文管理接口（内部使用）

### 1. 获取碑文列表
```
GET /inscription/list?page=0&size=10&sort=created:desc&keyword=碑文
Authorization: Bearer {token}
```

### 2. 获取碑文详情
```
GET /inscription/{id}
Authorization: Bearer {token}
```

### 3. 更新碑文
```
PUT /inscription/{id}
Authorization: Bearer {token}
```

### 4. 删除碑文
```
DELETE /inscription/{id}
Authorization: Bearer {token}
```

### 5. 搜索碑文
```
GET /inscription/search?keyword=碑文&page=0&size=10
```

## ⚠️ 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 📋 注意事项

1. **分页参数**: 识别历史接口使用 `page`（从1开始）和 `per_page`，其他接口使用 `page`（从0开始）和 `size`
2. **文件上传**: 单文件最大10MB，支持 jpg, jpeg, png, webp
3. **Token刷新**: 建议在Token即将过期前30分钟刷新
4. **请求频率**: 建议控制请求频率，避免频繁调用

## 🔧 开发环境配置

- **端口**: 8000
- **上下文路径**: `/api/v1`
- **配置文件**: `src/main/resources/application.yml`
- **日志文件**: `logs/beishuo-backend.log`

---


