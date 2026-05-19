# 快速开始指南

## 3分钟启动系统

### 步骤1: 配置API密钥（1分钟）

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件，填写OKX API信息
# Windows: notepad .env
# Linux/Mac: vim .env
```

需要填写的内容：
```env
OKX_API_KEY=你的API密钥
OKX_SECRET_KEY=你的密钥
OKX_PASSPHRASE=你的密码短语
```

**获取API密钥**: OKX官网 → 账户 → API → 创建API（勾选交易权限）

### 步骤2: 启动系统（1分钟）

**Windows用户**:
```bash
docker-compose up -d
```

**Linux/Mac用户**:
```bash
./start.sh
```

### 步骤3: 访问界面（1分钟）

浏览器打开: **http://localhost:5000**

查看：
- ✅ 网络状态是否正常
- ✅ 账户余额是否显示
- ✅ 持仓信息（如有）

---

## 常用命令

```bash
# 查看实时日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 备份数据库
cp data/trading.db data/trading.db.backup

# 查看容器状态
docker-compose ps
```

---

## 故障排查

### 问题1: 连接失败
- 检查 `.env` 文件中的API密钥是否正确
- 确认OKX API权限包含"交易"
- 查看日志: `docker-compose logs | grep "连接"`

### 问题2: 邮件发送失败
- Outlook需使用"应用专用密码"
- 检查SMTP配置
- 查看日志: `docker-compose logs | grep "邮件"`

### 问题3: 策略不执行
- 确认当前有持仓（策略要求必须有持仓）
- 检查日志是否有错误
- 确认网络连接正常

---

## 修改配置

### 调整交易参数

编辑 `.env` 文件：

```env
SYMBOL=ETH/USDT:USDT      # 修改交易对
ORDER_SIZE=0.01           # 修改每次购买数量
LEVERAGE=20               # 修改杠杆倍数
PRICE_GAP=500             # 修改价格间隔
```

修改后重启：
```bash
docker-compose restart
```

---

## 重要提醒

⚠️ **首次使用建议**:
1. 先在OKX模拟盘测试
2. 从小仓位开始
3. 密切监控策略表现
4. 定期备份数据库

📊 **Web界面功能**:
- 网络状态实时监控
- 当前持仓展示
- 历史交易查询（支持筛选）
- 收益趋势图表

📧 **邮件通知**:
每次交易后自动发送到 vick0515@outlook.com

---

## 获取帮助

- 完整文档: 查看 `README.md`
- 开发文档: 查看 `DEVELOPMENT_PLAN.md`
- 项目总结: 查看 `PROJECT_SUMMARY.md`

祝您交易顺利！🚀
