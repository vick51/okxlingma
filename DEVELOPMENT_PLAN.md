# 欧易量化交易系统 - 轻量级开发方案

## 1. 项目概述

### 1.1 核心目标
构建一个**低资源占用**的OKX永续合约量化交易系统，实现MACD策略自动交易、实时监控和数据展示。

### 1.2 设计原则
- **轻量化**: 最小化内存和CPU占用
- **高效性**: 减少不必要的计算和网络请求
- **稳定性**: 确保7×24小时稳定运行
- **简洁性**: 代码结构简单，易于维护

---

## 2. 技术选型（轻量级）

### 2.1 技术栈

| 组件 | 选择 | 理由 |
|------|------|------|
| 后端框架 | **Flask** | 轻量、简单、资源占用少 |
| 数据库 | **SQLite** | 零配置、单文件、无需独立服务 |
| 前端 | **原生HTML+JS** | 无框架依赖，加载快 |
| 图表库 | **Chart.js** | 轻量级可视化 |
| WebSocket | **Flask-SocketIO** | 实时数据推送 |
| 定时任务 | **APScheduler** | 轻量级任务调度 |
| 交易所API | **ccxt** | 统一接口，支持OKX |
| 邮件 | **smtplib** | Python内置，无需额外依赖 |
| 部署 | **Docker** | 容器化，便于部署 |

### 2.2 资源优化策略

```
✅ 使用SQLite替代PostgreSQL（节省~200MB内存）
✅ 前端不使用React/Vue框架（节省~50MB内存 + 减少构建复杂度）
✅ 只在必要时查询K线数据（避免频繁API调用）
✅ 使用内存缓存热点数据（减少数据库I/O）
✅ 异步处理邮件发送（不阻塞主线程）
✅ 日志轮转，限制文件大小（防止磁盘占满）
```

---

## 3. 系统架构

```
┌─────────────────────────────────────────────┐
│           Docker Container                   │
│                                              │
│  ┌──────────┐    ┌──────────────────┐       │
│  │  Flask   │◄──►│  Trading Engine  │       │
│  │  Server  │    │  (Strategy Core) │       │
│  └────┬─────┘    └────────┬─────────┘       │
│       │                   │                  │
│  ┌────┴─────┐    ┌────────┴─────────┐       │
│  │ SQLite   │    │  OKX API (ccxt)  │       │
│  │ Database │    └──────────────────┘       │
│  └──────────┘                               │
│                                              │
│  External:                                   │
│  - SMTP Server (Email)                       │
│  - Browser (Web UI)                          │
└─────────────────────────────────────────────┘
```

**预计资源占用**:
- 内存: ~150-200MB
- CPU: <5% (空闲时), <20% (交易时)
- 磁盘: ~50MB (含数据库)

---

## 4. 核心交易策略（保留原逻辑）

### 4.1 配置参数

```python
CONFIG = {
    "exchange": "okx",              # 交易平台
    "symbol": "BTC/USDT:USDT",      # 交易对（永续合约格式）
    "order_size": 0.002,            # 每次开仓数量
    "leverage": 50,                 # 杠杆倍数
    "price_gap": 1000,              # 价格间隔阈值(USDT)
    "timeframe": "15m",             # K线周期
    "email_recipient": "vick0515@outlook.com"
}
```

### 4.2 策略执行流程

```
每15分钟触发一次策略检查:
│
├─ 1. 获取最新15分钟K线数据
│     └─ 计算MACD指标
│
├─ 2. 检查当前持仓状态
│     └─ 如果无持仓 → 跳过本次执行
│
├─ 3. 判断MACD方向
│     │
│     ├─ MACD > 0 (多头市场)
│     │   ├─ IF 当前价格 < 上一根K线收盘价:
│     │   │   ├─ 计算当前空单收益(扣除手续费+资金费)
│     │   │   ├─ IF 收益 > 0:
│     │   │   │   └─ 【平掉所有空单】
│     │   │   └─ ELSE:
│     │   │       ├─ 【多单计数 + 1】
│     │   │       └─ 检查仓位平衡:
│     │   │           └─ IF 当日MACD始终>0 AND 空单数量 > 多单数量:
│     │   │               └─ 【补充多单使多单≥空单】
│     │   └─ 检查价格间隔:
│     │       └─ IF |当前价 - 上次开仓价| < 1000:
│     │           └─ 跳过开仓
│     │
│     └─ MACD < 0 (空头市场)
│         ├─ IF 当前价格 < 上一根K线收盘价:
│         │   ├─ 计算当前多单收益(扣除手续费+资金费)
│         │   ├─ IF 收益 > 0:
│         │   │   └─ 【平掉所有多单】
│         │   └─ ELSE:
│         │       ├─ 【空单计数 + 1】
│         │       └─ 检查仓位平衡:
│         │           └─ IF 当日MACD始终<0 AND 多单数量 > 空单数量:
│         │               └─ 【补充空单使空单≥多单】
│         └─ 检查价格间隔:
│             └─ IF |当前价 - 上次开仓价| < 1000:
│                 └─ 跳过开仓
│
└─ 4. 执行交易后发送邮件通知
```

### 4.3 关键逻辑说明

#### 4.3.1 持仓检查
```python
def should_trade():
    """如果没有持仓，则不交易"""
    positions = get_current_positions()
    return len(positions) > 0
```

#### 4.3.2 收益计算（扣除所有费用）
```python
def calculate_net_pnl(position):
    """计算净收益（扣除手续费和资金费）"""
    gross_pnl = position['unrealized_pnl']
    trading_fee = position['size'] * position['price'] * FEE_RATE * 2  # 开仓+平仓
    funding_fee = get_accumulated_funding_fee(position)
    
    net_pnl = gross_pnl - trading_fee - funding_fee
    return net_pnl
```

#### 4.3.3 价格间隔控制
```python
def check_price_gap(current_price, last_entry_price):
    """检查价格间隔是否满足1000 USDT"""
    return abs(current_price - last_entry_price) >= 1000
```

#### 4.3.4 仓位平衡逻辑
```python
def check_position_balance(macd_direction, long_count, short_count):
    """
    检查仓位平衡
    macd_direction: 'positive' 或 'negative'
    """
    if macd_direction == 'positive':
        # MACD > 0 时，空单不应超过多单
        if short_count > long_count:
            return 'need_more_long'
    elif macd_direction == 'negative':
        # MACD < 0 时，多单不应超过空单
        if long_count > short_count:
            return 'need_more_short'
    return 'balanced'
```

---

## 5. 数据库设计（SQLite）

### 5.1 表结构

```sql
-- 交易订单表
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,          -- 'buy'(多) 或 'sell'(空)
    action TEXT NOT NULL,        -- 'open' 或 'close'
    size REAL NOT NULL,
    price REAL NOT NULL,
    leverage INTEGER NOT NULL,
    pnl REAL DEFAULT 0,          -- 盈亏
    fee REAL DEFAULT 0,          -- 手续费
    funding_fee REAL DEFAULT 0,  -- 资金费
    open_time DATETIME,
    close_time DATETIME,
    status TEXT NOT NULL,        -- 'open', 'closed', 'cancelled'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 持仓快照表（记录每次开仓）
CREATE TABLE IF NOT EXISTS position_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,          -- 'long' 或 'short'
    size REAL NOT NULL,
    entry_price REAL NOT NULL,
    leverage INTEGER NOT NULL,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_closed INTEGER DEFAULT 0  -- 0=未平仓, 1=已平仓
);

-- 策略执行日志
CREATE TABLE IF NOT EXISTS strategy_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    macd_value REAL,
    signal_line REAL,
    histogram REAL,
    current_price REAL,
    prev_close_price REAL,
    action TEXT,                 -- 执行的动作
    long_count INTEGER,
    short_count INTEGER,
    message TEXT
);

-- 账户余额快照
CREATE TABLE IF NOT EXISTS balance_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_balance REAL,
    available_balance REAL,
    unrealized_pnl REAL,
    total_equity REAL
);

-- 创建索引优化查询
CREATE INDEX IF NOT EXISTS idx_orders_close_time ON orders(close_time);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_position_entries_is_closed ON position_entries(is_closed);
```

### 5.2 数据库优化

```python
# SQLite性能优化配置
PRAGMA journal_mode = WAL;      # 写前日志模式，提高并发性能
PRAGMA synchronous = NORMAL;    # 平衡安全性和性能
PRAGMA cache_size = -64000;     # 64MB缓存
PRAGMA temp_store = MEMORY;     # 临时表存内存
PRAGMA mmap_size = 268435456;   # 256MB内存映射
```

---

## 6. Web界面设计（轻量级）

### 6.1 页面结构

```
index.html (单页应用)
├── 网络状态面板
├── 当前持仓卡片
├── 历史交易表格（带筛选）
└── 收益统计图表
```

### 6.2 功能模块

#### 6.2.1 网络状态显示
```html
<div id="network-status">
    <span class="status-indicator"></span>
    <span id="status-text">连接中...</span>
    <span id="latency">延迟: --ms</span>
    <button onclick="checkNetwork()">检测</button>
</div>
```

**实时更新**: 每5秒通过WebSocket推送状态

#### 6.2.2 当前持仓展示
```html
<div id="positions">
    <table>
        <thead>
            <tr>
                <th>币种</th>
                <th>方向</th>
                <th>数量</th>
                <th>杠杆</th>
                <th>开仓价</th>
                <th>当前价</th>
                <th>盈亏</th>
                <th>收益率</th>
            </tr>
        </thead>
        <tbody id="positions-body">
            <!-- 动态填充 -->
        </tbody>
    </table>
</div>
```

**更新频率**: 每秒通过WebSocket推送最新价格和盈亏

#### 6.2.3 历史交易查询

**筛选器**:
```html
<div class="filters">
    <select id="filter-period">
        <option value="today">今天</option>
        <option value="week">本周</option>
        <option value="month">本月</option>
        <option value="year">今年</option>
        <option value="all">全部</option>
    </select>
    <input type="number" id="filter-limit" placeholder="最近N笔" min="1" max="1000">
    <button onclick="loadOrders()">查询</button>
</div>
```

**订单表格**:
```html
<table id="orders-table">
    <thead>
        <tr>
            <th>平仓时间</th>
            <th>币种</th>
            <th>方向</th>
            <th>数量</th>
            <th>开仓价</th>
            <th>平仓价</th>
            <th>杠杆</th>
            <th>手续费</th>
            <th>净利润</th>
            <th>收益率</th>
            <th>持仓时长</th>
        </tr>
    </thead>
    <tbody></tbody>
</table>
```

#### 6.2.4 收益统计图表
```javascript
// 使用Chart.js绘制收益曲线
const ctx = document.getElementById('pnl-chart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: dates,
        datasets: [{
            label: '累计收益',
            data: cumulativePnl,
            borderColor: '#4CAF50',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
```

### 6.3 API接口（Flask）

```python
# 系统状态
@app.route('/api/status')
def get_status():
    return jsonify({
        'network': check_network_status(),
        'strategy_running': strategy.is_running,
        'last_update': datetime.now().isoformat()
    })

# 当前持仓
@app.route('/api/positions')
def get_positions():
    positions = trading_engine.get_current_positions()
    return jsonify(positions)

# 历史订单（支持筛选）
@app.route('/api/orders')
def get_orders():
    period = request.args.get('period', 'all')  # today, week, month, year, all
    limit = request.args.get('limit', 100, type=int)
    orders = db.query_orders(period=period, limit=limit)
    return jsonify(orders)

# 账户余额
@app.route('/api/balance')
def get_balance():
    balance = trading_engine.get_account_balance()
    return jsonify(balance)

# WebSocket实时推送
@socketio.on('connect')
def handle_connect():
    emit('status', get_status())

@socketio.on('disconnect')
def handle_disconnect():
    pass
```

---

## 7. 邮件通知系统

### 7.1 邮件模板

```python
def send_trade_notification(trade_info):
    """发送交易通知邮件"""
    
    subject = f"[OKX量化] {trade_info['symbol']} {'做多' if trade_info['side']=='long' else '做空'} 交易通知"
    
    body = f"""
    交易详情:
    ━━━━━━━━━━━━━━━━━━━━━━━━
    
    📊 交易收入: {trade_info['pnl']:.2f} USDT
    
    💼 当前持仓:
       • 币种: {trade_info['symbol']}
       • 方向: {'做多' if trade_info['side']=='long' else '做空'}
       • 数量: {trade_info['size']}
       • 杠杆: {trade_info['leverage']}倍
       • 未实现盈亏: {trade_info['unrealized_pnl']:.2f} USDT
    
    💰 账户余额: {trade_info['balance']:.2f} USDT
    
    📈 累计收益率: {trade_info['total_return_rate']:.2f}%
    
    ⏰ 交易时间: {trade_info['timestamp']}
    
    ━━━━━━━━━━━━━━━━━━━━━━━━
    此邮件由OKX量化交易系统自动发送
    """
    
    send_email(
        to="vick0515@outlook.com",
        subject=subject,
        body=body
    )
```

### 7.2 SMTP配置

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp-mail.outlook.com',
    'smtp_port': 587,
    'sender': 'your_email@outlook.com',
    'password': 'your_app_password',  # 使用应用专用密码
    'recipient': 'vick0515@outlook.com'
}
```

---

## 8. 项目结构

```
okx-trading-system/
│
├── app.py                    # Flask主应用
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── Dockerfile                # Docker镜像
├── docker-compose.yml        # Docker编排（可选，单个容器即可）
│
├── trading/
│   ├── __init__.py
│   ├── engine.py             # 交易引擎核心
│   ├── strategy.py           # MACD策略逻辑
│   ├── okx_client.py         # OKX API封装
│   └── indicators.py         # 技术指标计算
│
├── database/
│   ├── __init__.py
│   ├── models.py             # 数据模型
│   └── db_manager.py         # 数据库操作
│
├── web/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # 样式文件
│   │   └── js/
│   │       ├── app.js        # 前端逻辑
│   │       └── chart.js      # 图表相关
│   └── templates/
│       └── index.html        # 主页面
│
├── utils/
│   ├── __init__.py
│   ├── email_sender.py       # 邮件发送
│   └── logger.py             # 日志管理
│
└── data/
    └── trading.db            # SQLite数据库文件
```

---

## 9. 核心代码示例

### 9.1 交易引擎主循环

```python
import ccxt
import pandas as pd
import talib
from apscheduler.schedulers.blocking import BlockingScheduler

class TradingEngine:
    def __init__(self, config):
        self.config = config
        self.exchange = ccxt.okx({
            'apiKey': config['api_key'],
            'secret': config['secret'],
            'password': config['passphrase'],
            'options': {'defaultType': 'swap'}  # 永续合约
        })
        self.db = DatabaseManager('data/trading.db')
        self.last_entry_price = None
        
    def run_strategy(self):
        """策略主函数 - 每15分钟执行"""
        try:
            # 1. 检查是否有持仓
            positions = self.get_positions()
            if not positions:
                logger.info("当前无持仓，跳过交易")
                return
            
            # 2. 获取K线数据
            ohlcv = self.exchange.fetch_ohlcv(
                self.config['symbol'], 
                timeframe='15m', 
                limit=100
            )
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # 3. 计算MACD
            macd, signal, hist = talib.MACD(
                df['close'].values, 
                fastperiod=12, 
                slowperiod=26, 
                signalperiod=9
            )
            
            current_macd = macd[-1]
            current_price = df['close'].iloc[-1]
            prev_close = df['close'].iloc[-2]
            
            # 4. 记录日志
            self.db.log_strategy(
                macd=current_macd,
                signal=signal[-1],
                histogram=hist[-1],
                price=current_price,
                prev_close=prev_close
            )
            
            # 5. 执行策略逻辑
            if current_macd > 0:
                self.handle_bull_market(current_price, prev_close, positions)
            elif current_macd < 0:
                self.handle_bear_market(current_price, prev_close, positions)
                
        except Exception as e:
            logger.error(f"策略执行错误: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_bull_market(self, current_price, prev_close, positions):
        """多头市场逻辑 (MACD > 0)"""
        short_positions = [p for p in positions if p['side'] == 'short']
        long_positions = [p for p in positions if p['side'] == 'long']
        
        if current_price < prev_close:
            # 检查空单收益
            for pos in short_positions:
                net_pnl = self.calculate_net_pnl(pos)
                if net_pnl > 0:
                    # 平空
                    self.close_position(pos)
                    logger.info(f"平空单，净收益: {net_pnl}")
                else:
                    # 开多
                    if self.check_price_gap(current_price):
                        self.open_long()
                        logger.info("开多单")
                        
                        # 检查仓位平衡
                        if self.need_balance_positions('long', long_positions, short_positions):
                            self.open_long()  # 补充多单
        else:
            logger.info("价格条件不满足，跳过")
    
    def handle_bear_market(self, current_price, prev_close, positions):
        """空头市场逻辑 (MACD < 0)"""
        long_positions = [p for p in positions if p['side'] == 'long']
        short_positions = [p for p in positions if p['side'] == 'short']
        
        if current_price < prev_close:
            # 检查多单收益
            for pos in long_positions:
                net_pnl = self.calculate_net_pnl(pos)
                if net_pnl > 0:
                    # 平多
                    self.close_position(pos)
                    logger.info(f"平多单，净收益: {net_pnl}")
                else:
                    # 开空
                    if self.check_price_gap(current_price):
                        self.open_short()
                        logger.info("开空单")
                        
                        # 检查仓位平衡
                        if self.need_balance_positions('short', long_positions, short_positions):
                            self.open_short()  # 补充空单
        else:
            logger.info("价格条件不满足，跳过")
    
    def check_price_gap(self, current_price):
        """检查价格间隔"""
        if self.last_entry_price is None:
            return True
        return abs(current_price - self.last_entry_price) >= self.config['price_gap']
    
    def calculate_net_pnl(self, position):
        """计算净收益（扣除手续费和资金费）"""
        gross_pnl = position['unrealizedPnl']
        notional = position['contracts'] * position['markPrice']
        trading_fee = notional * 0.0005 * 2  # 假设费率0.05%，开仓+平仓
        funding_fee = self.get_funding_fee(position)
        
        return gross_pnl - trading_fee - funding_fee
    
    def start_scheduler(self):
        """启动定时任务"""
        scheduler = BlockingScheduler()
        scheduler.add_job(
            self.run_strategy, 
            'cron', 
            minute='*/15',  # 每15分钟
            second='0'
        )
        logger.info("策略调度器已启动")
        scheduler.start()
```

### 9.2 Flask应用

```python
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

trading_engine = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'network': 'connected' if trading_engine else 'disconnected',
        'running': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/positions')
def get_positions():
    if trading_engine:
        return jsonify(trading_engine.get_positions())
    return jsonify([])

@app.route('/api/orders')
def get_orders():
    period = request.args.get('period', 'all')
    limit = request.args.get('limit', 100, type=int)
    orders = db.query_orders(period=period, limit=limit)
    return jsonify(orders)

def broadcast_updates():
    """后台线程：定期推送更新"""
    while True:
        try:
            positions = trading_engine.get_positions() if trading_engine else []
            balance = trading_engine.get_balance() if trading_engine else {}
            
            socketio.emit('positions_update', positions)
            socketio.emit('balance_update', balance)
            socketio.emit('status_update', {'network': 'connected'})
            
            time.sleep(1)  # 每秒更新
        except Exception as e:
            logger.error(f"推送更新失败: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # 启动交易引擎
    trading_engine = TradingEngine(CONFIG)
    threading.Thread(target=trading_engine.start_scheduler, daemon=True).start()
    
    # 启动更新推送线程
    threading.Thread(target=broadcast_updates, daemon=True).start()
    
    # 启动Web服务器
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
```

---

## 10. Docker部署

### 10.1 Dockerfile

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# 启动命令
CMD ["python", "app.py"]
```

### 10.2 requirements.txt

```txt
flask==3.0.0
flask-socketio==5.3.6
ccxt==4.2.0
pandas==2.1.4
numpy==1.26.2
TA-Lib==0.4.28
apscheduler==3.10.4
python-dotenv==1.0.0
```

### 10.3 docker-compose.yml（简化版）

```yaml
version: '3.8'

services:
  okx-trading:
    build: .
    container_name: okx-trading-system
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

### 10.4 .env 配置文件

```env
# OKX API配置
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase

# 交易配置
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

# Web配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

## 11. 部署步骤

```bash
# 1. 克隆项目
git clone <repository_url>
cd okx-trading-system

# 2. 配置环境变量
cp .env.example .env
vim .env  # 填写OKX API密钥等信息

# 3. 构建并启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问Web界面
# 浏览器打开: http://localhost:5000

# 6. 停止服务
docker-compose down
```

---

## 12. 监控与维护

### 12.1 日志管理

```python
# utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger('okx_trading')
    logger.setLevel(logging.INFO)
    
    # 文件处理器（轮转，最大10MB，保留5个备份）
    file_handler = RotatingFileHandler(
        'data/trading.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### 12.2 健康检查

```python
@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.test_connection()
        
        # 检查交易所连接
        exchange.load_markets()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'exchange': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

---

## 13. 风险控制

### 13.1 安全措施

```python
# 1. API密钥加密存储
from cryptography.fernet import Fernet

def encrypt_api_key(key):
    fernet = Fernet(os.getenv('ENCRYPTION_KEY'))
    return fernet.encrypt(key.encode()).decode()

# 2. 异常处理
try:
    execute_trade()
except ccxt.NetworkError:
    logger.error("网络错误，等待重试")
    time.sleep(30)
except ccxt.ExchangeError as e:
    logger.error(f"交易所错误: {e}")
    send_alert_email(f"交易异常: {e}")
except Exception as e:
    logger.critical(f"未知错误: {e}", exc_info=True)
    send_alert_email(f"系统异常: {e}")

# 3. 最大亏损限制
MAX_DAILY_LOSS = 1000  # USDT
if daily_loss > MAX_DAILY_LOSS:
    logger.warning("达到每日最大亏损限制，停止交易")
    stop_trading()
```

### 13.2 建议的风控参数

```python
RISK_CONFIG = {
    'max_leverage': 50,              # 最大杠杆
    'max_position_size': 0.01,       # 最大持仓数量
    'stop_loss_percent': 0.05,       # 止损比例 5%
    'max_daily_loss': 1000,          # 每日最大亏损 USDT
    'emergency_close_all': True,     # 紧急情况下全平仓
}
```

---

## 14. 测试计划

### 14.1 单元测试

```python
# tests/test_strategy.py
import unittest

class TestTradingStrategy(unittest.TestCase):
    
    def test_macd_calculation(self):
        """测试MACD计算"""
        prices = [100, 101, 102, ...]  # 测试数据
        macd = calculate_macd(prices)
        self.assertIsNotNone(macd)
    
    def test_price_gap_check(self):
        """测试价格间隔检查"""
        self.assertTrue(check_price_gap(50000, 49000))  # 差1000
        self.assertFalse(check_price_gap(50000, 49500)) # 差500
    
    def test_position_balance(self):
        """测试仓位平衡逻辑"""
        result = check_balance('positive', long=2, short=3)
        self.assertEqual(result, 'need_more_long')
```

### 14.2 模拟交易测试

```bash
# 使用OKX模拟盘进行测试
# 1. 在OKX申请模拟盘API密钥
# 2. 修改config.py使用模拟盘端点
# 3. 运行至少1周观察策略表现
# 4. 验证邮件通知是否正常
# 5. 检查数据库记录是否完整
```

---

## 15. 常见问题

### Q1: 如何调整策略参数？
编辑 `.env` 文件中的配置项，重启容器即可：
```bash
docker-compose restart
```

### Q2: 数据库文件在哪里？
数据库文件位于 `./data/trading.db`，已挂载到宿主机，不会因容器重建而丢失。

### Q3: 如何查看实时日志？
```bash
docker-compose logs -f --tail=100
```

### Q4: 邮件收不到怎么办？
1. 检查SMTP配置是否正确
2. Outlook邮箱需启用"应用专用密码"
3. 查看日志确认是否有发送错误

### Q5: 如何备份数据？
```bash
# 备份数据库
cp data/trading.db data/trading.db.backup.$(date +%Y%m%d)

# 或使用Docker命令
docker exec okx-trading-system tar czf /tmp/backup.tar.gz /app/data
docker cp okx-trading-system:/tmp/backup.tar.gz ./backup.tar.gz
```

---

## 16. 总结

本方案特点：

✅ **轻量级**: 单容器部署，内存占用<200MB  
✅ **简单可靠**: SQLite无需额外服务，降低故障点  
✅ **策略完整**: 完全保留您的MACD交易逻辑  
✅ **实时监控**: WebSocket推送，秒级更新  
✅ **易于部署**: Docker一键启动  
✅ **低成本**: 无需云服务器，树莓派即可运行  

**下一步**:
1. 填写`.env`配置文件
2. 运行`docker-compose up -d`
3. 访问 http://localhost:5000 监控交易

---

**文档版本**: v1.0  
**创建日期**: 2026-05-19  
**适用系统**: OKX永续合约量化交易
