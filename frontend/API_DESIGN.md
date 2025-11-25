# 碑说 API 接口设计文档

## 📋 API 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Token
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 🔐 用户认证相关接口

### 1. 用户注册
```
POST /auth/register
Content-Type: application/json

Request Body:
{
  "name": "张三",
  "email": "zhangsan@example.com", 
  "password": "password123",
  "phone": "13800138000",
  "avatar": "base64_encoded_image" // 可选
}

Response 200:
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
      "email": "zhangsan@example.com",
      "avatar": "https://cdn.example.com/avatars/1.jpg",
      "created_at": "2024-01-20T10:30:00Z"
    }
  }
}
```

### 2. 用户登录
```
POST /auth/login
Content-Type: application/json

Request Body:
{
  "email": "zhangsan@example.com",
  "password": "password123",
  "remember_me": true // 可选，默认false
}

Response 200:
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_at": "2024-02-01T12:00:00Z",
    "user": {
      "id": 1,
      "name": "张三",
      "email": "zhangsan@example.com",
      "avatar": "https://cdn.example.com/avatars/1.jpg"
    }
  }
}
```

### 3. 刷新Token
```
POST /auth/refresh
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_at": "2024-02-01T12:00:00Z"
  }
}
```

### 4. 用户登出
```
POST /auth/logout
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "message": "已成功登出"
}
```

### 5. 获取用户信息
```
GET /auth/profile
Authorization: Bearer {token}

Response 200:
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

---

## 📸 图片上传与碑文识别接口

### 1. 上传图片
```
POST /upload/image
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- image: File (必需)
- filename: String (可选)

Response 200:
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

### 2. 开始碑文识别
```
POST /recognition/start
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "image_id": "img_123456789",
  "language": "classical", // classical, modern
  "options": {
    "enhance_image": true,
    "auto_detect_orientation": true
  }
}

Response 200:
{
  "success": true,
  "message": "识别任务已开始",
  "data": {
    "task_id": "task_987654321",
    "status": "processing",
    "estimated_time": 30, // 秒
    "progress": 0
  }
}
```

### 3. 查询识别进度
```
GET /recognition/progress/{task_id}
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "task_id": "task_987654321",
    "status": "completed", // processing, completed, failed
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

### 4. 获取识别历史记录
```
GET /recognition/history
Authorization: Bearer {token}
Query Parameters:
- page: 1 (页码)
- per_page: 20 (每页数量)
- dynasty: "唐代" (筛选朝代)
- sort: "date_desc" (排序方式)

Response 200:
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

---

## ✏️ 校对与编辑接口

### 1. 更新识别结果
```
PUT /recognition/{recognition_id}/correct
Authorization: Bearer {token}

Request Body:
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

Response 200:
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

### 2. 获取校对建议
```
GET /recognition/{recognition_id}/suggestions
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "position": 15,
        "original_char": "丑",
        "suggestions": ["丑", "醜", "丑"],
        "confidence": 0.95
      }
    ]
  }
}
```

### 3. 保存校对记录
```
POST /recognition/{recognition_id}/history
Authorization: Bearer {token}

Request Body:
{
  "action": "correction",
  "changes": [
    {
      "position": 10,
      "before": "有",
      "after": "",
      "reason": "去除虚字"
    }
  ],
  "notes": "去除不必要虚字"
}

Response 200:
{
  "success": true,
  "message": "校对记录已保存"
}
```

---

## 🤖 AI功能接口

### 1. 获取AI阐释
```
POST /ai/interpretation
Authorization: Bearer {token}

Request Body:
{
  "recognition_id": "rec_123456789",
  "aspects": ["history", "culture", "literature"], // 要分析的方面
  "depth": "detailed" // brief, detailed, academic
}

Response 200:
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
    "related_inscriptions": [
      {
        "id": 2,
        "title": "杜甫墓志铭",
        "similarity": 0.85
      }
    ]
  }
}
```

### 2. AI对话接口
```
POST /ai/chat
Authorization: Bearer {token}

Request Body:
{
  "recognition_id": "rec_123456789",
  "message": "这个'维'字是什么意思？",
  "context": "唐代碑文阅读",
  "conversation_id": "conv_123456789" // 可选，用于连续对话
}

Response 200:
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
    "related_questions": [
      {
        "question": "唐代碑文有什么特点？",
        "confidence": 0.9
      }
    ]
  }
}
```

### 3. 获取相关推荐
```
GET /ai/recommendations
Authorization: Bearer {token}
Query Parameters:
- type: "inscriptions|articles|questions"
- limit: 5

Response 200:
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
    "articles": [
      {
        "id": 101,
        "title": "唐代墓碑文的特点",
        "excerpt": "唐代墓碑文具有独特的文体特征...",
        "read_time": 5
      }
    ],
    "questions": [
      {
        "id": 201,
        "question": "唐代书法有哪些特点？",
        "difficulty": "beginner"
      }
    ]
  }
}
```

---

## 📚 知识库接口

### 1. 获取知识库首页
```
GET /knowledge/home
Query Parameters:
- category: String (可选)
- period: String (可选)

Response 200:
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": "calligraphy",
        "name": "书法艺术",
        "icon": "fas fa-pen-fancy",
        "count": 125,
        "articles": [
          {
            "id": 101,
            "title": "唐代楷书的发展与特点",
            "excerpt": "唐代楷书在中国书法史上占据重要地位...",
            "cover_image": "https://cdn.example.com/articles/101.jpg",
            "read_time": 8,
            "tags": ["唐代", "楷书", "书法"],
            "publish_date": "2024-01-15"
          }
        ]
      }
    ],
    "featured": [
      {
        "id": 201,
        "title": "中国古代碑刻艺术概览",
        "type": "article",
        "cover": "https://cdn.example.com/articles/201.jpg",
        "stats": {
          "views": 15420,
          "likes": 342
        }
      }
    ],
    "recent_articles": [
      {
        "id": 202,
        "title": "最新考古发现：汉代石碑研究新进展",
        "publish_date": "2024-01-20"
      }
    ]
  }
}
```

### 2. 获取文章详情
```
GET /knowledge/articles/{article_id}

Response 200:
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
    "related_articles": [
      {
        "id": 102,
        "title": "宋代书法的发展",
        "relevance": 0.85
      }
    ]
  }
}
```

### 3. 搜索知识库
```
GET /knowledge/search
Query Parameters:
- q: "唐代楷书" (搜索关键词)
- type: "all" // all, articles, inscriptions
- category: String (分类)
- dynasty: String (朝代)
- page: 1
- per_page: 20

Response 200:
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
    "suggestions": [
      "唐代书法",
      "颜真卿",
      "欧阳询"
    ],
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

---

## ❤️ 收藏管理接口

### 1. 获取收藏列表
```
GET /favorites
Authorization: Bearer {token}
Query Parameters:
- type: "inscriptions|articles" // 可选，筛选类型
- page: 1
- per_page: 20

Response 200:
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

Request Body:
{
  "type": "inscription",
  "item_id": "rec_123456789",
  "notes": "很有价值的碑文",
  "tags": ["李白", "唐代", "重要"]
}

Response 200:
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

Request Body:
{
  "notes": "更新收藏笔记",
  "tags": ["李白", "唐代", "重要", "诗仙"]
}

Response 200:
{
  "success": true,
  "message": "收藏已更新"
}
```

### 4. 删除收藏
```
DELETE /favorites/{favorite_id}
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "message": "已从收藏中移除"
}
```

---

## 📊 统计数据接口

### 1. 获取用户统计
```
GET /stats/user
Authorization: Bearer {token}

Response 200:
{
  "success": true,
  "data": {
    "recognition_stats": {
      "total_count": 45,
      "this_month": 12,
      "by_dynasty": {
        "唐代": 15,
        "汉代": 10,
        "宋代": 8
      },
      "average_confidence": 96.5
    },
    "activity_stats": {
      "favorites_count": 12,
      "questions_asked": 23,
      "articles_read": 34,
      "last_active": "2024-01-20T10:30:00Z"
    },
    "growth_trend": [
      {"date": "2024-01-01", "count": 2},
      {"date": "2024-01-15", "count": 5}
    ]
  }
}
```

### 2. 获取平台统计
```
GET /stats/platform

Response 200:
{
  "success": true,
  "data": {
    "users": {
      "total": 15240,
      "active_today": 1250,
      "new_this_month": 480
    },
    "recognitions": {
      "total": 89456,
      "this_month": 3240,
      "average_accuracy": 97.2
    },
    "popular_content": {
      "dynasties": [
        {"name": "唐代", "count": 12500},
        {"name": "汉代", "count": 8900}
      ],
      "categories": [
        {"name": "书法碑刻", "count": 15420},
        {"name": "名人碑刻", "count": 12350}
      ]
    }
  }
}
```

---

## 🛠️ 工具类接口

### 1. 文本转换
```
POST /tools/text-convert
Authorization: Bearer {token}

Request Body:
{
  "text": "维大唐开元二十有九年",
  "convert_type": "ancient_to_modern", // ancient_to_modern, modern_to_ancient
  "options": {
    "simplify_characters": true,
    "add_punctuation": true
  }
}

Response 200:
{
  "success": true,
  "data": {
    "original_text": "维大唐开元二十有九年",
    "converted_text": "维大唐开元二十九年",
    "changes": [
      {
        "position": 10,
        "original": "有",
        "converted": "",
        "reason": "虚字去除"
      }
    ]
  }
}
```

### 2. 字体识别
```
POST /tools/font-identify
Authorization: Bearer {token}

Request Body:
{
  "image_id": "img_123456789",
  "sample_area": {
    "x": 100,
    "y": 100,
    "width": 200,
    "height": 100
  }
}

Response 200:
{
  "success": true,
  "data": {
    "font_type": "楷书",
    "dynasty": "唐代",
    "confidence": 0.94,
    "characteristics": {
      "stroke_style": "浑厚",
      "structure": "端正",
      "aesthetic": "庄重"
    },
    "similar_fonts": [
      {
        "name": "颜真卿体",
        "similarity": 0.89,
        "dynasty": "唐代"
      }
    ]
  }
}
```

---

## ⚠️ 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 429 | 请求频率限制 |
| 500 | 服务器内部错误 |
| 503 | 服务暂不可用 |

## 📝 通用响应格式

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
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "details": {
      "email": ["邮箱格式不正确"]
    }
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## 🔒 认证说明

1. **Token获取**: 通过 `/auth/login` 或 `/auth/register` 接口获取JWT Token
2. **Token使用**: 在请求头中添加 `Authorization: Bearer {token}`
3. **Token刷新**: Token即将过期时使用 `/auth/refresh` 接口刷新
4. **Token失效**: 主动调用 `/auth/logout` 注销

## 📋 请求限制

- **频率限制**: 每分钟最多100次请求
- **文件上传**: 单文件最大10MB
- **批量操作**: 最多50条记录

---

*最后更新时间: 2024-01-20*
*版本: v1.0*