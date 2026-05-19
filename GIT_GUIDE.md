# Git 使用指南

## 快速提交

### Windows用户
```bash
commit.bat
```

### Linux/Mac用户
```bash
chmod +x commit.sh
./commit.sh
```

## 手动Git操作

### 1. 初始化仓库（首次使用）
```bash
git init
git add .
git commit -m "初始提交: OKX量化交易系统"
```

### 2. 添加远程仓库
```bash
git remote add origin <your_repository_url>
git branch -M main
git push -u origin main
```

### 3. 日常提交
```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交
git commit -m "提交说明"

# 推送
git push
```

### 4. 查看历史
```bash
# 查看提交历史
git log

# 查看简洁历史
git log --oneline

# 查看最近5条
git log -5
```

### 5. 分支管理
```bash
# 创建新分支
git checkout -b feature-new

# 切换分支
git checkout main

# 合并分支
git merge feature-new

# 删除分支
git branch -d feature-new
```

## 自动提交脚本

### 功能
- ✅ 自动检测Git仓库
- ✅ 显示当前状态
- ✅ 添加所有更改
- ✅ 自动生成提交信息（带时间戳）
- ✅ 询问是否推送到远程

### 使用方法

**Windows**:
```bash
commit.bat
```

**Linux/Mac**:
```bash
chmod +x commit.sh
./commit.sh
```

## .gitignore 说明

以下文件不会被提交到Git：

### 敏感信息
- `.env` - 包含API密钥等敏感配置

### 运行时生成
- `data/*.db` - SQLite数据库
- `data/*.log` - 日志文件
- `__pycache__/` - Python缓存

### 开发环境
- `venv/` - Python虚拟环境
- `.vscode/` - VSCode配置
- `.idea/` - PyCharm配置

### 其他
- `*.backup` - 备份文件
- `logs/` - 日志目录
- `backups/` - 备份目录

## 最佳实践

### 1. 提交频率
- 完成一个功能就提交
- 不要累积太多更改
- 提交前测试代码

### 2. 提交信息
```bash
# 好的提交信息
git commit -m "修复: MACD指标计算错误"
git commit -m "新增: 邮件通知功能"
git commit -m "优化: Docker构建速度"

# 避免的提交信息
git commit -m "更新"
git commit -m "修复bug"
git commit -m "."
```

### 3. 分支策略
```
main          - 主分支（稳定版本）
develop       - 开发分支
feature/*     - 功能分支
bugfix/*      - 修复分支
```

### 4. 保护敏感信息
```bash
# 永远不要提交 .env 文件
echo ".env" >> .gitignore

# 如果已经提交了敏感文件
git rm --cached .env
git commit -m "移除敏感的.env文件"
```

## 常见问题

### Q1: 如何撤销提交？
```bash
# 撤销最后一次提交（保留更改）
git reset --soft HEAD~1

# 撤销并提交暂存
git reset HEAD~1

# 完全撤销（丢弃更改）
git reset --hard HEAD~1
```

### Q2: 如何修改提交信息？
```bash
# 修改最后一次提交信息
git commit --amend -m "新的提交信息"
```

### Q3: 如何忽略已跟踪的文件？
```bash
# 从Git中移除但保留本地文件
git rm --cached filename
git commit -m "移除文件"
```

### Q4: 如何回退到某个版本？
```bash
# 查看提交历史
git log --oneline

# 回退到指定commit
git reset --hard <commit_hash>
```

### Q5: 如何解决冲突？
```bash
# 1. 拉取最新代码
git pull

# 2. 如果有冲突，编辑冲突文件
# 查找 <<<<<<<, =======, >>>>>>> 标记

# 3. 解决冲突后
git add .
git commit -m "解决冲突"
```

## Git Hooks（可选）

### 自动提交前检查
创建 `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# 提交前运行测试
python -m pytest tests/ -q
if [ $? -ne 0 ]; then
    echo "测试失败，阻止提交"
    exit 1
fi
```

## 推荐工具

### GUI客户端
- **Windows**: TortoiseGit, GitHub Desktop
- **Mac**: GitHub Desktop, Sourcetree
- **Linux**: GitKraken, Sourcetree

### VSCode插件
- GitLens
- Git Graph
- Git History

## 参考资源

- [Git官方文档](https://git-scm.com/doc)
- [Git教程 - 菜鸟教程](https://www.runoob.com/git/git-tutorial.html)
- [Pro Git书籍](https://git-scm.com/book/zh/v2)

---

**提示**: 定期提交和推送是良好的开发习惯！
