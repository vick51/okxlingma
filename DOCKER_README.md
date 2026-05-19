# Docker Compose 部署 - 快速参考

## 🚀 30秒快速启动

### Windows用户
```bash
start.bat
```

### Linux/Mac用户
```bash
chmod +x start.sh && ./start.sh
```

### 访问系统
```
http://localhost:5000
```

---

## 📋 部署前准备

### 1. 安装Docker
- **Windows**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Mac**: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- **Linux**: `curl -fsSL https://get.docker.com | sh`

### 2. 配置文件
```bash
cp .env.example .env
# 编辑 .env 填写OKX API密钥
```

### 3. 启动
```bash
docker-compose up -d
```

---

## 🛠️ 常用命令

| 操作 | 命令 | 说明 |
|------|------|------|
| 启动 | `docker-compose up -d` | 后台启动服务 |
| 停止 | `docker-compose down` | 停止并删除容器 |
| 重启 | `docker-compose restart` | 重启服务 |
| 日志 | `docker-compose logs -f` | 实时查看日志 |
| 状态 | `docker-compose ps` | 查看容器状态 |
| 进入 | `docker exec -it okx-trading-system bash` | 进入容器内部 |
| 构建 | `docker-compose build` | 重新构建镜像 |
| 更新 | `docker-compose up -d --build` | 更新并重启 |

---

## 📊 系统架构

```
┌─────────────────────────────────────┐
│     Docker Container                │
│                                     │
│  ┌──────────┐    ┌──────────────┐  │
│  │  Flask   │◄──►│ Trading      │  │
│  │  Web UI  │    │ Engine       │  │
│  └────┬─────┘    └──────┬───────┘  │
│       │                 │           │
│  ┌────┴─────────────────┴──────┐   │
│  │     SQLite Database         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
         ▲
         │ Port 5000
         ▼
    Web Browser
```

---

## 🔧 配置说明

### docker-compose.yml 关键点

```yaml
services:
  okx-trading:
    ports:
      - "5000:5000"          # Web端口映射
    
    volumes:
      - ./data:/app/data     # 数据持久化
      - ./.env:/app/.env:ro  # 配置文件（只读）
    
    environment:
      - TZ=Asia/Shanghai     # 时区设置
    
    healthcheck:             # 健康检查
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
    
    deploy:
      resources:
        limits:
          memory: 512M       # 内存限制
          cpus: '0.5'        # CPU限制
```

---

## 🔍 故障排查

### 检查容器状态
```bash
docker-compose ps
```

**正常状态**: `Up (healthy)`  
**异常状态**: `Exited`, `Restarting`

### 查看日志
```bash
# 实时日志
docker-compose logs -f

# 最近100行
docker-compose logs --tail=100

# 仅错误
docker-compose logs | grep ERROR
```

### 常见问题

#### 1. 端口被占用
```bash
# 修改端口
echo "WEB_PORT=8080" >> .env
docker-compose up -d
```

#### 2. 镜像构建失败
```bash
# 清理缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

#### 3. 容器无法启动
```bash
# 查看详细错误
docker-compose logs

# 检查配置
cat .env

# 修复权限
chmod -R 777 data/
```

---

## 💾 数据管理

### 备份数据库
```bash
# 手动备份
cp data/trading.db data/trading.db.backup.$(date +%Y%m%d)

# 自动备份（添加到crontab）
0 2 * * * cp /path/to/data/trading.db /path/to/backups/trading.db.$(date +\%Y\%m\%d)
```

### 恢复数据
```bash
cp data/trading.db.backup.20260519 data/trading.db
docker-compose restart
```

### 清理数据
```bash
# 警告：这将删除所有数据！
rm -rf data/*
docker-compose up -d
```

---

## 📈 监控

### 资源使用
```bash
# 实时监控
docker stats okx-trading-system

# 一次性查看
docker stats --no-stream
```

**预期资源占用**:
- 内存: 150-200 MB
- CPU: <5% (空闲), <20% (交易时)

### 健康检查
```bash
# 检查健康状态
docker inspect okx-trading-system | grep Health -A 10

# 测试API
curl http://localhost:5000/api/status
```

---

## 🔐 安全建议

### 1. 保护API密钥
```bash
# 不要将.env提交到Git
chmod 600 .env
```

### 2. 限制网络访问
```yaml
# docker-compose.yml
ports:
  - "127.0.0.1:5000:5000"  # 仅本地访问
```

### 3. 定期更新
```bash
# 每月更新一次
docker-compose pull
docker-compose up -d --build
```

---

## 📚 相关文档

- **完整文档**: [README.md](README.md)
- **详细部署指南**: [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)
- **部署检查清单**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **快速开始**: [QUICK_START.md](QUICK_START.md)

---

## ⚡ 一键脚本

### Windows
- `start.bat` - 启动系统
- `stop.bat` - 停止系统
- `restart.bat` - 重启系统

### Linux/Mac
- `start.sh` - 启动系统
- `stop.sh` - 停止系统

---

## 🎯 下一步

1. ✅ 启动系统: `docker-compose up -d`
2. ✅ 访问界面: http://localhost:5000
3. ✅ 查看日志: `docker-compose logs -f`
4. ✅ 配置策略: 编辑 `.env` 文件
5. ✅ 开始交易: 等待策略执行（每15分钟）

---

**提示**: 首次启动需要1-2分钟初始化数据库和加载依赖。

**支持**: 遇到问题请查看 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) 的故障排查章节。
