"""
Flask Web应用主文件
提供REST API和WebSocket实时推送
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from datetime import datetime

from config import Config
from database.db_manager import DatabaseManager
from trading.okx_client import OKXClient
from trading.strategy import TradingStrategy
from utils.logger import logger

# 初始化Flask应用
app = Flask(__name__, 
            static_folder='web/static',
            template_folder='web/templates')
app.config['SECRET_KEY'] = 'okx-trading-system-secret-key'
CORS(app)

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 全局变量
db = DatabaseManager()
trading_engine = None
okx_client = None


def init_trading_engine():
    """初始化交易引擎"""
    global trading_engine, okx_client
    
    try:
        okx_client = OKXClient()
        
        # 检查API密钥是否配置
        if okx_client.exchange is None:
            logger.warning("⚠️  API密钥未配置，系统将以只读模式运行")
            logger.warning("📝 请在.env文件中配置OKX API密钥以启用交易功能")
            trading_engine = None
        else:
            trading_engine = TradingStrategy()
            logger.info("✅ 交易引擎初始化成功")
    except Exception as e:
        logger.error(f"❌ 交易引擎初始化失败: {e}")
        logger.warning("⚠️  系统将以只读模式运行")
        trading_engine = None
        okx_client = None


def broadcast_updates():
    """后台线程：定期推送更新到前端"""
    while True:
        try:
            if okx_client:
                # 获取持仓
                positions = okx_client.get_positions()
                
                # 获取余额
                balance = okx_client.get_balance()
                
                # 获取网络状态
                network_status = okx_client.check_network_status()
                
                # 推送数据
                socketio.emit('positions_update', positions)
                socketio.emit('balance_update', balance)
                socketio.emit('network_status', network_status)
            
            time.sleep(2)  # 每2秒更新一次
            
        except Exception as e:
            logger.error(f"推送更新失败: {e}")
            time.sleep(5)


# ==================== 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status')
def get_system_status():
    """获取系统状态"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'trading_engine': trading_engine is not None
    })


@app.route('/api/network')
def get_network_status():
    """获取网络状态"""
    if okx_client:
        status = okx_client.check_network_status()
        return jsonify(status)
    return jsonify({'status': 'not_initialized'})


@app.route('/api/positions')
def get_positions():
    """获取当前持仓"""
    if okx_client:
        positions = okx_client.get_positions()
        return jsonify(positions)
    return jsonify([])


@app.route('/api/orders')
def get_orders():
    """获取历史订单"""
    period = request.args.get('period', 'all')
    limit = request.args.get('limit', 100, type=int)
    
    orders = db.get_orders(period=period, limit=limit)
    return jsonify(orders)


@app.route('/api/balance')
def get_balance():
    """获取账户余额"""
    if okx_client:
        balance = okx_client.get_balance()
        return jsonify(balance)
    return jsonify({})


@app.route('/api/statistics')
def get_statistics():
    """获取交易统计"""
    stats = db.get_statistics()
    return jsonify(stats)


@app.route('/api/strategy/logs')
def get_strategy_logs():
    """获取策略日志"""
    limit = request.args.get('limit', 50, type=int)
    logs = db.get_strategy_logs(limit=limit)
    return jsonify(logs)


@app.route('/api/balance/history')
def get_balance_history():
    """获取账户余额历史"""
    limit = request.args.get('limit', 100, type=int)
    history = db.get_balance_history(limit=limit)
    return jsonify(history)


# ==================== WebSocket事件 ====================

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info("客户端已连接")
    emit('status', {'message': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开"""
    logger.info("客户端已断开")


@socketio.on('request_update')
def handle_request_update():
    """处理客户端请求更新"""
    if okx_client:
        positions = okx_client.get_positions()
        balance = okx_client.get_balance()
        network = okx_client.check_network_status()
        
        emit('positions_update', positions)
        emit('balance_update', balance)
        emit('network_status', network)


# ==================== 主程序 ====================

if __name__ == '__main__':
    logger.info("启动OKX量化交易系统...")
    
    # 初始化交易引擎
    init_trading_engine()
    
    # 启动后台更新线程
    update_thread = threading.Thread(target=broadcast_updates, daemon=True)
    update_thread.start()
    
    # 如果配置了自动交易，启动策略调度器
    if trading_engine:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            trading_engine.execute_strategy,
            'cron',
            minute='*/15',  # 每15分钟执行
            second='0'
        )
        scheduler.start()
        logger.info("策略调度器已启动（每15分钟执行）")
    
    # 启动Web服务器
    logger.info(f"Web服务器启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    socketio.run(
        app,
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
        allow_unsafe_werkzeug=True
    )
