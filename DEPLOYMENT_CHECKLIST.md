# 部署检查清单

## 部署前检查

### 1. 环境准备
- [ ] Docker已安装（版本20.10+）
- [ ] Docker Compose已安装（版本2.0+）
- [ ] 网络连接正常
- [ ] 磁盘空间充足（至少1GB）

### 2. OKX账户准备
- [ ] OKX账户已注册并实名认证
- [ ] 账户中有足够的USDT余额
- [ ] API密钥已创建
- [ ] API权限包含"交易"和"读取"
- [ ] 记录了API Key、Secret Key、Passphrase
- [ ] **建议**: 先在模拟盘测试

### 3. 邮件配置
- [ ] Outlook邮箱已注册
- [ ] 已启用两步验证
- [ ] 已生成应用专用密码（不是登录密码）
- [ ] 测试SMTP连接是否正常

### 4. 配置文件
- [ ] `.env` 文件已创建
- [ ] OKX_API_KEY 已填写
- [ ] OKX_SECRET_KEY 已填写
- [ ] OKX_PASSPHRASE 已填写
- [ ] EMAIL_USER 已填写
- [ ] EMAIL_PASSWORD 已填写（使用应用专用密码）
- [ ] 其他参数根据需要调整

---

## 部署步骤

### Step 1: 验证配置
```bash
# 检查.env文件是否存在
ls -la .env

# 检查Docker是否可用
docker --version
docker-compose --version
```

### Step 2: 启动服务
```bash
# Windows
docker-compose up -d

# Linux/Mac
./start.sh
```

### Step 3: 检查服务状态
```bash
# 查看容器状态
docker-compose ps

# 应该看到:
# NAME                 STATUS
# okx-trading-system   Up (healthy)
```

### Step 4: 查看日志
```bash
# 实时查看日志
docker-compose logs -f

# 确认以下信息:
# ✅ OKX连接成功
# ✅ 数据库初始化完成
# ✅ 交易引擎初始化完成
# ✅ Web服务器启动在 http://0.0.0.0:5000
# ✅ 策略调度器已启动
```

### Step 5: 访问Web界面
```
浏览器打开: http://localhost:5000

检查:
✅ 页面正常加载
✅ 网络状态显示"已连接"
✅ 账户余额显示正确
✅ 延迟在合理范围（<1000ms）
```

### Step 6: 功能测试
```bash
# 1. 检查持仓显示
# 如果有持仓，应该显示在"当前持仓"区域

# 2. 检查历史订单
# 点击"查询"按钮，应该能加载历史订单

# 3. 检查网络检测
# 点击"检测网络"按钮，应该更新状态

# 4. 检查实时更新
# 观察数据是否每2秒自动刷新
```

### Step 7: 邮件测试
```bash
# 等待第一次策略执行（每15分钟）
# 或手动触发一次交易

# 检查:
# ✅ 收到邮件通知
# ✅ 邮件内容完整
# ✅ 收件人正确
```

---

## 验证清单

### 基础功能
- [ ] Web界面可访问
- [ ] 网络连接正常
- [ ] 账户余额正确显示
- [ ] 持仓信息正确显示（如有持仓）
- [ ] 历史订单可查询
- [ ] 收益图表正常显示

### 交易功能
- [ ] 策略每15分钟执行一次
- [ ] 日志中可见策略执行记录
- [ ] MACD指标计算正确
- [ ] 交易指令发送成功
- [ ] 订单记录保存到数据库

### 通知功能
- [ ] 交易后收到邮件
- [ ] 邮件内容完整准确
- [ ] 收件人地址正确

### 数据持久化
- [ ] 数据库文件在 `data/` 目录
- [ ] 重启容器后数据不丢失
- [ ] 日志文件正常记录

---

## 常见问题处理

### 问题1: 容器启动失败

**症状**: `docker-compose up` 报错

**解决**:
```bash
# 查看详细错误
docker-compose logs

# 常见原因:
# 1. .env文件缺失或格式错误
# 2. 端口5000被占用
# 3. Docker资源不足

# 解决方法:
# 1. 检查.env文件
# 2. 修改docker-compose.yml中的端口映射
# 3. 清理Docker资源: docker system prune
```

### 问题2: OKX连接失败

**症状**: 日志显示 "OKX连接失败"

**解决**:
```bash
# 检查:
# 1. API密钥是否正确
# 2. 网络是否能访问OKX
# 3. API权限是否包含"交易"

# 测试API:
curl -X GET "https://www.okx.com/api/v5/account/balance" \
  -H "OK-ACCESS-KEY: your_api_key" \
  -H "OK-ACCESS-SIGN: your_signature" \
  -H "OK-ACCESS-TIMESTAMP: your_timestamp" \
  -H "OK-ACCESS-PASSPHRASE: your_passphrase"
```

### 问题3: 邮件发送失败

**症状**: 日志显示 "邮件发送失败"

**解决**:
```bash
# 检查:
# 1. SMTP配置是否正确
# 2. 是否使用应用专用密码（不是登录密码）
# 3. 邮箱是否开启SMTP服务

# Outlook设置:
# SMTP服务器: smtp-mail.outlook.com
# 端口: 587
# 加密: STARTTLS
# 密码: 应用专用密码
```

### 问题4: 策略不执行

**症状**: 日志中没有策略执行记录

**解决**:
```bash
# 检查:
# 1. 当前是否有持仓（策略要求必须有持仓）
# 2. 调度器是否正常启动
# 3. 时间是否正确

# 手动测试:
# 进入容器执行一次策略
docker exec -it okx-trading-system python -c "
from trading.strategy import TradingStrategy
strategy = TradingStrategy()
strategy.execute_strategy()
"
```

### 问题5: 数据库错误

**症状**: 日志显示数据库相关错误

**解决**:
```bash
# 检查:
# 1. data目录权限
# 2. 磁盘空间
# 3. 数据库文件是否损坏

# 修复:
# 1. 删除损坏的数据库文件
rm data/trading.db
# 2. 重启容器，会自动重建
docker-compose restart
```

---

## 性能优化

### 内存优化
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M    # 根据实际情况调整
      cpus: '0.5'
```

### 日志优化
```python
# config.py
LOG_LEVEL = 'WARNING'  # 生产环境使用WARNING级别
LOG_MAX_BYTES = 5242880  # 减小日志文件大小
```

### 数据库优化
```sql
-- 定期清理旧数据
DELETE FROM strategy_logs WHERE timestamp < datetime('now', '-30 days');
DELETE FROM balance_snapshots WHERE timestamp < datetime('now', '-90 days');
```

---

## 安全加固

### 1. API密钥保护
```bash
# 不要将.env文件提交到Git
# 确保.gitignore包含.env
chmod 600 .env  # Linux/Mac限制文件权限
```

### 2. 网络隔离
```yaml
# docker-compose.yml - 只暴露必要端口
ports:
  - "127.0.0.1:5000:5000"  # 只允许本地访问
```

### 3. 添加认证
```python
# app.py - 添加简单的HTTP认证
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == 'admin' and password == os.getenv('WEB_PASSWORD')

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

---

## 监控和维护

### 日常监控
```bash
# 查看系统状态
docker-compose ps

# 查看资源使用
docker stats okx-trading-system

# 查看最新日志
docker-compose logs --tail=50
```

### 定期维护
```bash
# 每周备份数据库
cp data/trading.db backups/trading.db.$(date +%Y%m%d)

# 每月清理日志
docker-compose logs --tail=1000 > logs/archive_$(date +%Y%m).txt

# 每季度更新镜像
docker-compose pull
docker-compose up -d --build
```

### 健康检查
```bash
# 检查系统健康状态
curl http://localhost:5000/api/status
curl http://localhost:5000/health

# 预期返回:
# {"status": "running", "trading_engine": true}
```

---

## 备份策略

### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp data/trading.db $BACKUP_DIR/trading_$TIMESTAMP.db

# 备份配置
cp .env $BACKUP_DIR/env_$TIMESTAMP

# 压缩备份
tar czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz $BACKUP_DIR/*_$TIMESTAMP*

# 删除7天前的备份
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: backup_$TIMESTAMP.tar.gz"
```

### 定时备份
```bash
# 添加到crontab（每天凌晨2点备份）
0 2 * * * /path/to/backup.sh
```

---

## 升级指南

### 更新代码
```bash
# 1. 拉取最新代码
git pull

# 2. 停止服务
docker-compose down

# 3. 重新构建
docker-compose build --no-cache

# 4. 启动服务
docker-compose up -d

# 5. 检查日志
docker-compose logs -f
```

### 更新依赖
```bash
# 1. 更新requirements.txt
pip install --upgrade -r requirements.txt

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d
```

---

## 紧急处理

### 止损操作
```bash
# 如果策略出现问题，立即停止

# 方法1: 停止容器
docker-compose stop

# 方法2: 进入容器手动平仓
docker exec -it okx-trading-system bash
python -c "
from trading.okx_client import OKXClient
client = OKXClient()
positions = client.get_positions()
for pos in positions:
    if pos['side'] == 'long':
        client.close_position('sell', pos['size'])
    else:
        client.close_position('buy', pos['size'])
print('已全部平仓')
"
```

### 恢复数据
```bash
# 从备份恢复数据库
cp backups/trading_20260519.db data/trading.db
docker-compose restart
```

---

## 联系支持

遇到问题时：
1. 查看日志: `docker-compose logs -f`
2. 查阅文档: `README.md`
3. 检查常见问题: 本文档"常见问题处理"部分

---

**最后更新**: 2026-05-19
