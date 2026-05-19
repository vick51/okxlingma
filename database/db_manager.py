"""
数据库管理模块 - SQLite
"""
import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import Config
from utils.logger import logger


class DatabaseManager:
    """SQLite数据库管理器"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 优化SQLite性能
            cursor.execute('PRAGMA journal_mode = WAL')
            cursor.execute('PRAGMA synchronous = NORMAL')
            cursor.execute('PRAGMA cache_size = -64000')  # 64MB
            cursor.execute('PRAGMA temp_store = MEMORY')
            
            # 创建交易订单表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    action TEXT NOT NULL,
                    size REAL NOT NULL,
                    price REAL NOT NULL,
                    leverage INTEGER NOT NULL,
                    pnl REAL DEFAULT 0,
                    fee REAL DEFAULT 0,
                    funding_fee REAL DEFAULT 0,
                    open_time DATETIME,
                    close_time DATETIME,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建持仓入场记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS position_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    size REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    leverage INTEGER NOT NULL,
                    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_closed INTEGER DEFAULT 0
                )
            ''')
            
            # 创建策略执行日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    macd_value REAL,
                    signal_line REAL,
                    histogram REAL,
                    current_price REAL,
                    prev_close_price REAL,
                    action TEXT,
                    long_count INTEGER,
                    short_count INTEGER,
                    message TEXT
                )
            ''')
            
            # 创建账户余额快照表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_balance REAL,
                    available_balance REAL,
                    unrealized_pnl REAL,
                    total_equity REAL
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_close_time ON orders(close_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_position_entries_is_closed ON position_entries(is_closed)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_strategy_logs_timestamp ON strategy_logs(timestamp)')
            
            logger.info("数据库初始化完成")
    
    # ==================== 订单相关操作 ====================
    
    def add_order(self, order_id, symbol, side, action, size, price, leverage, 
                  pnl=0, fee=0, funding_fee=0, open_time=None, close_time=None, status='open'):
        """添加订单记录"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO orders (order_id, symbol, side, action, size, price, leverage, 
                                   pnl, fee, funding_fee, open_time, close_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, symbol, side, action, size, price, leverage,
                  pnl, fee, funding_fee, open_time, close_time, status))
        logger.debug(f"订单记录已保存: {order_id}")
    
    def update_order_status(self, order_id, status, pnl=None, fee=None, funding_fee=None, close_time=None):
        """更新订单状态"""
        with self.get_connection() as conn:
            updates = ['status = ?']
            params = [status]
            
            if pnl is not None:
                updates.append('pnl = ?')
                params.append(pnl)
            if fee is not None:
                updates.append('fee = ?')
                params.append(fee)
            if funding_fee is not None:
                updates.append('funding_fee = ?')
                params.append(funding_fee)
            if close_time is not None:
                updates.append('close_time = ?')
                params.append(close_time)
            
            params.append(order_id)
            query = f"UPDATE orders SET {', '.join(updates)} WHERE order_id = ?"
            conn.execute(query, params)
    
    def get_orders(self, period='all', limit=100):
        """
        查询历史订单
        
        Args:
            period: 时间周期 ('today', 'week', 'month', 'year', 'all')
            limit: 返回数量限制
            
        Returns:
            list: 订单列表
        """
        with self.get_connection() as conn:
            query = "SELECT * FROM orders WHERE status = 'closed'"
            params = []
            
            now = datetime.now()
            if period == 'today':
                query += " AND close_time >= ?"
                params.append(now.replace(hour=0, minute=0, second=0).isoformat())
            elif period == 'week':
                query += " AND close_time >= ?"
                params.append((now - timedelta(days=7)).isoformat())
            elif period == 'month':
                query += " AND close_time >= ?"
                params.append((now - timedelta(days=30)).isoformat())
            elif period == 'year':
                query += " AND close_time >= ?"
                params.append((now - timedelta(days=365)).isoformat())
            
            query += " ORDER BY close_time DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_order_by_id(self, order_id):
        """根据ID查询订单"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== 持仓相关操作 ====================
    
    def add_position_entry(self, symbol, side, size, entry_price, leverage):
        """添加持仓入场记录"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO position_entries (symbol, side, size, entry_price, leverage)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, side, size, entry_price, leverage))
    
    def close_position_entry(self, entry_id):
        """标记持仓为已平仓"""
        with self.get_connection() as conn:
            conn.execute('UPDATE position_entries SET is_closed = 1 WHERE id = ?', (entry_id,))
    
    def get_open_positions(self):
        """获取未平仓的持仓记录"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM position_entries WHERE is_closed = 0 ORDER BY entry_time DESC'
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_position_counts(self):
        """获取当日多空单数量统计"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT 
                    SUM(CASE WHEN side = 'long' THEN 1 ELSE 0 END) as long_count,
                    SUM(CASE WHEN side = 'short' THEN 1 ELSE 0 END) as short_count
                FROM position_entries 
                WHERE entry_time >= ? AND is_closed = 0
            ''', (today_start,))
            
            row = cursor.fetchone()
            return {
                'long_count': row['long_count'] or 0,
                'short_count': row['short_count'] or 0
            }
    
    # ==================== 策略日志相关操作 ====================
    
    def log_strategy(self, macd_value, signal_line, histogram, current_price, 
                     prev_close_price, action=None, long_count=0, short_count=0, message=None):
        """记录策略执行日志"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO strategy_logs (macd_value, signal_line, histogram, current_price, 
                                          prev_close_price, action, long_count, short_count, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (macd_value, signal_line, histogram, current_price, 
                  prev_close_price, action, long_count, short_count, message))
    
    def get_strategy_logs(self, limit=100):
        """获取策略日志"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM strategy_logs ORDER BY timestamp DESC LIMIT ?', (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 账户余额相关操作 ====================
    
    def save_balance_snapshot(self, total_balance, available_balance, unrealized_pnl=0, total_equity=0):
        """保存账户余额快照"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO balance_snapshots (total_balance, available_balance, unrealized_pnl, total_equity)
                VALUES (?, ?, ?, ?)
            ''', (total_balance, available_balance, unrealized_pnl, total_equity))
    
    def get_latest_balance(self):
        """获取最新的账户余额"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM balance_snapshots ORDER BY timestamp DESC LIMIT 1'
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_balance_history(self, limit=100):
        """获取账户余额历史"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM balance_snapshots ORDER BY timestamp DESC LIMIT ?', (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 统计分析 ====================
    
    def get_statistics(self):
        """获取交易统计数据"""
        with self.get_connection() as conn:
            # 总盈亏
            cursor = conn.execute("SELECT SUM(pnl) as total_pnl, COUNT(*) as total_trades FROM orders WHERE status = 'closed'")
            stats = dict(cursor.fetchone())
            
            # 今日盈亏
            today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
            cursor = conn.execute(
                "SELECT SUM(pnl) as today_pnl FROM orders WHERE status = 'closed' AND close_time >= ?",
                (today_start,)
            )
            today_stats = dict(cursor.fetchone())
            stats.update(today_stats)
            
            # 胜率
            cursor = conn.execute('''
                SELECT 
                    COUNT(CASE WHEN pnl > 0 THEN 1 END) as win_count,
                    COUNT(CASE WHEN pnl <= 0 THEN 1 END) as loss_count
                FROM orders WHERE status = 'closed'
            ''')
            win_stats = dict(cursor.fetchone())
            
            total = win_stats['win_count'] + win_stats['loss_count']
            if total > 0:
                stats['win_rate'] = win_stats['win_count'] / total * 100
            else:
                stats['win_rate'] = 0
            
            stats.update(win_stats)
            return stats
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                conn.execute('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
