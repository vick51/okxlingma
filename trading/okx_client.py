"""
OKX交易所API封装模块
使用ccxt库统一接口
"""
import ccxt
import time
from config import Config
from utils.logger import logger


class OKXClient:
    """OKX交易所客户端"""
    
    def __init__(self):
        """初始化OKX客户端"""
        # 调试：打印配置状态
        logger.info(f"API Key配置状态: {'已设置' if Config.OKX_API_KEY and Config.OKX_API_KEY != 'your_api_key_here' else '未设置'}")
        logger.info(f"Secret Key配置状态: {'已设置' if Config.OKX_SECRET_KEY and Config.OKX_SECRET_KEY != 'your_secret_key_here' else '未设置'}")
        logger.info(f"Passphrase配置状态: {'已设置' if Config.OKX_PASSPHRASE and Config.OKX_PASSPHRASE != 'your_passphrase_here' else '未设置'}")
        
        # 验证API密钥
        if not Config.OKX_API_KEY or Config.OKX_API_KEY == 'your_api_key_here':
            logger.warning("⚠️  OKX API密钥未配置，使用模拟模式")
            logger.warning("请在.env文件中配置真实的OKX API密钥")
            self.exchange = None
            self.symbol = Config.SYMBOL
            self.leverage = Config.LEVERAGE
            return
        
        if not Config.OKX_SECRET_KEY or Config.OKX_SECRET_KEY == 'your_secret_key_here':
            logger.error("❌ OKX Secret Key未配置")
            raise ValueError("请配置OKX_SECRET_KEY")
        
        if not Config.OKX_PASSPHRASE or Config.OKX_PASSPHRASE == 'your_passphrase_here':
            logger.error("❌ OKX Passphrase未配置")
            raise ValueError("请配置OKX_PASSPHRASE")
        
        try:
            self.exchange = ccxt.okx({
                'apiKey': str(Config.OKX_API_KEY),
                'secret': str(Config.OKX_SECRET_KEY),
                'password': str(Config.OKX_PASSPHRASE),
                'options': {
                    'defaultType': 'swap',  # 永续合约
                    'adjustForTimeDifference': True
                },
                'timeout': 30000,
                'enableRateLimit': True,
            })
            self.symbol = Config.SYMBOL
            self.leverage = Config.LEVERAGE
            
            # 测试连接
            self._test_connection()
        except Exception as e:
            logger.error(f"❌ OKX客户端初始化失败: {e}")
            raise
    
    def _test_connection(self):
        """测试交易所连接"""
        try:
            markets = self.exchange.load_markets()
            if self.symbol in markets:
                logger.info(f"OKX连接成功，交易对: {self.symbol}")
            else:
                raise ValueError(f"交易对 {self.symbol} 不存在")
        except Exception as e:
            logger.error(f"OKX连接失败: {e}")
            raise
    
    def set_leverage(self, leverage=None):
        """
        设置杠杆倍数
        
        Args:
            leverage: 杠杆倍数，默认使用配置值
        """
        lev = leverage or self.leverage
        try:
            self.exchange.set_leverage(lev, self.symbol)
            logger.info(f"杠杆已设置为: {lev}x")
            return True
        except Exception as e:
            logger.error(f"设置杠杆失败: {e}")
            return False
    
    def get_balance(self):
        """
        获取账户余额
        
        Returns:
            dict: 账户余额信息
        """
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {})
            
            return {
                'total': usdt_balance.get('total', 0),
                'free': usdt_balance.get('free', 0),
                'used': usdt_balance.get('used', 0)
            }
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            return None
    
    def get_positions(self):
        """
        获取当前持仓
        
        Returns:
            list: 持仓列表
        """
        try:
            positions = self.exchange.fetch_positions([self.symbol])
            active_positions = []
            
            for pos in positions:
                # 只返回有持仓的数据
                if pos['contracts'] and pos['contracts'] > 0:
                    side = 'long' if pos['side'] == 'long' else 'short'
                    active_positions.append({
                        'symbol': pos['symbol'],
                        'side': side,
                        'size': pos['contracts'],
                        'entry_price': pos['entryPrice'],
                        'current_price': pos['markPrice'],
                        'leverage': pos['leverage'],
                        'unrealized_pnl': pos['unrealizedPnl'],
                        'liquidation_price': pos['liquidationPrice'],
                        'margin': pos['initialMargin'],
                        'percentage': pos['percentage']
                    })
            
            return active_positions
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []
    
    def get_ohlcv(self, timeframe='15m', limit=100):
        """
        获取K线数据
        
        Args:
            timeframe: K线周期
            limit: 获取数量
            
        Returns:
            list: K线数据 [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            return []
    
    def get_ticker(self):
        """
        获取最新行情
        
        Returns:
            dict: 行情数据
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return {
                'symbol': ticker['symbol'],
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'high': ticker['high'],
                'low': ticker['low'],
                'volume': ticker['baseVolume']
            }
        except Exception as e:
            logger.error(f"获取行情失败: {e}")
            return None
    
    def create_market_order(self, side, amount, params=None):
        """
        创建市价单
        
        Args:
            side: 'buy'(做多) 或 'sell'(做空)
            amount: 数量
            params: 额外参数
            
        Returns:
            dict: 订单信息
        """
        try:
            order = self.exchange.create_market_order(self.symbol, side, amount, params=params)
            logger.info(f"订单创建成功: {side} {amount} {self.symbol}")
            return order
        except Exception as e:
            logger.error(f"创建订单失败: {e}")
            raise
    
    def close_position(self, side, amount=None):
        """
        平仓
        
        Args:
            side: 'sell'(平多) 或 'buy'(平空)
            amount: 平仓数量，None则全部平仓
            
        Returns:
            dict: 订单信息
        """
        try:
            # 获取当前持仓
            positions = self.get_positions()
            
            if not positions:
                logger.warning("没有持仓可平")
                return None
            
            # 找到对应方向的持仓
            target_pos = None
            for pos in positions:
                if (side == 'sell' and pos['side'] == 'long') or \
                   (side == 'buy' and pos['side'] == 'short'):
                    target_pos = pos
                    break
            
            if not target_pos:
                logger.warning(f"没有找到{side}方向的持仓")
                return None
            
            # 确定平仓数量
            close_amount = amount or target_pos['size']
            
            # OKX平仓需要特殊参数
            params = {
                'reduceOnly': True
            }
            
            order = self.create_market_order(side, close_amount, params=params)
            logger.info(f"平仓成功: {side} {close_amount}")
            return order
            
        except Exception as e:
            logger.error(f"平仓失败: {e}")
            raise
    
    def get_funding_rate(self):
        """
        获取资金费率
        
        Returns:
            float: 资金费率
        """
        try:
            funding = self.exchange.fetch_funding_rate(self.symbol)
            return funding['fundingRate']
        except Exception as e:
            logger.error(f"获取资金费率失败: {e}")
            return 0
    
    def get_recent_trades(self, limit=10):
        """
        获取最近的个人交易记录
        
        Args:
            limit: 数量限制
            
        Returns:
            list: 交易记录
        """
        try:
            trades = self.exchange.fetch_my_trades(self.symbol, limit=limit)
            return trades
        except Exception as e:
            logger.error(f"获取交易记录失败: {e}")
            return []
    
    def check_network_status(self):
        """
        检查网络连接状态
        
        Returns:
            dict: 网络状态信息
        """
        try:
            start_time = time.time()
            self.exchange.fetch_ticker(self.symbol)
            latency = int((time.time() - start_time) * 1000)
            
            return {
                'status': 'connected',
                'latency': latency,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'disconnected',
                'error': str(e),
                'timestamp': time.time()
            }
