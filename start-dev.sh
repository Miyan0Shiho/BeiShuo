#!/bin/bash

# 碑说项目一键开发环境部署脚本
# 确保项目能在其他电脑上一键部署并启动前后端进行开发调试

set -e

echo "🚀 开始部署碑说项目开发环境..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查项目结构
echo "📁 检查项目结构..."
if [ ! -d "frontend" ]; then
    echo "❌ 前端目录不存在，请检查项目结构"
    exit 1
fi

# 检查后端项目结构
if [ ! -d "src/main/java" ]; then
    echo "❌ 后端项目结构不完整，请检查项目结构"
    exit 1
fi

echo "✅ 项目结构检查通过"

# 创建必要的目录
echo "📂 创建必要目录..."
mkdir -p data/faiss uploads logs

# 检查并构建后端镜像
echo "🔨 构建后端镜像..."
if [ ! -f "target/app.jar" ]; then
    echo "📦 编译后端项目..."
    docker run --rm -v "$(pwd):/app" -w /app maven:3.9.6-eclipse-temurin-17 mvn clean package -DskipTests
fi

# 检查并安装前端依赖
echo "📦 安装前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖包..."
    cd frontend
    docker run --rm -v "$(pwd):/app" -w /app node:18-alpine npm ci
    cd ..
fi

# 启动开发环境
echo "🚀 启动开发环境..."
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ 等待服务启动..."

# 等待后端服务启动
for i in {1..30}; do
    if curl -f http://localhost:8080/actuator/health >/dev/null 2>&1; then
        echo "✅ 后端服务启动成功"
        break
    fi
    echo "⏳ 等待后端服务启动... ($i/30)"
    sleep 5
    if [ $i -eq 30 ]; then
        echo "❌ 后端服务启动超时"
        docker-compose -f docker-compose.dev.yml logs backend
        exit 1
    fi
done

# 等待前端服务启动
for i in {1..30}; do
    if curl -f http://localhost:5173 >/dev/null 2>&1; then
        echo "✅ 前端服务启动成功"
        break
    fi
    echo "⏳ 等待前端服务启动... ($i/30)"
    sleep 5
    if [ $i -eq 30 ]; then
        echo "❌ 前端服务启动超时"
        docker-compose -f docker-compose.dev.yml logs frontend
        exit 1
    fi
done

echo ""
echo "🎉 碑说项目开发环境部署完成！"
echo ""
echo "📋 服务访问地址："
echo "   前端开发服务器: http://localhost:5173"
echo "   后端API服务: http://localhost:8080"
echo "   数据库管理: localhost:5432 (用户名: beishuo, 密码: beishuo123)"
echo "   Redis管理: localhost:6379"
echo "   对象存储管理: http://localhost:9001 (用户名: minioadmin, 密码: minioadmin)"
echo ""
echo "🔧 常用命令："
echo "   查看服务状态: docker-compose -f docker-compose.dev.yml ps"
echo "   查看服务日志: docker-compose -f docker-compose.dev.yml logs -f [服务名]"
echo "   停止服务: docker-compose -f docker-compose.dev.yml down"
echo "   重新构建: docker-compose -f docker-compose.dev.yml build"
echo ""
echo "💡 开始愉快的开发吧！"