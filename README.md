# 碑说项目 - 完整部署指南

## 项目概述

碑说项目是一个基于Java Spring Boot后端和Vue.js前端的Web应用，用于管理和展示古代碑文及相关知识。项目采用微服务架构，支持Docker容器化部署。

## 快速开始

### 系统要求

- **操作系统**: macOS / Linux / Windows (WSL2)
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **内存**: 至少4GB可用内存
- **磁盘空间**: 至少2GB可用磁盘空间

### 一键部署（推荐）

```bash
# 1. 克隆项目
git clone <项目GitHub地址>
cd 团队项目

# 2. 给脚本添加执行权限
chmod +x start-dev.sh stop-dev.sh test-deploy.sh

# 3. 运行环境检查
./test-deploy.sh

# 4. 启动开发环境
./start-dev.sh
```

### 访问应用

部署完成后，可以访问以下服务：

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8080
- **数据库管理**: localhost:5432 (用户名: beishuo, 密码: beishuo123)
- **Redis管理**: localhost:6379
- **对象存储管理**: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)

## 部署方式

### 方式一：开发环境部署（推荐）

使用Docker Compose进行完整的开发环境部署：

```bash
# 使用开发环境配置
./start-dev.sh

# 停止服务
./stop-dev.sh
```

**特点**:
- 包含所有依赖服务（PostgreSQL、Redis、MinIO）
- 支持热重载开发
- 自动数据库初始化
- 适合开发和测试

### 方式二：生产环境部署

使用Docker构建生产镜像：

```bash
# 构建后端镜像
docker build -t beishuo-backend:latest .

# 构建前端镜像
cd frontend
docker build -f Dockerfile.dev -t beishuo-frontend:latest .

# 运行生产环境
docker-compose -f docker-compose.prod.yml up -d
```

**特点**:
- 优化过的生产镜像
- 最小化依赖
- 适合生产部署

### 方式三：手动部署

如果不想使用Docker，可以手动部署：

```bash
# 后端部署
cd src
mvn clean package
java -jar target/beishuo-*.jar

# 前端部署
cd frontend
npm install
npm run build
npm run preview
```

## 项目结构

```
团队项目/
├── src/                    # Java后端源代码
│   ├── main/java/          # Spring Boot应用代码
│   ├── resources/          # 配置文件
│   └── test/               # 单元测试
├── frontend/               # Vue.js前端源代码
│   ├── src/                # Vue组件和逻辑
│   ├── public/             # 静态资源
│   └── package.json        # 前端依赖
├── docker/                 # Docker相关文件
│   ├── docker-compose.dev.yml    # 开发环境配置
│   └── docker-compose.prod.yml   # 生产环境配置
├── init-scripts/           # 数据库初始化脚本
├── Dockerfile              # 后端生产镜像配置
├── start-dev.sh            # 一键启动脚本
├── stop-dev.sh             # 停止脚本
├── test-deploy.sh          # 环境检查脚本
├── README.md               # 本文档
└── README-DEV.md           # 详细开发指南
```

## 服务说明

### 核心服务

| 服务 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 后端服务 | Java Spring Boot | 8080 | 提供RESTful API接口 |
| 前端服务 | Vue.js + Vite | 5173 | 用户界面，支持热重载 |
| 数据库 | PostgreSQL 15 | 5432 | 数据持久化存储 |
| 缓存 | Redis 7 | 6379 | 会话和缓存管理 |
| 对象存储 | MinIO | 9000/9001 | 文件存储和管理 |

### 依赖服务

- **PostgreSQL**: 关系型数据库，存储应用数据
- **Redis**: 缓存和会话存储，提升性能
- **MinIO**: 对象存储服务，用于文件上传

## 配置说明

### 环境变量

项目使用环境变量进行配置管理，主要配置文件：

- `.env.dev` - 开发环境配置
- `.env.prod` - 生产环境配置

关键配置项：

```bash
# 数据库配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=beishuo
DB_USER=beishuo
DB_PASS=beishuo123

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO配置
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# 应用配置
SERVER_PORT=8080
VITE_DEV_SERVER_PORT=5173
```

### 自定义配置

如需自定义配置，可以：

1. **修改环境文件**
   ```bash
   cp .env.sample .env.local
   # 编辑 .env.local 文件
   ```

2. **使用自定义配置启动**
   ```bash
   docker-compose --env-file .env.local up -d
   ```

## 部署验证

### 环境检查

部署前建议运行环境检查脚本：

```bash
./test-deploy.sh
```

检查项目包括：
- Docker环境检查
- 项目结构验证
- 配置文件检查
- Dockerfile语法验证
- 脚本权限检查
- Docker Compose配置检查

### 健康检查

部署完成后，验证各服务状态：

```bash
# 检查后端服务
curl http://localhost:8080/actuator/health

# 检查前端服务
curl http://localhost:5173

# 检查数据库连接
docker exec -it beishuo-postgres psql -U beishuo -d beishuo -c "SELECT 1;"

# 检查Redis连接
docker exec -it beishuo-redis redis-cli ping
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :8080
   lsof -i :5173
   lsof -i :5432
   
   # 修改端口配置
   # 编辑 .env.dev 文件，修改端口号
   ```

2. **服务启动失败**
   ```bash
   # 查看服务日志
   docker-compose -f docker-compose.dev.yml logs
   
   # 重新启动
   ./stop-dev.sh
   ./start-dev.sh
   ```

3. **数据库连接问题**
   ```bash
   # 检查数据库服务
   docker exec -it beishuo-postgres psql -U beishuo -d beishuo
   
   # 重新初始化
   docker-compose -f docker-compose.dev.yml down -v
   ./start-dev.sh
   ```

4. **前端热重载不工作**
   ```bash
   # 检查文件挂载
   docker exec -it beishuo-frontend ls -la /app/src
   
   # 重启前端服务
   docker-compose -f docker-compose.dev.yml restart frontend
   ```

### 日志查看

```bash
# 查看所有服务日志
docker-compose -f docker-compose.dev.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# 查看容器日志
docker logs -f beishuo-backend
docker logs -f beishuo-frontend
```

## 维护和更新

### 日常维护

```bash
# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 重启服务
docker-compose -f docker-compose.dev.yml restart backend

# 更新依赖
# 后端：修改 pom.xml 后重新构建
# 前端：修改 package.json 后重新安装依赖
```

### 数据备份

```bash
# 备份数据库
docker exec beishuo-postgres pg_dump -U beishuo beishuo > backup.sql

# 备份Redis数据
docker exec beishuo-redis redis-cli --rdb - > redis_backup.rdb
```

### 清理资源

```bash
# 停止并清理所有容器
./stop-dev.sh
docker system prune -f

# 清理镜像
docker image prune -a

# 清理卷
docker volume prune
```

## 开发指南

详细的开发环境配置和开发流程请参考：[README-DEV.md](./README-DEV.md)

## 技术支持

- **项目文档**: 查看 [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **问题反馈**: 创建Issue
- **开发团队**: 联系项目维护者

## 许可证

本项目采用 [MIT License](LICENSE)。

---

**祝您部署顺利！** 🚀

如果遇到任何问题，请参考故障排除部分或联系开发团队。