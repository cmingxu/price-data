#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时爬虫调度器
每3小时执行一次数据抓取任务
"""

import logging
import sys
import time
from datetime import datetime
from data_manager import DataManager
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_scrape():
    """执行数据抓取任务"""
    start_time = datetime.now()
    logger.info(f"开始执行数据抓取任务 - {start_time}")
    
    try:
        # 初始化数据管理器
        with DataManager() as dm:
            dm.ensure_database_setup()
            logger.info("数据管理器初始化成功")
            
            # 执行同步（使用立即保存模式，抓取最近7天数据）
            result = dm.sync_data(
                days_back=2,
                limit=20,
                immediate_save=True
            )
            
            if result['status'] == 'success':
                logger.info(f"数据同步成功: 总记录数={result['total_records']}, 新增={result['new_records']}, 更新={result['updated_records']}, 耗时={result['duration']:.2f}秒")
            elif result['status'] == 'warning':
                logger.warning(f"数据同步完成但有警告: {result['message']}")
            else:
                logger.error(f"数据同步失败: {result['message']}")
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"数据抓取过程中发生错误: {str(e)}", exc_info=True)
        sys.exit(1)
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"每日数据抓取任务完成 - {end_time}，耗时: {duration}")

def main():
    """主循环 - 每3小时执行一次抓取任务"""
    logger.info("启动定时爬虫调度器 - 每3小时执行一次")
    
    # 3小时 = 3 * 60 * 60 = 10800秒
    INTERVAL_SECONDS = 3 * 60 * 60
    
    while True:
        try:
            # 执行抓取任务
            run_scrape()
            
            # 等待3小时
            logger.info(f"任务完成，等待{INTERVAL_SECONDS}秒（3小时）后执行下一次抓取...")
            time.sleep(INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止调度器...")
            break
        except Exception as e:
            logger.error(f"调度器运行出错: {e}")
            logger.info(f"等待{INTERVAL_SECONDS}秒后重试...")
            time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
