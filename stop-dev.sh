#!/bin/bash

# 碑说项目开发环境停止脚本

echo "🛑 停止碑说项目开发环境..."

# 检查Docker Compose文件是否存在
if [ ! -f "docker-compose.dev.yml" ]; then
    echo "❌ docker-compose.dev.yml 文件不存在"
    exit 1
fi

# 停止服务
docker-compose -f docker-compose.dev.yml down

echo "✅ 开发环境已停止"
echo ""
echo "💡 如需重新启动，请运行: ./start-dev.sh"