#!/usr/bin/env python3
"""
演示重试功能的脚本
"""

from scraper import XinfadiScraper
from config import Config
from loguru import logger

def main():
    """演示重试功能"""
    
    logger.info("=== 重试功能演示 ===")
    logger.info(f"配置信息:")
    logger.info(f"  - 最大重试次数: {Config.RETRY_MAX_ATTEMPTS}")
    logger.info(f"  - 重试间隔: {Config.RETRY_INTERVAL} 秒")
    logger.info(f"  - 请求超时: {Config.REQUEST_TIMEOUT} 秒")
    logger.info("")
    
    # 创建抓取器实例
    with XinfadiScraper() as scraper:
        logger.info("🚀 开始测试正常请求...")
        
        # 测试正常请求（获取最新1条数据）
        result = scraper.scrape_page(limit=1, current=1)
        
        if result:
            records = result.get('list', [])
            total_count = result.get('count', 0)
            
            logger.info(f"✅ 请求成功!")
            logger.info(f"  - 总记录数: {total_count}")
            logger.info(f"  - 本页记录数: {len(records)}")
            
            if records:
                first_record = records[0]
                logger.info(f"  - 示例数据: {first_record.get('prod_name', 'N/A')} - {first_record.get('avg_price', 'N/A')}元")
        else:
            logger.error("❌ 请求失败")
    
    logger.info("")
    logger.info("=== 演示完成 ===")
    logger.info("")
    logger.info("重试机制说明:")
    logger.info("1. 当遇到网络连接错误、超时错误或HTTP错误时，会自动重试")
    logger.info("2. 每次重试前会等待10秒")
    logger.info("3. 最多重试5次，如果都失败则返回None")
    logger.info("4. JSON解析错误等非网络错误不会重试")
    logger.info("5. 重试过程中会有详细的日志输出")

if __name__ == '__main__':
    main()