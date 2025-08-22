import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./data/price_data.db"
    )
    
    # API配置
    XINFADI_API_URL = "http://www.xinfadi.com.cn/getPriceData.html"
    XINFADI_REFERER = "http://www.xinfadi.com.cn/priceDetail.html"
    
    # 速率限制配置
    RATE_LIMIT_CALLS = 10  # 每分钟最多10次请求
    RATE_LIMIT_PERIOD = 60  # 60秒
    
    # 请求配置
    REQUEST_TIMEOUT = 30
    REQUEST_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # 重试配置
    RETRY_MAX_ATTEMPTS = 5  # 最大重试次数
    RETRY_INTERVAL = 10  # 重试间隔（秒）
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "xinfadi_scraper.log"
    
    # FastAPI配置
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_TITLE = "新发地价格数据API"
    API_VERSION = "1.0.0"