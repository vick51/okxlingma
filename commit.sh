#!/bin/bash

echo "========================================="
echo "  Git 自动提交脚本"
echo "========================================="
echo ""

# 检查是否在Git仓库中
if [ ! -d .git ]; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

# 显示当前状态
echo "📊 当前Git状态:"
git status --short
echo ""

# 添加所有更改
echo "➕ 添加所有更改..."
git add .

if [ $? -ne 0 ]; then
    echo "❌ 错误: 添加文件失败"
    exit 1
fi

# 获取当前时间作为提交信息
COMMIT_MSG="自动提交: $(date '+%Y-%m-%d %H:%M:%S')"

# 检查是否有更改
if git diff --cached --quiet; then
    echo "ℹ️  没有需要提交的更改"
    exit 0
fi

# 提交更改
echo "💾 提交更改..."
echo "提交信息: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "  ✅ 提交完成"
    echo "========================================="
    echo ""

    # 询问是否推送
    read -p "是否推送到远程仓库？(y/n): " push_now
    if [ "$push_now" = "y" ] || [ "$push_now" = "Y" ]; then
        echo "🚀 正在推送..."
        git push

        if [ $? -eq 0 ]; then
            echo "✅ 推送完成"
        else
            echo "❌ 推送失败"
        fi
    fi
else
    echo "❌ 错误: 提交失败"
fi

echo ""
