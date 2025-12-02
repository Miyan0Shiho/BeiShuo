# 碑说项目 - 开发环境部署指南

## 项目概述

碑说项目是一个基于Java Spring Boot后端和Vue.js前端的Web应用，用于管理和展示古代碑文及相关知识。

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存
- 至少2GB可用磁盘空间

## 快速开始

### 1. 克隆项目

```bash
git clone <项目GitHub地址>
cd 团队项目
```

### 2. 一键部署

```bash
# 给脚本添加执行权限
chmod +x start-dev.sh stop-dev.sh

# 启动开发环境
./start-dev.sh
```

脚本会自动：
- 检查Docker环境
- 构建后端镜像
- 安装前端依赖
- 启动所有服务
- 等待服务健康检查通过

### 3. 访问应用

部署完成后，可以访问以下服务：

- **前端开发服务器**: http://localhost:5173
- **后端API服务**: http://localhost:8080
- **数据库管理**: localhost:5432 (用户名: beishuo, 密码: beishuo123)
- **Redis管理**: localhost:6379
- **对象存储管理**: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)

## 项目结构

```
团队项目/
├── src/                    # Java后端源代码
├── frontend/               # Vue.js前端源代码
├── docker-compose.dev.yml  # 开发环境Docker配置
├── Dockerfile              # 后端生产环境镜像
├── start-dev.sh            # 一键启动脚本
├── stop-dev.sh             # 停止脚本
├── .env.dev                # 开发环境配置
└── init-scripts/           # 数据库初始化脚本
```

## 服务说明

### 后端服务 (backend)
- **技术栈**: Java Spring Boot
- **端口**: 8080
- **健康检查**: http://localhost:8080/actuator/health
- **依赖服务**: PostgreSQL, Redis, MinIO

### 前端服务 (frontend)
- **技术栈**: Vue.js + Vite
- **端口**: 5173
- **热重载**: 支持代码修改实时刷新

### 数据库服务 (postgres)
- **数据库**: PostgreSQL 15
- **端口**: 5432
- **数据库名**: beishuo
- **用户名/密码**: beishuo/beishuo123

### 缓存服务 (redis)
- **缓存**: Redis 7
- **端口**: 6379

### 对象存储服务 (minio)
- **存储**: MinIO (S3兼容)
- **API端口**: 9000
- **管理界面**: 9001
- **用户名/密码**: minioadmin/minioadmin

## 开发命令

### 常用Docker命令

```bash
# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 查看服务日志
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# 重启特定服务
docker-compose -f docker-compose.dev.yml restart backend

# 重新构建服务
docker-compose -f docker-compose.dev.yml build backend
```

### 后端开发

```bash
# 进入后端容器
docker exec -it beishuo-backend bash

# 查看后端日志
docker logs -f beishuo-backend

# 重新编译后端
cd /app
mvn clean compile
```

### 前端开发

```bash
# 进入前端容器
docker exec -it beishuo-frontend sh

# 查看前端日志
docker logs -f beishuo-frontend

# 安装新依赖 (在宿主机执行)
cd frontend
npm install <package-name>
```

## 故障排除

### 服务启动失败

1. **检查Docker服务状态**
   ```bash
   docker ps -a
   docker-compose -f docker-compose.dev.yml logs
   ```

2. **检查端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :8080
   lsof -i :5173
   lsof -i :5432
   ```

3. **清理并重新启动**
   ```bash
   ./stop-dev.sh
   docker system prune -f
   ./start-dev.sh
   ```

### 数据库连接问题

1. **检查数据库服务状态**
   ```bash
   docker exec -it beishuo-postgres psql -U beishuo -d beishuo
   ```

2. **重新初始化数据库**
   ```bash
   docker-compose -f docker-compose.dev.yml down -v
   ./start-dev.sh
   ```

### 前端热重载不工作

1. **检查文件挂载**
   ```bash
   docker exec -it beishuo-frontend ls -la /app/src
   ```

2. **重启前端服务**
   ```bash
   docker-compose -f docker-compose.dev.yml restart frontend
   ```

## 开发流程

### 1. 代码修改
- 前端代码修改会自动热重载
- 后端代码修改需要重启服务：`docker-compose restart backend`

### 2. 数据库变更
- 修改 `init-scripts/01-init-db.sql`
- 重新启动服务：`./stop-dev.sh && ./start-dev.sh`

### 3. 依赖更新
- 后端：修改 `pom.xml` 后重新构建
- 前端：修改 `frontend/package.json` 后重新安装依赖

## 环境配置

### 自定义配置

编辑 `.env.dev` 文件来自定义环境变量：

```bash
# 修改数据库密码
DB_PASS=your_new_password

# 修改服务端口
SERVER_PORT=9090
VITE_DEV_SERVER_PORT=3000
```

### 添加新服务

在 `docker-compose.dev.yml` 中添加新服务定义：

```yaml
services:
  new-service:
    image: some-image:latest
    # ... 其他配置
```

## 性能优化

### 开发环境优化

1. **增加Docker资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
         cpus: '2.0'
   ```

2. **使用本地开发模式**
   - 后端：直接在IDE中运行Spring Boot应用
   - 前端：直接在宿主机运行 `npm run dev`

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 技术支持

如有问题，请查看：
- [项目Wiki]()
- [Issue Tracker]()
- 联系开发团队

---

**祝您开发愉快！** 🚀