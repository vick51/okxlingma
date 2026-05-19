# Ubuntu 24.04 部署指南

## 系统要求

- Ubuntu 24.04 LTS (Noble)
- Docker 20.10+
- Docker Compose V2

## 快速开始

### 1. 安装Docker（如果未安装）

```bash
# 更新包索引
sudo apt update

# 安装依赖
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
sudo docker --version
sudo docker compose version
```

### 2. 配置项目

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置，填写OKX API密钥
vim .env
```

### 3. 赋予脚本执行权限

```bash
chmod +x start.sh stop.sh restart.sh commit.sh
```

### 4. 启动系统

```bash
./start.sh
```

### 5. 访问Web界面

浏览器打开: http://localhost:5000

---

## 常用命令（需要sudo）

```bash
# 启动
sudo docker compose up -d

# 停止
sudo docker compose down

# 重启
sudo docker compose restart

# 查看日志
sudo docker compose logs -f

# 查看状态
sudo docker compose ps

# 重新构建
sudo docker compose build --no-cache

# 进入容器
sudo docker exec -it okx-trading-system bash
```

---

## 使用脚本（推荐）

```bash
# 启动
./start.sh

# 停止
./stop.sh

# 重启
./restart.sh

# Git提交
./commit.sh
```

---

## 故障排查

### 问题1: Permission denied

**解决**: 所有docker命令都需要sudo
```bash
sudo docker compose up -d
```

或者将用户加入docker组（不推荐，有安全风险）:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 问题2: Docker服务未启动

**解决**:
```bash
sudo systemctl start docker
sudo systemctl enable docker  # 开机自启
```

### 问题3: 端口被占用

**解决**:
```bash
# 查看占用端口的进程
sudo lsof -i :5000

# 停止占用的进程
sudo kill -9 <PID>
```

### 问题4: 数据目录权限问题

**解决**:
```bash
sudo chmod 777 data/
```

---

## 安全建议

### 1. 不要将用户加入docker组

docker组有root权限，建议使用sudo。

### 2. 限制API密钥权限

在OKX创建API时：
- 只勾选必要的权限（读取、交易）
- 设置IP白名单
- 定期更换密钥

### 3. 防火墙配置

```bash
# 只允许本地访问5000端口
sudo ufw allow from 127.0.0.1 to any port 5000

# 启用防火墙
sudo ufw enable
```

### 4. 定期更新

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 更新Docker
sudo apt update && sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

---

## 性能优化

### 1. 调整Docker资源限制

编辑 `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
```

### 2. 清理Docker缓存

```bash
# 清理未使用的镜像和容器
sudo docker system prune -a

# 清理卷
sudo docker volume prune
```

### 3. 监控资源使用

```bash
# 实时监控
sudo docker stats okx-trading-system

# 查看系统资源
htop
```

---

## 备份和恢复

### 备份数据库

```bash
# 手动备份
sudo cp data/trading.db data/trading.db.backup.$(date +%Y%m%d)

# 定时备份（添加到crontab）
crontab -e
# 每天凌晨2点备份
0 2 * * * cp /path/to/data/trading.db /path/to/backups/trading.db.$(date +\%Y\%m\%d)
```

### 恢复数据

```bash
sudo cp data/trading.db.backup.20260519 data/trading.db
sudo docker compose restart
```

---

## 开机自启

系统已经配置了 `restart: unless-stopped`，Docker服务启动后容器会自动运行。

```bash
# 确保Docker开机自启
sudo systemctl enable docker

# 重启测试
sudo reboot

# 重启后检查
sudo docker compose ps
```

---

## 日志管理

### 查看日志

```bash
# 实时日志
sudo docker compose logs -f

# 最近100行
sudo docker compose logs --tail=100

# 仅错误
sudo docker compose logs | grep ERROR

# 导出日志
sudo docker compose logs > logs/$(date +%Y%m%d).log
```

### 日志轮转

已在 `docker-compose.yml` 中配置：
```yaml
logging:
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 相关文档

- `README.md` - 完整使用文档
- `DOCKER_DEPLOY.md` - Docker详细部署指南
- `GIT_GUIDE.md` - Git使用指南
- `QUICK_START.md` - 快速开始

---

**提示**: Ubuntu环境下，所有docker命令都需要加sudo！
