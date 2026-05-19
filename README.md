# OKX量化交易系统

基于MACD指标的OKX永续合约自动量化交易系统，支持实时监控股、历史交易查询和邮件通知。

## 功能特性

- ✅ **自动化交易**: 基于15分钟MACD指标自动执行交易策略
- ✅ **双平台支持**: 支持OKX和Binance交易所（当前实现OKX）
- ✅ **永续合约**: 专注于永续合约交易
- ✅ **风险控制**: 价格间隔控制、仓位平衡机制
- ✅ **实时监控**: Web界面实时显示持仓、余额和网络状态
- ✅ **历史查询**: 支持按年/月/周/天筛选历史交易
- ✅ **邮件通知**: 每次交易后发送邮件通知
- ✅ **轻量级**: 单容器部署，内存占用<200MB
- ✅ **Docker部署**: 一键启动，简单易用

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 或使用 Python 3.9+

## 快速开始

### 方式一：Docker部署（推荐）

#### 1. 克隆项目

```bash
git clone <repository_url>
cd okx-trading-system
```

#### 2. 配置环境变量

复制示例配置文件并填写您的OKX API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OKX API配置（必填）
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here

# 交易配置（可选，有默认值）
SYMBOL=BTC/USDT:USDT
ORDER_SIZE=0.002
LEVERAGE=50
PRICE_GAP=1000

# 邮件配置
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
EMAIL_USER=your_email@outlook.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=vick0515@outlook.com
```

**获取OKX API密钥**:
1. 登录 [OKX官网](https://www.okx.com/)
2. 进入「账户」→「API」
3. 创建新API密钥，勾选「交易」权限
4. 记录 API Key、Secret Key 和 Passphrase

**Outlook邮箱应用密码**:
1. 访问 [Microsoft账户安全](https://account.live.com/password/reset)
2. 启用两步验证
3. 生成应用专用密码

#### 3. 启动服务

**Windows用户（推荐）**:
```bash
# 双击运行或在命令行执行
start.bat
```

**Linux/Mac用户（推荐）**:
```bash
chmod +x start.sh
./start.sh
```

**或使用Docker Compose命令（V2）**:
```bash
docker compose up -d
```

#### 4. 查看日志

```bash
docker compose logs -f
```

#### 5. 访问Web界面

浏览器打开: http://localhost:5000

#### 6. 停止服务

```bash
docker compose down
```

### 方式二：Python直接运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境变量

同上，创建并编辑 `.env` 文件。

#### 3. 运行程序

```bash
python app.py
```

#### 4. 访问Web界面

浏览器打开: http://localhost:5000

## 交易策略说明

### 核心逻辑

系统每15分钟检查一次市场状态，根据MACD指标执行交易：

#### 多头市场（MACD > 0）

当满足以下条件时：
- 当前MACD > 0
- 当前价格 < 上一根K线收盘价

执行逻辑：
1. 如果空单收益（扣除手续费和资金费）> 0 → **平掉所有空单**
2. 否则 → **开多单**
   - 检查价格间隔：距上次开仓价必须≥1000 USDT
   - 检查仓位平衡：如果空单数量 > 多单数量，补充多单

#### 空头市场（MACD < 0）

当满足以下条件时：
- 当前MACD < 0
- 当前价格 < 上一根K线收盘价

执行逻辑：
1. 如果多单收益（扣除手续费和资金费）> 0 → **平掉所有多单**
2. 否则 → **开空单**
   - 检查价格间隔：距上次开仓价必须≥1000 USDT
   - 检查仓位平衡：如果多单数量 > 空单数量，补充空单

### 重要规则

⚠️ **无持仓不交易**: 如果当前没有任何持仓，系统不会执行任何操作

⚠️ **价格间隔**: 每次新开仓时，当前价格与上次开仓价格差值必须≥1000 USDT

⚠️ **仓位平衡**: 
- MACD > 0 时，空单数量不应超过多单数量
- MACD < 0 时，多单数量不应超过空单数量

### 收益计算

```
净收益 = 未实现盈亏 - 交易手续费 - 资金费

交易手续费 = 名义价值 × 费率 × 2（开仓+平仓）
资金费 = 名义价值 × |资金费率|
```

## Web界面功能

### 1. 网络状态
- 实时显示与交易所的连接状态
- 显示API响应延迟
- 手动检测按钮

### 2. 账户概览
- 总余额
- 可用余额
- 未实现盈亏
- 累计收益

### 3. 当前持仓
实时更新显示：
- 币种
- 方向（做多/做空）
- 数量
- 杠杆倍数
- 开仓价
- 当前价
- 盈亏
- 收益率

### 4. 历史交易
支持筛选：
- 今天
- 本周
- 本月
- 今年
- 全部

显示字段：
- 平仓时间
- 币种
- 方向
- 数量
- 开仓价
- 平仓价
- 杠杆
- 手续费
- 净利润
- 收益率

### 5. 收益图表
可视化展示账户权益变化趋势

## 项目结构

```
okx-trading-system/
├── app.py                    # Flask主应用
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── Dockerfile                # Docker镜像
├── docker-compose.yml        # Docker编排
├── .env.example              # 环境变量示例
│
├── trading/
│   ├── __init__.py
│   ├── okx_client.py         # OKX API封装
│   ├── strategy.py           # 交易策略引擎
│   └── indicators.py         # 技术指标计算
│
├── database/
│   ├── __init__.py
│   └── db_manager.py         # SQLite数据库管理
│
├── utils/
│   ├── __init__.py
│   ├── logger.py             # 日志管理
│   └── email_sender.py       # 邮件发送
│
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # 样式文件
│   │   └── js/
│   │       └── app.js        # 前端逻辑
│   └── templates/
│       └── index.html        # 主页面
│
└── data/
    ├── trading.db            # SQLite数据库（自动生成）
    └── trading.log           # 日志文件（自动生成）
```

## 常见问题

### Q1: 如何修改交易参数？

编辑 `.env` 文件中的配置项，然后重启容器：

```bash
docker compose restart
```

### Q2: 数据库文件在哪里？

数据库文件位于 `./data/trading.db`，已挂载到宿主机，容器重建不会丢失数据。

### Q3: 如何查看日志？

```bash
# 实时日志
docker compose logs -f

# 最近100行
docker compose logs --tail=100
```

### Q4: 邮件收不到怎么办？

1. 检查SMTP配置是否正确
2. Outlook邮箱需启用"应用专用密码"，不能使用登录密码
3. 查看日志确认是否有发送错误：
   ```bash
   docker compose logs | grep "邮件"
   ```

### Q5: 如何备份数据？

```bash
# 备份数据库
cp data/trading.db data/trading.db.backup.$(date +%Y%m%d)

# 备份整个数据目录
tar czf backup_$(date +%Y%m%d).tar.gz data/
```

### Q6: 策略不执行怎么办？

检查以下几点：
1. 确认当前有持仓（策略要求必须有持仓才执行）
2. 检查日志是否有错误信息
3. 确认API密钥权限正确（需要交易权限）
4. 检查网络连接是否正常

### Q7: 如何调整策略执行频率？

编辑 `app.py` 中的调度器配置：

```python
scheduler.add_job(
    trading_engine.execute_strategy,
    'cron',
    minute='*/15',  # 修改这里的数字
    second='0'
)
```

## 风险提示

⚠️ **重要提醒**:

1. **杠杆风险**: 高杠杆交易存在爆仓风险，请谨慎设置杠杆倍数
2. **模拟测试**: 建议先在OKX模拟盘充分测试后再实盘运行
3. **资金管理**: 不要投入超过您能承受损失的资金
4. **策略局限**: 任何策略都有失效的可能，请持续监控表现
5. **技术风险**: 网络延迟、API限流等可能影响交易执行
6. **合规性**: 确保交易行为符合当地法律法规

## 技术支持

如有问题，请查看日志文件或提交Issue。

## 许可证

MIT License

---

**免责声明**: 本软件仅供学习和研究使用，使用本软件进行交易的风险由用户自行承担。作者不对任何损失负责。
