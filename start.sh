#!/bin/bash

echo "========================================="
echo "  OKX量化交易系统 - 启动脚本"
echo "========================================="
echo ""

# 检查.env文件是否存在
if [ ! -f .env ]; then
    echo "❌ 错误: .env 文件不存在"
    echo "请先复制示例配置并填写您的API密钥:"
    echo "  cp .env.example .env"
    echo "  vim .env"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ 检查通过，开始启动..."
echo ""

# 创建数据目录
mkdir -p data

# 启动服务
echo "🚀 启动Docker容器..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "========================================="
    echo "  ✅ 系统启动成功！"
    echo "========================================="
    echo ""
    echo "📊 Web界面: http://localhost:5000"
    echo "📝 查看日志: docker-compose logs -f"
    echo "🛑 停止服务: docker-compose down"
    echo ""
else
    echo ""
    echo "========================================="
    echo "  ❌ 启动失败，请查看日志"
    echo "========================================="
    echo ""
    docker-compose logs
fi
