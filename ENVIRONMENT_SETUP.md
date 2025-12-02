# 环境变量配置说明

## 概述

碑说项目需要配置以下环境变量才能正常运行。这些配置包含在 `python/.env` 文件中。

## 必需配置

### 1. LLM服务配置
```env
# DashScope API密钥 (阿里云通义千问)
LLM_API_KEY=sk-your-dashscope-api-key-here
```

**获取方式：**
1. 访问 [阿里云DashScope控制台](https://dashscope.aliyun.com/)
2. 注册/登录阿里云账号
3. 创建API密钥
4. 将密钥填入 `LLM_API_KEY` 字段

### 2. OCR服务配置
```env
# 看店古籍OCR服务配置
KANDIANGUJI_OCR_TOKEN=your-ocr-token-here
KANDIANGUJI_OCR_EMAIL=your-email@example.com
```

**获取方式：**
1. 联系看店古籍OCR服务提供商获取token和邮箱
2. 或使用其他OCR服务替换相关代码

## 可选配置

### 应用配置
```env
# 应用名称和版本
APP_NAME=碑说后端服务
APP_VERSION=1.0.0

# 文件上传配置
FILE_UPLOAD_MAX_SIZE=10485760
FILE_UPLOAD_ALLOWED_TYPES=["jpg", "jpeg", "png", "webp"]
```

### 数据库配置
```env
# PostgreSQL数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=beishuo
DB_USER=postgres
DB_PASS=password
```

### Redis配置
```env
# Redis缓存配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### JWT配置
```env
# JWT令牌配置
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### CORS配置
```env
# 跨域配置
CORS_ALLOWED_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]
CORS_ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOWED_HEADERS=["*"]
```

## 快速开始

### 1. 复制示例文件
```bash
cp python/env.example python/.env
```

### 2. 编辑配置文件
```bash
# 使用文本编辑器编辑 .env 文件
vim python/.env
# 或
nano python/.env
```

### 3. 配置必需参数
确保以下参数已正确配置：
- `LLM_API_KEY`
- `KANDIANGUJI_OCR_TOKEN`
- `KANDIANGUJI_OCR_EMAIL`

### 4. 启动服务
```bash
# 使用一键脚本
./run.sh
# 或 Windows
run.bat
```

## 注意事项

1. **安全警告**：不要将 `.env` 文件提交到版本控制系统
2. **格式要求**：数组类型的配置项必须使用JSON格式（如 `["item1", "item2"]`）
3. **开发环境**：开发时可以使用默认配置，但生产环境必须修改所有默认值
4. **API限制**：注意各API服务的调用频率限制和配额

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查 `.env` 文件格式是否正确
   - 确认所有必需参数已配置
   - 查看Docker日志：`docker-compose logs`

2. **OCR服务不可用**
   - 检查OCR token和邮箱是否正确
   - 确认OCR服务提供商的服务状态

3. **LLM服务错误**
   - 验证API密钥是否正确
   - 检查API调用配额是否用完
   - 确认网络连接正常

## 支持

如有问题，请查看项目README文档或联系开发团队。