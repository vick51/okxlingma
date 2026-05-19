# API密钥配置指南

## 问题说明

系统启动时出现错误：
```
OKX连接失败: unsupported operand type(s) for +: 'NoneType' and 'str'
```

**原因**: `.env` 文件中的API密钥未配置或使用默认占位符。

---

## 解决步骤

### 1. 获取OKX API密钥

1. 登录 [OKX官网](https://www.okx.com/)
2. 进入「账户」→ 「API」
3. 点击「创建API密钥」
4. 设置权限：
   - ✅ 读取（必须）
   - ✅ 交易（必须）
   - ❌ 提现（不要勾选）
5. 设置IP白名单（推荐）
6. 记录以下信息：
   - API Key
   - Secret Key
   - Passphrase（密码短语）

### 2. 配置.env文件

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
vim .env
```

填写您的API密钥：
```env
# OKX API配置（必填）
OKX_API_KEY=你的实际API密钥
OKX_SECRET_KEY=你的实际Secret密钥
OKX_PASSPHRASE=你的实际Passphrase

# 交易配置
SYMBOL=BTC/USDT:USDT
ORDER_SIZE=0.002
LEVERAGE=50
PRICE_GAP=1000
```

⚠️ **重要**:
- 不要用引号包裹密钥
- 不要有空格
- 保持密钥原样复制

### 3. 重启系统

```bash
# 停止
sudo docker compose down

# 重新启动
sudo docker compose up -d

# 查看日志
sudo docker compose logs -f
```

---

## 验证配置

### 检查日志

```bash
sudo docker compose logs | grep "OKX"
```

**成功标志**:
```
✅ OKX连接成功，交易对: BTC/USDT:USDT
✅ 交易引擎初始化成功
```

**失败标志**:
```
❌ OKX API密钥未配置
⚠️ 系统将以只读模式运行
```

### 测试API连接

```bash
# 进入容器
sudo docker exec -it okx-trading-system bash

# 测试Python导入
python -c "
from config import Config
print('API Key:', Config.OKX_API_KEY[:10] + '...' if Config.OKX_API_KEY else 'Not Set')
"
```

---

## 常见问题

### Q1: 如何确认API密钥是否正确？

**方法1**: 查看日志
```bash
sudo docker compose logs | grep -i "api"
```

**方法2**: 使用curl测试
```bash
curl -X GET "https://www.okx.com/api/v5/account/balance" \
  -H "OK-ACCESS-KEY: 你的API密钥" \
  -H "OK-ACCESS-SIGN: 签名" \
  -H "OK-ACCESS-TIMESTAMP: 时间戳" \
  -H "OK-ACCESS-PASSPHRASE: 你的Passphrase"
```

### Q2: Passphrase是什么？

Passphrase是创建API密钥时设置的密码短语，不是您的登录密码。

### Q3: API密钥安全吗？

**安全措施**:
1. ✅ .env文件已在.gitignore中，不会被提交到Git
2. ✅ Docker挂载为只读卷
3. ⚠️ 不要分享.env文件
4. ⚠️ 定期更换API密钥
5. ✅ 设置IP白名单

### Q4: 可以使用模拟盘吗？

可以！OKX提供模拟盘API：

```env
# 使用模拟盘需要在代码中修改
# trading/okx_client.py 中添加:
'options': {
    'defaultType': 'swap',
    'sandboxMode': True  # 启用模拟盘
}
```

### Q5: 没有API密钥能使用系统吗？

可以，但只能：
- ✅ 查看Web界面
- ✅ 查看历史数据
- ❌ 无法获取实时持仓
- ❌ 无法执行交易

---

## 安全建议

### 1. 权限最小化
- 只勾选「读取」和「交易」
- 不要勾选「提现」

### 2. IP白名单
在OKX API设置中添加服务器IP：
```bash
# 查看服务器公网IP
curl ifconfig.me
```

### 3. 定期更换
建议每3个月更换一次API密钥

### 4. 监控异常
定期检查：
- OKX账户活动日志
- API调用记录
- 异常交易行为

---

## 快速配置模板

复制以下内容到`.env`，替换为您的实际密钥：

```env
# OKX API配置
OKX_API_KEY=替换为你的API_Key
OKX_SECRET_KEY=替换为你的Secret_Key  
OKX_PASSPHRASE=替换为你的Passphrase

# 交易配置
SYMBOL=BTC/USDT:USDT
ORDER_SIZE=0.002
LEVERAGE=50
PRICE_GAP=1000

# 邮件配置（可选）
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
EMAIL_USER=your_email@outlook.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=vick0515@outlook.com

# Web配置
WEB_PORT=5000
FLASK_HOST=0.0.0.0
FLASK_DEBUG=false
```

---

**提示**: 配置完成后，运行 `./restart.sh` 重启系统即可生效！
