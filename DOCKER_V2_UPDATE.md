# Docker Compose V2 更新说明

## 重要变更

从 **Docker Compose V1** 升级到 **V2**，命令发生变化：

### 旧命令（V1）
```bash
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose ps
docker-compose build
```

### 新命令（V2）
```bash
docker compose up -d
docker compose down
docker compose logs -f
docker compose ps
docker compose build
```

**主要区别**: `docker-compose` → `docker compose`（连改为空格）

---

## 版本要求

- **Docker**: >= 20.10
- **Docker Compose**: V2（作为Docker插件内置）

检查版本：
```bash
docker --version
docker compose version
```

---

## 已更新的文件

以下文件已全部更新为使用 `docker compose` 命令：

### Windows脚本
- ✅ `start.bat` - 启动脚本
- ✅ `stop.bat` - 停止脚本
- ✅ `restart.bat` - 重启脚本

### Linux/Mac脚本
- ✅ `start.sh` - 启动脚本
- ✅ `stop.sh` - 停止脚本

### 文档
- ✅ `README.md`
- ✅ `DOCKER_DEPLOY.md`
- ✅ `DOCKER_README.md`
- ✅ `QUICK_START.md`
- ✅ `DEPLOYMENT_CHECKLIST.md`

---

## 快速开始（使用新命令）

### Windows用户
```bash
# 方式1：使用脚本（推荐）
start.bat

# 方式2：手动命令
docker compose up -d
```

### Linux/Mac用户
```bash
# 方式1：使用脚本（推荐）
chmod +x start.sh
./start.sh

# 方式2：手动命令
docker compose up -d
```

---

## 常用命令对照表

| 操作 | V1命令 | V2命令 |
|------|--------|--------|
| 启动 | `docker-compose up -d` | `docker compose up -d` |
| 停止 | `docker-compose down` | `docker compose down` |
| 重启 | `docker-compose restart` | `docker compose restart` |
| 日志 | `docker-compose logs -f` | `docker compose logs -f` |
| 状态 | `docker-compose ps` | `docker compose ps` |
| 构建 | `docker-compose build` | `docker compose build` |
| 进入容器 | `docker exec -it` | `docker exec -it` (不变) |
| 查看版本 | `docker-compose version` | `docker compose version` |

---

## 兼容性说明

### 如果您的系统仍使用V1

某些旧系统可能还未升级到V2，可以使用兼容方案：

#### 方案1：安装V2插件
```bash
# Docker Desktop >= 20.10 已内置V2
# Linux手动安装
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

#### 方案2：创建别名（临时方案）
```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias docker-compose='docker compose'

# 生效
source ~/.bashrc
```

#### 方案3：同时保留V1和V2
```bash
# 检查是否有V1
which docker-compose

# 检查是否有V2
docker compose version

# 可以两者共存，根据需要选择
```

---

## V2的优势

### 1. 更好的性能
- 启动速度更快
- 内存占用更少
- 并行处理优化

### 2. 更好的集成
- 作为Docker CLI插件
- 统一的命令行体验
- 更好的错误提示

### 3. 新特性支持
- Compose Specification完全支持
- 更好的profiles支持
- 增强的secrets管理
- Watch模式（开发时自动同步）

### 4. 长期维护
- V1已停止新功能开发
- V2是未来发展方向
- Docker官方推荐

---

## 迁移指南

### 从V1迁移到V2

#### 步骤1：检查当前版本
```bash
docker-compose version  # V1
docker compose version  # V2
```

#### 步骤2：更新脚本
将所有 `docker-compose` 替换为 `docker compose`

#### 步骤3：测试
```bash
# 测试基本功能
docker compose ps
docker compose logs

# 测试完整流程
docker compose down
docker compose up -d
```

#### 步骤4：卸载V1（可选）
```bash
# Ubuntu/Debian
sudo apt-get remove docker-compose

# CentOS/RHEL
sudo yum remove docker-compose

# macOS
brew uninstall docker-compose

# Windows
# 通过"添加或删除程序"卸载
```

---

## 常见问题

### Q1: 如何确认使用的是V2？
```bash
docker compose version
# 输出类似: Docker Compose version v2.20.0
```

### Q2: V1和V2能共存吗？
是的，可以同时安装：
- V1: `docker-compose` 命令
- V2: `docker compose` 命令

### Q3: docker-compose.yml需要修改吗？
不需要，配置文件格式完全兼容。

### Q4: 如果命令找不到怎么办？
```bash
# 检查Docker是否安装
docker --version

# 检查Compose插件
docker compose version

# 如果未安装V2，升级Docker Desktop
# 或安装compose插件
```

### Q5: CI/CD管道需要更新吗？
是的，建议将所有CI/CD脚本中的 `docker-compose` 更新为 `docker compose`。

---

## 参考资源

- [Docker Compose V2官方文档](https://docs.docker.com/compose/)
- [Compose Specification](https://github.com/compose-spec/compose-spec)
- [从V1迁移到V2](https://docs.docker.com/compose/migrate/)

---

**更新日期**: 2026-05-19  
**适用版本**: Docker Compose V2.x
