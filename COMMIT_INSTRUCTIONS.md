# Git 提交指南

## 快速提交（推荐）

### Windows用户
双击运行或在命令行执行：
```bash
commit.bat
```

### Linux/Mac用户
```bash
chmod +x commit.sh
./commit.sh
```

---

## 手动提交命令

如果您想手动提交，请按以下步骤操作：

### 1. 检查状态
```bash
git status
```

### 2. 添加所有更改
```bash
git add .
```

### 3. 提交更改
```bash
git commit -m "修复: Docker构建问题 - 移除ta-lib依赖，改用pandas原生实现

- 移除ta-lib，使用pandas原生实现MACD指标
- 简化Dockerfile，移除TA-Lib编译步骤
- 更新requirements.txt依赖版本
- 添加Git自动提交脚本
- 更新为Docker Compose V2命令格式"
```

### 4. 推送到远程仓库（如果有）
```bash
git push
```

---

## 本次提交的主要变更

### 修复的问题
1. ✅ Docker构建失败 - ta-lib编译错误
2. ✅ ccxt版本不存在问题
3. ✅ Docker Compose命令过时

### 核心改动
1. **requirements.txt**
   - 移除 `ta-lib==0.4.28`
   - 添加 `pandas-ta>=0.3.14b0`
   - 修改 `ccxt==4.2.0` → `ccxt>=4.0.0`

2. **Dockerfile**
   - 移除TA-Lib原生库编译步骤
   - 简化系统依赖安装
   - 移除国内镜像源

3. **新增文件**
   - `commit.bat` - Windows自动提交脚本
   - `commit.sh` - Linux/Mac自动提交脚本
   - `GIT_GUIDE.md` - Git使用指南
   - `CHANGELOG.md` - 更新日志
   - `DOCKER_V2_UPDATE.md` - Docker V2说明

4. **更新的文档**
   - `README.md` - 更新Docker命令
   - `start.bat/sh`, `stop.bat/sh`, `restart.bat` - 使用docker compose V2

---

## 验证清单

提交前请确认：

- [ ] 代码可以正常运行
- [ ] Docker可以成功构建
- [ ] .env文件未被提交（在.gitignore中）
- [ ] data目录未被提交（在.gitignore中）
- [ ] venv目录未被提交（在.gitignore中）

---

## 如果遇到问题

### 问题1: Git未初始化
```bash
git init
git add .
git commit -m "初始提交"
```

### 问题2: 没有远程仓库
```bash
# 先在GitHub/GitLab创建仓库
git remote add origin <your_repo_url>
git branch -M main
git push -u origin main
```

### 问题3: 提交冲突
```bash
git pull --rebase
# 解决冲突后
git add .
git rebase --continue
```

---

## 提交后的操作

1. **重新构建Docker镜像**:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

2. **测试系统**:
   - 访问 http://localhost:5000
   - 检查Web界面是否正常
   - 查看日志确认无错误

3. **推送到远程** (如果需要):
   ```bash
   git push
   ```

---

**提示**: 建议使用自动提交脚本 `commit.bat` 或 `./commit.sh`，它会自动处理大部分步骤！
