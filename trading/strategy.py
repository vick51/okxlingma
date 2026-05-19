"""
核心交易策略引擎
实现MACD策略逻辑
"""
import time
from datetime import datetime
from config import Config
from trading.okx_client import OKXClient
from trading.indicators import TechnicalIndicators
from database.db_manager import DatabaseManager
from utils.email_sender import EmailSender
from utils.logger import logger


class TradingStrategy:
    """MACD交易策略引擎"""
    
    def __init__(self):
        """初始化策略引擎"""
        self.client = OKXClient()
        self.db = DatabaseManager()
        self.email_sender = EmailSender()
        
        # 记录上次开仓价格
        self.last_entry_price = None
        
        # 加载上次开仓价格
        self._load_last_entry_price()
        
        logger.info("交易策略引擎初始化完成")
    
    def _load_last_entry_price(self):
        """从数据库加载上次开仓价格"""
        try:
            positions = self.db.get_open_positions()
            if positions:
                # 取最新的持仓价格
                self.last_entry_price = positions[0]['entry_price']
                logger.info(f"加载上次开仓价格: {self.last_entry_price}")
        except Exception as e:
            logger.error(f"加载开仓价格失败: {e}")
    
    def execute_strategy(self):
        """
        执行策略主逻辑
        每15分钟调用一次
        """
        try:
            logger.info("=" * 50)
            logger.info(f"开始执行策略 - {datetime.now()}")
            
            # 1. 检查是否有持仓
            positions = self.client.get_positions()
            if not positions:
                logger.info("当前无持仓，跳过交易")
                return
            
            logger.info(f"当前持仓数量: {len(positions)}")
            
            # 2. 获取K线数据
            ohlcv = self.client.get_ohlcv(timeframe=Config.TIMEFRAME, limit=100)
            if not ohlcv:
                logger.error("获取K线数据失败")
                return
            
            # 3. 计算MACD
            macd_info = TechnicalIndicators.get_latest_macd(ohlcv)
            if not macd_info:
                logger.error("计算MACD失败")
                return
            
            logger.info(f"MACD: {macd_info['macd']:.4f}, "
                       f"Signal: {macd_info['signal']:.4f}, "
                       f"Histogram: {macd_info['histogram']:.4f}")
            logger.info(f"当前价格: {macd_info['current_price']}, "
                       f"上一根收盘: {macd_info['prev_close']}")
            
            # 4. 记录策略日志
            position_counts = self.db.get_position_counts()
            self.db.log_strategy(
                macd_value=macd_info['macd'],
                signal_line=macd_info['signal'],
                histogram=macd_info['histogram'],
                current_price=macd_info['current_price'],
                prev_close_price=macd_info['prev_close'],
                long_count=position_counts['long_count'],
                short_count=position_counts['short_count']
            )
            
            # 5. 根据MACD方向执行策略
            if macd_info['macd'] > 0:
                self._handle_bull_market(macd_info, positions)
            elif macd_info['macd'] < 0:
                self._handle_bear_market(macd_info, positions)
            else:
                logger.info("MACD = 0，观望")
            
            # 6. 保存账户余额快照
            balance = self.client.get_balance()
            if balance:
                unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
                self.db.save_balance_snapshot(
                    total_balance=balance['total'],
                    available_balance=balance['free'],
                    unrealized_pnl=unrealized_pnl,
                    total_equity=balance['total'] + unrealized_pnl
                )
            
            logger.info("策略执行完成")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"策略执行异常: {e}", exc_info=True)
    
    def _handle_bull_market(self, macd_info, positions):
        """
        多头市场逻辑 (MACD > 0)
        
        当15分钟 macd > 0, 当前价格<上一个k线收盘价, 收益>0，则平空
        否则多+1次，且当日macd > 0, 空单数量不超过多单，如果超过了补多单
        """
        logger.info("进入多头市场逻辑 (MACD > 0)")
        
        # 分离多空持仓
        long_positions = [p for p in positions if p['side'] == 'long']
        short_positions = [p for p in positions if p['side'] == 'short']
        
        current_price = macd_info['current_price']
        prev_close = macd_info['prev_close']
        
        # 检查价格条件: 当前价格 < 上一根K线收盘价
        if current_price < prev_close:
            logger.info(f"价格条件满足: {current_price} < {prev_close}")
            
            # 检查空单收益
            for pos in short_positions:
                net_pnl = self._calculate_net_pnl(pos)
                logger.info(f"空单净收益: {net_pnl:.2f} USDT")
                
                if net_pnl > 0:
                    # 平空
                    logger.info("空单收益>0，执行平空")
                    self._close_short_position(pos)
                else:
                    # 开多
                    logger.info("空单收益<=0，考虑开多")
                    if self._check_price_gap(current_price):
                        self._open_long_position()
                        
                        # 检查仓位平衡
                        position_counts = self.db.get_position_counts()
                        if position_counts['short_count'] > position_counts['long_count']:
                            logger.info("空单数量>多单数量，补充多单")
                            self._open_long_position()
                    else:
                        logger.info(f"价格间隔不足{Config.PRICE_GAP} USDT，跳过开仓")
        else:
            logger.info(f"价格条件不满足: {current_price} >= {prev_close}")
    
    def _handle_bear_market(self, macd_info, positions):
        """
        空头市场逻辑 (MACD < 0)
        
        当15分钟 macd < 0, 当前价格<上一个k线收盘价, 收益>0，则平多
        否则空+1次，且当日macd < 0, 多单数量不超过空单，如果超过了补空单
        """
        logger.info("进入空头市场逻辑 (MACD < 0)")
        
        # 分离多空持仓
        long_positions = [p for p in positions if p['side'] == 'long']
        short_positions = [p for p in positions if p['side'] == 'short']
        
        current_price = macd_info['current_price']
        prev_close = macd_info['prev_close']
        
        # 检查价格条件: 当前价格 < 上一根K线收盘价
        if current_price < prev_close:
            logger.info(f"价格条件满足: {current_price} < {prev_close}")
            
            # 检查多单收益
            for pos in long_positions:
                net_pnl = self._calculate_net_pnl(pos)
                logger.info(f"多单净收益: {net_pnl:.2f} USDT")
                
                if net_pnl > 0:
                    # 平多
                    logger.info("多单收益>0，执行平多")
                    self._close_long_position(pos)
                else:
                    # 开空
                    logger.info("多单收益<=0，考虑开空")
                    if self._check_price_gap(current_price):
                        self._open_short_position()
                        
                        # 检查仓位平衡
                        position_counts = self.db.get_position_counts()
                        if position_counts['long_count'] > position_counts['short_count']:
                            logger.info("多单数量>空单数量，补充空单")
                            self._open_short_position()
                    else:
                        logger.info(f"价格间隔不足{Config.PRICE_GAP} USDT，跳过开仓")
        else:
            logger.info(f"价格条件不满足: {current_price} >= {prev_close}")
    
    def _calculate_net_pnl(self, position):
        """
        计算净收益（扣除手续费和资金费）
        
        Args:
            position: 持仓信息
            
        Returns:
            float: 净收益
        """
        gross_pnl = position['unrealized_pnl']
        
        # 计算交易手续费（开仓+平仓）
        notional = position['size'] * position['current_price']
        trading_fee = notional * Config.TRADING_FEE_RATE * 2
        
        # 估算资金费（简化计算）
        funding_rate = self.client.get_funding_rate()
        funding_fee = notional * abs(funding_rate)
        
        net_pnl = gross_pnl - trading_fee - funding_fee
        return net_pnl
    
    def _check_price_gap(self, current_price):
        """
        检查价格间隔是否满足要求
        
        Args:
            current_price: 当前价格
            
        Returns:
            bool: 是否满足价格间隔
        """
        if self.last_entry_price is None:
            logger.info("首次开仓，无需检查价格间隔")
            return True
        
        gap = abs(current_price - self.last_entry_price)
        if gap >= Config.PRICE_GAP:
            logger.info(f"价格间隔满足: {gap:.2f} >= {Config.PRICE_GAP}")
            return True
        else:
            logger.info(f"价格间隔不足: {gap:.2f} < {Config.PRICE_GAP}")
            return False
    
    def _open_long_position(self):
        """开多单"""
        try:
            logger.info(f"开多单: {Config.ORDER_SIZE} {Config.SYMBOL}")
            
            # 设置杠杆
            self.client.set_leverage(Config.LEVERAGE)
            
            # 创建市价买单（做多）
            order = self.client.create_market_order('buy', Config.ORDER_SIZE)
            
            # 获取成交价格
            filled_price = order.get('average') or order.get('price', 0)
            
            # 记录到数据库
            self.db.add_order(
                order_id=order['id'],
                symbol=Config.SYMBOL,
                side='long',
                action='open',
                size=Config.ORDER_SIZE,
                price=filled_price,
                leverage=Config.LEVERAGE,
                status='open',
                open_time=datetime.now().isoformat()
            )
            
            # 记录持仓入场
            self.db.add_position_entry(
                symbol=Config.SYMBOL,
                side='long',
                size=Config.ORDER_SIZE,
                entry_price=filled_price,
                leverage=Config.LEVERAGE
            )
            
            # 更新上次开仓价格
            self.last_entry_price = filled_price
            
            # 发送邮件通知
            self._send_trade_notification('open', 'long', order, filled_price)
            
            logger.info("开多单成功")
            
        except Exception as e:
            logger.error(f"开多单失败: {e}")
    
    def _open_short_position(self):
        """开空单"""
        try:
            logger.info(f"开空单: {Config.ORDER_SIZE} {Config.SYMBOL}")
            
            # 设置杠杆
            self.client.set_leverage(Config.LEVERAGE)
            
            # 创建市价卖单（做空）
            order = self.client.create_market_order('sell', Config.ORDER_SIZE)
            
            # 获取成交价格
            filled_price = order.get('average') or order.get('price', 0)
            
            # 记录到数据库
            self.db.add_order(
                order_id=order['id'],
                symbol=Config.SYMBOL,
                side='short',
                action='open',
                size=Config.ORDER_SIZE,
                price=filled_price,
                leverage=Config.LEVERAGE,
                status='open',
                open_time=datetime.now().isoformat()
            )
            
            # 记录持仓入场
            self.db.add_position_entry(
                symbol=Config.SYMBOL,
                side='short',
                size=Config.ORDER_SIZE,
                entry_price=filled_price,
                leverage=Config.LEVERAGE
            )
            
            # 更新上次开仓价格
            self.last_entry_price = filled_price
            
            # 发送邮件通知
            self._send_trade_notification('open', 'short', order, filled_price)
            
            logger.info("开空单成功")
            
        except Exception as e:
            logger.error(f"开空单失败: {e}")
    
    def _close_long_position(self, position):
        """平多单"""
        try:
            logger.info(f"平多单: {position['size']} {Config.SYMBOL}")
            
            # 平仓（卖出）
            order = self.client.close_position('sell', position['size'])
            
            if order:
                # 获取成交价格和盈亏
                filled_price = order.get('average') or order.get('price', 0)
                pnl = position['unrealized_pnl']
                
                # 更新订单状态
                self.db.update_order_status(
                    order_id=order['id'],
                    status='closed',
                    pnl=pnl,
                    close_time=datetime.now().isoformat()
                )
                
                # 标记持仓为已平仓
                positions = self.db.get_open_positions()
                for pos in positions:
                    if pos['side'] == 'long':
                        self.db.close_position_entry(pos['id'])
                
                # 发送邮件通知
                self._send_trade_notification('close', 'long', order, filled_price, pnl)
                
                logger.info("平多单成功")
            
        except Exception as e:
            logger.error(f"平多单失败: {e}")
    
    def _close_short_position(self, position):
        """平空单"""
        try:
            logger.info(f"平空单: {position['size']} {Config.SYMBOL}")
            
            # 平仓（买入）
            order = self.client.close_position('buy', position['size'])
            
            if order:
                # 获取成交价格和盈亏
                filled_price = order.get('average') or order.get('price', 0)
                pnl = position['unrealized_pnl']
                
                # 更新订单状态
                self.db.update_order_status(
                    order_id=order['id'],
                    status='closed',
                    pnl=pnl,
                    close_time=datetime.now().isoformat()
                )
                
                # 标记持仓为已平仓
                positions = self.db.get_open_positions()
                for pos in positions:
                    if pos['side'] == 'short':
                        self.db.close_position_entry(pos['id'])
                
                # 发送邮件通知
                self._send_trade_notification('close', 'short', order, filled_price, pnl)
                
                logger.info("平空单成功")
            
        except Exception as e:
            logger.error(f"平空单失败: {e}")
    
    def _send_trade_notification(self, action, side, order, price, pnl=None):
        """
        发送交易通知邮件
        
        Args:
            action: 'open' 或 'close'
            side: 'long' 或 'short'
            order: 订单信息
            price: 成交价格
            pnl: 盈亏（平仓时）
        """
        try:
            # 获取当前持仓
            positions = self.client.get_positions()
            
            # 获取账户余额
            balance = self.client.get_balance()
            
            # 计算统计数据
            stats = self.db.get_statistics()
            
            # 构建邮件内容
            action_text = "开仓" if action == 'open' else "平仓"
            side_text = "做多" if side == 'long' else "做空"
            
            # 持仓详情
            position_details = []
            for pos in positions:
                position_details.append(
                    f"  • 币种: {pos['symbol']}\n"
                    f"  • 方向: {'做多' if pos['side'] == 'long' else '做空'}\n"
                    f"  • 数量: {pos['size']}\n"
                    f"  • 杠杆: {pos['leverage']}倍\n"
                    f"  • 未实现盈亏: {pos['unrealized_pnl']:.2f} USDT"
                )
            
            position_text = "\n".join(position_details) if position_details else "  无持仓"
            
            # 计算收益率
            total_equity = balance['total'] if balance else 0
            total_pnl = stats.get('total_pnl', 0) or 0
            return_rate = (total_pnl / total_equity * 100) if total_equity > 0 else 0
            
            pnl_text = f"{pnl:.2f} USDT" if pnl is not None else "N/A"
            balance_text = f"{balance['total']:.2f} USDT" if balance else "N/A"
            
            email_body = f"""
交易详情:
━━━━━━━━━━━━━━━━━━━━━━━━

📊 交易收入: {pnl_text}

💼 当前持仓:
{position_text}

💰 账户余额: {balance_text}

📈 累计收益率: {return_rate:.2f}%

⏰ 交易时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━
此邮件由OKX量化交易系统自动发送
            """
            
            subject = f"[OKX量化] {Config.SYMBOL} {side_text}{action_text} 通知"
            
            self.email_sender.send_email(subject, email_body)
            logger.info("邮件通知已发送")
            
        except Exception as e:
            logger.error(f"发送邮件通知失败: {e}")
