#!/bin/bash

echo "========================================="
echo "  OKX量化交易系统 - Docker Compose V2 启动"
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

# 检查Docker Compose V2是否安装
if ! sudo docker compose version &> /dev/null; then
    echo "❌ 错误: Docker Compose V2 未安装"
    echo "请确保 Docker 版本 >= 20.10"
    exit 1
fi

# 检查Docker是否运行
if ! sudo docker info &> /dev/null; then
    echo "❌ 错误: Docker 服务未运行"
    echo "请启动 Docker: sudo systemctl start docker"
    exit 1
fi

echo "✅ Docker版本: $(sudo docker --version)"
echo "✅ Docker Compose版本: $(sudo docker compose version | head -n 1)"
echo ""

echo "🚀 开始启动系统..."
echo ""

# 创建数据目录
mkdir -p data
sudo chmod 777 data
echo "📁 数据目录已就绪"

# 检查是否有旧容器在运行
if sudo docker compose ps 2>/dev/null | grep -q "Up"; then
    echo "⚠️  检测到运行中的容器，先停止..."
    sudo docker compose down
    echo ""
fi

# 构建并启动服务
echo "🔨 正在构建Docker镜像..."
sudo docker compose build

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 镜像构建失败"
    echo "请查看上方错误信息"
    exit 1
fi

echo ""
echo "🚀 正在启动Docker容器..."
sudo docker compose up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 容器启动失败"
    echo "请查看上方错误信息"
    exit 1
fi

# 等待服务启动
echo ""
echo "⏳ 等待服务启动（15秒）..."
sleep 15

# 检查服务状态
echo ""
echo "🔍 验证服务状态..."
sudo docker compose ps

echo ""
if sudo docker compose ps | grep -q "Up"; then
    echo ""
    echo "========================================="
    echo "  ✅ 系统启动成功！"
    echo "========================================="
    echo ""
    echo "📊 Web界面: http://localhost:5000"
    echo ""
    echo "📝 常用命令："
    echo "  查看日志: sudo docker compose logs -f"
    echo "  停止服务: sudo docker compose down"
    echo "  重启服务: sudo docker compose restart"
    echo "  查看状态: sudo docker compose ps"
    echo ""
    echo "💡 提示：首次启动需要一些时间初始化数据库"
    echo ""
else
    echo ""
    echo "========================================="
    echo "  ❌ 启动失败，请查看日志"
    echo "========================================="
    echo ""
    sudo docker compose logs --tail=50
    echo ""
    echo "常见问题："
    echo "1. 检查 .env 文件配置是否正确"
    echo "2. 确认端口 5000 未被占用"
    echo "3. 查看完整日志: sudo docker compose logs"
    echo ""
fi
