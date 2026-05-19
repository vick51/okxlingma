"""
系统配置文件
从环境变量加载配置，提供默认值
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Config:
    """系统配置类"""
    
    # OKX交易所配置
    EXCHANGE = 'okx'
    OKX_API_KEY = os.getenv('OKX_API_KEY', '')
    OKX_SECRET_KEY = os.getenv('OKX_SECRET_KEY', '')
    OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE', '')
    
    # 交易参数
    SYMBOL = os.getenv('SYMBOL', 'BTC/USDT:USDT')
    ORDER_SIZE = float(os.getenv('ORDER_SIZE', '0.002'))
    LEVERAGE = int(os.getenv('LEVERAGE', '50'))
    PRICE_GAP = float(os.getenv('PRICE_GAP', '1000'))
    TIMEFRAME = '15m'  # K线周期
    
    # 手续费率（OKX Maker/Taker费率，根据实际等级调整）
    TRADING_FEE_RATE = 0.0005  # 0.05%
    
    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'trading.db')
    
    # 邮件配置
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', 'vick0515@outlook.com')
    
    # Web配置
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # 风控配置
    MAX_DAILY_LOSS = 1000  # 每日最大亏损 USDT
    STOP_LOSS_PERCENT = 0.05  # 止损比例 5%
    
    @classmethod
    def validate(cls):
        """验证必要配置是否存在"""
        required = ['OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"缺少必要的配置项: {', '.join(missing)}")
        
        return True
