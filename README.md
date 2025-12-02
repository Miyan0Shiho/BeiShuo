# 碑说 - 智能古籍识别与对话系统

## 项目简介

碑说是一个基于AI技术的智能古籍识别与对话系统，能够识别古籍碑文图像，并提供智能对话功能。项目采用现代化的前后端分离架构，支持容器化部署。

## 功能特性

- 🖼️ **图像识别**：支持古籍碑文图像OCR识别
- 💬 **智能对话**：基于大语言模型的智能问答系统
- 🔍 **RAG检索**：基于向量检索的增强生成
- 📱 **响应式界面**：现代化的Vue.js前端界面
- 🐳 **容器化部署**：支持Docker一键部署
- 🔄 **实时通信**：支持流式聊天响应

## 技术栈

### 后端
- **框架**：FastAPI + Python 3.11
- **AI服务**：阿里云DashScope (通义千问)
- **OCR服务**：看店古籍OCR
- **缓存**：Redis
- **部署**：Docker + Uvicorn

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **样式**：Tailwind CSS
- **状态管理**：Pinia
- **路由**：Vue Router

## 快速开始

### 前提条件

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 一键启动

#### Linux/Mac
```bash
# 克隆项目
git clone <repository-url>
cd 团队项目

# 一键启动
./run.sh
```

#### Windows
```cmd
# 克隆项目
git clone <repository-url>
cd 团队项目

# 一键启动
run.bat
```

### 手动启动

1. **配置环境变量**
   ```bash
   cp python/env.example python/.env
   # 编辑 python/.env 文件，配置API密钥
   ```

2. **启动服务**
   ```bash
   # 构建并启动
   docker-compose up -d
   
   # 查看服务状态
   docker-compose ps
   
   # 查看日志
   docker-compose logs -f
   ```

3. **访问应用**
   - 前端界面：http://localhost:5173
   - 后端API文档：http://localhost:8080/docs

## 项目结构

```
团队项目/
├── python/                 # Python后端
│   ├── app/               # 应用代码
│   ├── requirements.txt   # Python依赖
│   ├── Dockerfile         # 后端Docker配置
│   └── .env              # 环境变量配置
├── frontend/              # Vue.js前端
│   ├── src/              # 源代码
│   ├── package.json      # 前端依赖
│   └── Dockerfile        # 前端Docker配置
├── docker-compose.yml     # 服务编排配置
├── run.sh                # Linux/Mac启动脚本
├── run.bat               # Windows启动脚本
├── README.md             # 项目文档
└── ENVIRONMENT_SETUP.md  # 环境配置说明
```

## API文档

启动服务后，可访问以下API端点：

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### 主要API接口

- `POST /api/chat` - 智能对话
- `POST /api/upload` - 文件上传
- `POST /api/ocr` - OCR识别
- `GET /api/health` - 健康检查

## 开发指南

### 后端开发

```bash
# 进入后端目录
cd python

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 部署说明

### 生产环境部署

1. **配置生产环境变量**
   ```bash
   # 复制生产环境配置
   cp python/env.production.example python/.env
   
   # 编辑配置文件
   vim python/.env
   ```

2. **构建生产镜像**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

3. **启动生产服务**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### 环境变量配置

详细的环境变量配置说明请参考 [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md)。

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页：https://github.com/your-org/beishuo
- 问题反馈：https://github.com/your-org/beishuo/issues
- 邮箱：dev@beishuo.com

## 致谢

感谢以下开源项目和技术服务：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [阿里云DashScope](https://dashscope.aliyun.com/) - 大语言模型服务
- [看店古籍OCR](https://www.kandian.com/) - 古籍识别服务