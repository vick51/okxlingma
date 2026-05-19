#!/bin/bash

echo "========================================="
echo "  OKX量化交易系统 - Docker Compose V2 重启"
echo "========================================="
echo ""

# 检查Docker是否运行
if ! sudo docker info &> /dev/null; then
    echo "❌ 错误: Docker 服务未运行"
    exit 1
fi

echo "🔄 正在重启服务..."
sudo docker compose restart

if [ $? -eq 0 ]; then
    echo ""
    echo "⏳ 等待服务启动（10秒）..."
    sleep 10
    
    echo ""
    echo "🔍 服务状态..."
    sudo docker compose ps
    
    echo ""
    echo "========================================="
    echo "  ✅ 服务已重启"
    echo "========================================="
    echo ""
    echo "📊 Web界面: http://localhost:5000"
    echo ""
else
    echo ""
    echo "❌ 重启失败"
    echo "尝试完全重启..."
    sudo docker compose down
    sudo docker compose up -d
fi
