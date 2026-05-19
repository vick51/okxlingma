# Docker Compose 部署指南

## 快速开始（3步启动）

### Windows用户

1. **双击运行**: `start.bat`
2. **等待启动**: 约15-30秒
3. **访问界面**: http://localhost:5000

### Linux/Mac用户

```bash
# 1. 赋予执行权限
chmod +x start.sh

# 2. 启动系统
./start.sh

# 3. 访问界面
# http://localhost:5000
```

---

## 详细部署步骤

### 第一步：准备配置文件

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# Windows: notepad .env
# Linux/Mac: vim .env
```

**必须填写的内容**：
```env
OKX_API_KEY=你的API密钥
OKX_SECRET_KEY=你的密钥
OKX_PASSPHRASE=你的密码短语
```

### 第二步：启动服务

**方式1：使用脚本（推荐）**
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

**方式2：手动命令**
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 第三步：验证部署

```bash
# 检查容器状态
docker-compose ps

# 应该看到：
# NAME                 STATUS         PORTS
# okx-trading-system   Up (healthy)   0.0.0.0:5000->5000/tcp
```

访问 http://localhost:5000 确认Web界面正常。

---

## Docker Compose 配置说明

### docker-compose.yml 详解

```yaml
version: '3.8'

services:
  okx-trading:
    build:
      context: .              # 构建上下文（当前目录）
      dockerfile: Dockerfile  # Dockerfile路径
    
    container_name: okx-trading-system  # 容器名称
    
    ports:
      - "${WEB_PORT:-5000}:${WEB_PORT:-5000}"  # 端口映射（可配置）
    
    volumes:
      - ./data:/app/data           # 数据持久化
      - ./.env:/app/.env:ro        # 配置文件（只读）
    
    environment:
      - TZ=Asia/Shanghai          # 时区设置
      - FLASK_PORT=${WEB_PORT:-5000}
    
    restart: unless-stopped       # 自动重启策略
    
    healthcheck:                  # 健康检查
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s               # 每30秒检查一次
      timeout: 10s                # 超时时间
      retries: 3                  # 重试次数
      start_period: 15s           # 启动宽限期
    
    deploy:
      resources:
        limits:
          memory: 512M            # 内存上限
          cpus: '0.5'             # CPU上限
        reservations:
          memory: 128M            # 内存预留
    
    logging:                      # 日志配置
      driver: "json-file"
      options:
        max-size: "10m"           # 单文件最大10MB
        max-file: "3"             # 保留3个文件
    
    networks:
      - trading-network           # 自定义网络

networks:
  trading-network:
    driver: bridge                # 桥接网络
```

---

## 常用命令速查

### 基础操作

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志（实时）
docker-compose logs -f

# 查看日志（最近100行）
docker-compose logs --tail=100
```

### 高级操作

```bash
# 重新构建镜像
docker-compose build --no-cache

# 更新服务（代码修改后）
docker-compose up -d --build

# 进入容器内部
docker exec -it okx-trading-system bash

# 查看资源使用
docker stats okx-trading-system

# 完全清理（删除容器、网络、镜像）
docker-compose down --rmi all --volumes
```

### 数据管理

```bash
# 备份数据库
cp data/trading.db data/trading.db.backup.$(date +%Y%m%d)

# 恢复数据库
cp data/trading.db.backup.20260519 data/trading.db
docker-compose restart

# 查看数据库大小
du -sh data/

# 清理旧日志
docker-compose logs --tail=100 > logs/latest.log
```

---

## 配置自定义

### 修改Web端口

编辑 `.env` 文件：
```env
WEB_PORT=8080
```

重启服务：
```bash
docker-compose down
docker-compose up -d
```

访问地址变为：http://localhost:8080

### 调整资源限制

编辑 `docker-compose.yml`：
```yaml
deploy:
  resources:
    limits:
      memory: 1G        # 增加内存限制
      cpus: '1.0'       # 增加CPU限制
```

重启生效：
```bash
docker-compose up -d
```

### 修改日志配置

编辑 `docker-compose.yml`：
```yaml
logging:
  options:
    max-size: "50m"     # 增大日志文件
    max-file: "5"       # 增加保留数量
```

---

## 故障排查

### 问题1：端口被占用

**错误信息**：
```
Error starting userland proxy: bind tcp 0.0.0.0:5000: bind: address already in use
```

**解决方案**：
```bash
# 方案1：修改端口
echo "WEB_PORT=8080" >> .env
docker-compose up -d

# 方案2：找出并停止占用端口的进程
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### 问题2：镜像构建失败

**错误信息**：
```
ERROR: Service 'okx-trading' failed to build
```

**解决方案**：
```bash
# 清理Docker缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache

# 查看详细错误
docker-compose build --progress=plain
```

### 问题3：容器启动后立即退出

**检查日志**：
```bash
docker-compose logs --tail=50
```

**常见原因**：
1. `.env` 文件配置错误
2. API密钥无效
3. 数据库权限问题

**解决方案**：
```bash
# 检查.env文件
cat .env

# 修复权限
chmod -R 777 data/

# 重新启动
docker-compose down
docker-compose up -d
```

### 问题4：健康检查失败

**检查状态**：
```bash
docker inspect okx-trading-system | grep Health -A 10
```

**解决方案**：
```bash
# 进入容器测试
docker exec -it okx-trading-system curl http://localhost:5000/api/status

# 如果失败，查看应用日志
docker exec -it okx-trading-system cat data/trading.log
```

### 问题5：数据丢失

**预防措施**：
```bash
# 定期备份
cp data/trading.db backups/trading.db.$(date +%Y%m%d)

# 使用数据卷（更可靠）
# 修改 docker-compose.yml
volumes:
  - okx-data:/app/data

volumes:
  okx-data:
```

---

## 性能优化

### 1. 启用BuildKit加速构建

```bash
# 设置环境变量
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 构建
docker-compose build
```

### 2. 使用国内镜像源

修改 `Dockerfile`：
```dockerfile
# 使用清华镜像源
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 3. 多阶段构建（减小镜像）

```dockerfile
# 构建阶段
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# 运行阶段
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "app.py"]
```

---

## 安全加固

### 1. 限制网络访问

```yaml
# docker-compose.yml
ports:
  - "127.0.0.1:5000:5000"  # 只允许本地访问
```

### 2. 添加认证

```python
# app.py
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username == os.getenv('WEB_USER', 'admin') and \
       password == os.getenv('WEB_PASSWORD', 'password'):
        return username

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

### 3. 使用Secrets管理敏感信息

```yaml
# docker-compose.yml
secrets:
  okx_api_key:
    file: ./secrets/okx_api_key.txt
  okx_secret_key:
    file: ./secrets/okx_secret_key.txt

services:
  okx-trading:
    secrets:
      - okx_api_key
      - okx_secret_key
```

---

## 监控和日志

### 查看实时日志

```bash
# 所有日志
docker-compose logs -f

# 仅错误日志
docker-compose logs -f | grep ERROR

# 仅交易日志
docker-compose logs -f | grep "交易"
```

### 导出日志

```bash
# 导出到文件
docker-compose logs --tail=1000 > logs/export_$(date +%Y%m%d).log

# 按日期归档
docker-compose logs --since="2026-05-19" > logs/2026-05-19.log
```

### 监控资源

```bash
# 实时监控
docker stats okx-trading-system

# 一次性查看
docker stats --no-stream okx-trading-system
```

---

## 备份和恢复

### 自动备份脚本

创建 `backup.sh`：
```bash
#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp data/trading.db $BACKUP_DIR/trading_$TIMESTAMP.db

# 备份配置
cp .env $BACKUP_DIR/env_$TIMESTAMP

# 压缩
tar czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz $BACKUP_DIR/*_$TIMESTAMP*

# 清理7天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: backup_$TIMESTAMP.tar.gz"
```

### 定时备份

```bash
# 添加到crontab（每天凌晨2点）
crontab -e
0 2 * * * /path/to/backup.sh
```

### 恢复数据

```bash
# 解压备份
tar xzf backups/backup_20260519.tar.gz

# 恢复数据库
cp backups/trading_20260519.db data/trading.db

# 重启服务
docker-compose restart
```

---

## 更新和升级

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build --no-cache

# 重启服务
docker-compose up -d

# 查看新版本
docker-compose logs | grep "版本"
```

### 更新依赖

```bash
# 编辑 requirements.txt
vim requirements.txt

# 重新构建
docker-compose build

# 重启
docker-compose up -d
```

---

## 生产环境建议

### 1. 使用固定标签

```yaml
# docker-compose.yml
services:
  okx-trading:
    image: okx-trading:v1.0.0  # 使用固定版本标签
```

### 2. 启用监控

```yaml
# 添加Prometheus监控
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

### 3. 日志聚合

```yaml
# 使用ELK Stack
services:
  elasticsearch:
    image: elasticsearch:7.17.0
  kibana:
    image: kibana:7.17.0
  logstash:
    image: logstash:7.17.0
```

### 4. 高可用部署

```yaml
# 使用Docker Swarm或Kubernetes
# docker-compose.yml
version: '3.8'
services:
  okx-trading:
    deploy:
      replicas: 2  # 多副本
      restart_policy:
        condition: on-failure
```

---

## 常见问题FAQ

### Q: 如何修改策略执行频率？
A: 修改 `app.py` 中的调度器配置，然后重新构建镜像。

### Q: 数据库文件在哪里？
A: 在 `./data/trading.db`，已挂载到宿主机。

### Q: 如何重置系统？
A: 删除 `data/` 目录，重启容器会自动初始化。

### Q: 支持多个交易对吗？
A: 当前版本支持单交易对，多交易对需要修改代码。

### Q: 如何在后台运行？
A: 使用 `docker-compose up -d` 即可后台运行。

---

## 获取帮助

- 查看日志: `docker-compose logs -f`
- 查阅文档: `README.md`
- 检查清单: `DEPLOYMENT_CHECKLIST.md`

---

**最后更新**: 2026-05-19
