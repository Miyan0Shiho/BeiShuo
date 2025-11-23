# 碑说 Python 后端 API 接口文档

## 📋 基础信息

- **Base URL**: `http://localhost:8080/api/v1`
- **框架**: FastAPI
- **认证方式**: JWT Token (Bearer Token)
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API文档**: `http://localhost:8080/docs` (Swagger UI)

## 🔐 认证说明

### Token 使用方式
1. 通过 `/auth/login` 或 `/auth/register` 获取 Token
2. 在请求头中添加: `Authorization: Bearer {token}`
3. Token 有效期: 24小时（登录时可选择7天）
4. 使用 `/auth/refresh` 刷新 Token

### 依赖注入
所有需要认证的接口都使用 `Depends(get_current_user_id)` 自动获取当前用户ID，无需手动解析Token。

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
    },
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

### 4. 刷新Token
```
POST /auth/refresh
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_at": "2024-02-01T12:00:00Z"
  }
}
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
- `image`: File (必需) - 图片文件
- `filename`: String (可选) - 自定义文件名

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

**文件限制:**
- 支持格式: jpg, jpeg, png, webp
- 最大大小: 10MB

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
      "word_count": 286,
      "dynasty": "唐代",
      "period": "开元年间",
      "location": "当涂",
      "person": "李白",
      "estimated_year": "公元741年",
      "processing_time": 25
    }
  }
}
```

### 3. 获取识别历史
```
GET /recognition/history?page=1&per_page=20&dynasty=唐代&sort=date_desc
Authorization: Bearer {token}
```

**查询参数:**
- `page`: 页码，从1开始（默认: 1）
- `per_page`: 每页数量（默认: 20，最大: 100）
- `dynasty`: 朝代筛选（可选）
- `sort`: 排序方式（可选，默认: date_desc）

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

**响应:**
```json
{
  "success": true,
  "message": "校对结果已保存",
  "data": {
    "recognition_id": "rec_123456789",
    "version": 2,
    "correction_count": 3
  }
}
```

### 5. 获取校对建议
```
GET /recognition/{recognition_id}/suggestions
Authorization: Bearer {token}
```

### 6. 保存校对记录
```
POST /recognition/{recognition_id}/history
Authorization: Bearer {token}
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
  "aspects": ["history", "culture", "literature"],  // 可选
  "depth": "detailed"  // brief, detailed, academic
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
        "key_points": ["李白生平", "开元盛世", "当涂地区"]
      },
      "culture": {
        "title": "文化意义",
        "content": "碑文体现了唐代的文化特色...",
        "keywords": ["唐代文化", "诗人地位", "文学传统"]
      },
      "literature": {
        "title": "文学价值",
        "content": "从文学角度看，这块碑文具有重要价值...",
        "style": "骈文体",
        "themes": ["人生感悟", "文学成就"]
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
  "conversation_id": "conv_123456789"  // 可选，用于连续对话
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv_123456789",
    "reply": {
      "content": "'维'在古文中是一个发语词，常用于碑文的开头...",
      "type": "text",
      "sources": [
        {
          "title": "古代汉语虚词研究",
          "url": "https://example.com/article/1"
        }
      ],
      "suggestions": [
        "唐代常用发语词有哪些？",
        "这块碑文的其他虚词解释"
      ]
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

**查询参数:**
- `type`: 推荐类型（可选）- inscriptions|articles|questions
- `limit`: 推荐数量（默认: 5，最大: 20）

**响应:**
```json
{
  "success": true,
  "data": {
    "inscriptions": [
      {
        "id": 2,
        "title": "杜甫墓志铭",
        "dynasty": "唐代",
        "similarity": 0.89,
        "reason": "同朝代诗人，内容相关"
      }
    ],
    "articles": [],
    "questions": []
  }
}
```

## 📚 知识库接口

### 1. 获取知识库首页
```
GET /knowledge/home?category=书法艺术&period=唐代
```

**查询参数:**
- `category`: 分类筛选（可选）
- `period`: 时期筛选（可选）

**响应:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": "calligraphy",
        "name": "书法艺术",
        "icon": "fas fa-pen-fancy",
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
    "content": "# 唐代楷书的发展与特点\n\n唐代是中国书法史上的黄金时期...",
    "excerpt": "唐代楷书在中国书法史上占据重要地位...",
    "cover_image": "https://cdn.example.com/articles/101.jpg",
    "author": {
      "name": "王教授",
      "avatar": "https://cdn.example.com/authors/wang.jpg",
      "title": "书法研究所研究员"
    },
    "metadata": {
      "category": "书法艺术",
      "tags": ["唐代", "楷书", "书法"],
      "read_time": 8,
      "word_count": 2500,
      "publish_date": "2024-01-15",
      "last_updated": "2024-01-20"
    },
    "stats": {
      "views": 3420,
      "likes": 156,
      "comments": 23,
      "bookmarks": 89
    },
    "related_articles": []
  }
}
```

### 3. 搜索知识库
```
GET /knowledge/search?q=唐代楷书&type=all&category=书法艺术&dynasty=唐代&page=1&per_page=20
```

**查询参数:**
- `q`: 搜索关键词（必需）
- `type`: 搜索类型（可选，默认: all）- all|articles|inscriptions
- `category`: 分类筛选（可选）
- `dynasty`: 朝代筛选（可选）
- `page`: 页码，从1开始（默认: 1）
- `per_page`: 每页数量（默认: 20）

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
        "relevance": 0.95,
        "publish_date": "2024-01-15"
      },
      {
        "type": "inscription",
        "id": 301,
        "title": "多宝塔碑",
        "dynasty": "唐代",
        "description": "颜真卿楷书代表作",
        "relevance": 0.88
      }
    ],
    "suggestions": ["唐代书法", "颜真卿", "欧阳询"],
    "facets": {
      "categories": [
        {"name": "书法艺术", "count": 15},
        {"name": "历史人物", "count": 8}
      ],
      "dynasties": [
        {"name": "唐代", "count": 25},
        {"name": "宋代", "count": 12}
      ]
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

**查询参数:**
- `type`: 收藏类型（可选）- inscriptions|articles
- `page`: 页码，从1开始（默认: 1）
- `per_page`: 每页数量（默认: 20，最大: 100）

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
          "dynasty": "唐代",
          "image_url": "https://cdn.example.com/images/img1.jpg",
          "excerpt": "维大唐开元二十有九年...",
          "confidence": 98.7
        },
        "notes": "很有价值的碑文",
        "tags": ["李白", "唐代", "重要"],
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

**响应:**
```json
{
  "success": true,
  "message": "已添加到收藏",
  "data": {
    "favorite_id": 1
  }
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

### 3. 创建碑文
```
POST /inscription
Authorization: Bearer {token}
```

### 4. 更新碑文
```
PUT /inscription/{id}
Authorization: Bearer {token}
```

### 5. 删除碑文
```
DELETE /inscription/{id}
Authorization: Bearer {token}
```

### 6. 搜索碑文
```
GET /inscription/search?keyword=碑文
```

## ⚠️ 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 🔧 技术特性

### FastAPI 特性
- **自动API文档**: 访问 `/docs` 查看 Swagger UI，`/redoc` 查看 ReDoc
- **类型验证**: 使用 Pydantic 进行请求/响应数据验证
- **依赖注入**: 使用 `Depends()` 实现认证和依赖管理
- **异步支持**: 所有接口都支持异步处理

### 代码结构
```
python/app/
├── api/v1/          # API路由
│   ├── auth.py      # 认证接口
│   ├── upload.py    # 上传接口
│   ├── recognition.py  # 识别接口
│   ├── ai.py        # AI功能接口
│   ├── knowledge.py # 知识库接口
│   └── favorites.py # 收藏接口
├── common/          # 公共模块
│   ├── response.py  # 响应格式
│   └── result_code.py  # 错误码
├── core/            # 核心模块
│   ├── security.py  # JWT工具
│   └── dependencies.py  # 依赖注入
├── services/        # 业务逻辑层
└── schemas/         # 数据模型
```

## 📋 注意事项

1. **分页参数**: 识别历史和收藏接口使用 `page`（从1开始）和 `per_page`，其他接口使用 `page`（从0开始）和 `size`
2. **文件上传**: 单文件最大10MB，支持 jpg, jpeg, png, webp
3. **Token刷新**: 建议在Token即将过期前30分钟刷新
4. **异步处理**: 所有接口都是异步的，使用 `async/await`
5. **服务层**: 每个服务使用后需要调用 `await service.close()` 关闭连接

## 🚀 启动方式

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## 📖 API文档访问

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

---


