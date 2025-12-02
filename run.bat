@echo off
chcp 65001 >nul

echo 🚀 启动碑说项目...

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 检查环境变量文件
if not exist "python\.env" (
    echo ⚠️  未找到环境变量文件，正在创建...
    
    REM 复制示例文件
    if exist "python\env.example" (
        copy "python\env.example" "python\.env"
        echo ✅ 已创建环境变量文件，请编辑 python\.env 文件配置您的API密钥
    ) else (
        echo ❌ 未找到环境变量示例文件
        pause
        exit /b 1
    )
)

REM 检查必要的环境变量是否已配置
findstr /C:"YOUR_API_KEY_HERE" "python\.env" >nul
if %errorlevel% equ 0 (
    echo ⚠️  请先配置 python\.env 文件中的API密钥
    echo    需要配置的密钥包括：
    echo    - LLM_API_KEY (DashScope API密钥)
    echo    - KANDIANGUJI_OCR_TOKEN (看店古籍OCR Token)
    echo    - KANDIANGUJI_OCR_EMAIL (看店古籍OCR邮箱)
    echo.
    set /p "continue=是否继续启动服务？(y/N): "
    if /i not "%continue%"=="y" (
        echo ❌ 用户取消启动
        pause
        exit /b 0
    )
)

REM 创建必要的目录
if not exist "python\uploads" mkdir "python\uploads"

REM 构建并启动服务
echo 📦 构建Docker镜像...
docker-compose build

echo 🚀 启动服务...
docker-compose up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ 服务启动成功！
    echo.
    echo 🌐 访问地址：
    echo    前端：http://localhost:5173
    echo    后端API文档：http://localhost:8080/docs
    echo.
    echo 📋 常用命令：
    echo    查看日志：docker-compose logs -f
    echo    停止服务：docker-compose down
    echo    重启服务：docker-compose restart
    echo.
) else (
    echo ❌ 服务启动失败，请检查日志：docker-compose logs
    pause
    exit /b 1
)

pause