#!/bin/bash

echo "========================================="
echo "  OKX量化交易系统 - Docker Compose V2 停止"
echo "========================================="
echo ""

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误: Docker 服务未运行"
    exit 1
fi

# 检查容器是否运行
if ! docker compose ps | grep -q "Up"; then
    echo "ℹ️  没有运行中的容器"
    exit 0
fi

echo "⚠️  即将停止OKX量化交易系统"
echo ""
read -p "确认停止？(y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ 操作已取消"
    exit 0
fi

echo ""
echo "🛑 正在停止容器..."
docker compose down

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 系统已停止"
    echo "========================================="
    echo ""
    echo "💾 数据已保存至 data/ 目录"
    echo "🔄 下次启动时会自动恢复"
    echo ""
else
    echo ""
    echo "❌ 停止失败"
    docker compose logs --tail=20
fi
