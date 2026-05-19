"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
from utils.logger import logger


class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
        """
        计算MACD指标
        
        Args:
            prices: 价格序列
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            tuple: (macd_line, signal_line, histogram)
        """
        if len(prices) < slow_period + signal_period:
            logger.warning("价格数据不足，无法计算MACD")
            return None, None, None
        
        # 转换为pandas Series
        price_series = pd.Series(prices)
        
        # 计算EMA
        ema_fast = price_series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = price_series.ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线（MACD的EMA）
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return macd_line.values, signal_line.values, histogram.values
    
    @staticmethod
    def get_latest_macd(ohlcv_data):
        """
        从K线数据获取最新MACD值
        
        Args:
            ohlcv_data: K线数据 [[timestamp, open, high, low, close, volume], ...]
            
        Returns:
            dict: MACD相关信息
        """
        if not ohlcv_data or len(ohlcv_data) < 50:
            return None
        
        # 提取收盘价
        closes = [candle[4] for candle in ohlcv_data]
        
        # 计算MACD
        macd_line, signal_line, histogram = TechnicalIndicators.calculate_macd(closes)
        
        if macd_line is None:
            return None
        
        # 获取最新值
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        current_hist = histogram[-1]
        
        # 获取前一根K线的收盘价
        prev_close = closes[-2] if len(closes) >= 2 else closes[-1]
        current_close = closes[-1]
        
        return {
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_hist,
            'current_price': current_close,
            'prev_close': prev_close,
            'macd_direction': 'positive' if current_macd > 0 else 'negative'
        }
