#!/bin/bash

# 碑说项目一键运行脚本
# 适用于协作开发环境

set -e

echo "🚀 启动碑说项目..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f "python/.env" ]; then
    echo "⚠️  未找到环境变量文件，正在创建..."
    
    # 复制示例文件
    if [ -f "python/env.example" ]; then
        cp python/env.example python/.env
        echo "✅ 已创建环境变量文件，请编辑 python/.env 文件配置您的API密钥"
    else
        echo "❌ 未找到环境变量示例文件"
        exit 1
    fi
fi

# 检查必要的环境变量是否已配置
if grep -q "YOUR_API_KEY_HERE" python/.env; then
    echo "⚠️  请先配置 python/.env 文件中的API密钥"
    echo "   需要配置的密钥包括："
    echo "   - LLM_API_KEY (DashScope API密钥)"
    echo "   - KANDIANGUJI_OCR_TOKEN (看店古籍OCR Token)"
    echo "   - KANDIANGUJI_OCR_EMAIL (看店古籍OCR邮箱)"
    echo ""
    read -p "是否继续启动服务？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 用户取消启动"
        exit 0
    fi
fi

# 创建必要的目录
mkdir -p python/uploads

# 构建并启动服务
echo "📦 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🌐 访问地址："
    echo "   前端：http://localhost:5173"
    echo "   后端API文档：http://localhost:8080/docs"
    echo ""
    echo "📋 常用命令："
    echo "   查看日志：docker-compose logs -f"
    echo "   停止服务：docker-compose down"
    echo "   重启服务：docker-compose restart"
    echo ""
else
    echo "❌ 服务启动失败，请检查日志：docker-compose logs"
    exit 1
fi