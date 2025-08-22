#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新发地价格数据抓取系统主程序

功能:
- 数据抓取和同步
- API服务启动
- 命令行工具
"""

import argparse
import asyncio
import sys
from datetime import datetime
from loguru import logger

from config import Config
from data_manager import DataManager
from models import create_tables

# 配置日志
logger.remove()  # 移除默认处理器
logger.add(
    sys.stderr,
    level=Config.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

def setup_database():
    """初始化数据库"""
    try:
        logger.info("正在初始化数据库...")
        create_tables()
        logger.info("数据库初始化完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

def sync_data(args):
    """同步数据命令"""
    logger.info("开始数据同步...")
    
    with DataManager() as dm:
        dm.ensure_database_setup()
        
        # 构建同步参数
        sync_params = {
            'limit': args.limit,
            'max_pages': args.max_pages,
        }
        
        if args.days:
            sync_params['days_back'] = args.days
        
        if args.product:
            sync_params['prod_name'] = args.product
        
        if args.category:
            sync_params['prod_catid'] = args.category
        
        # 设置保存模式
        sync_params['immediate_save'] = not args.batch_save  # 默认立即保存，除非指定批量保存
        
        # 执行同步
        if args.incremental:
            result = dm.sync_incremental(days=args.days or 1)
        else:
            result = dm.sync_data(**sync_params)
        
        # 输出结果
        logger.info(f"同步完成: {result}")
        print(f"\n同步结果:")
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        print(f"总记录数: {result['total_records']}")
        print(f"新增记录: {result['new_records']}")
        print(f"更新记录: {result['updated_records']}")
        print(f"耗时: {result['duration']:.2f} 秒")
        
        return result['status'] == 'success'

def check_status(args):
    """检查系统状态"""
    logger.info("检查系统状态...")
    
    with DataManager() as dm:
        try:
            # 检查数据库连接
            dm.ensure_database_setup()
            
            # 获取同步状态
            status = dm.get_sync_status()
            
            # 获取数据新鲜度
            freshness = dm.check_data_freshness()
            
            print(f"\n系统状态报告:")
            print(f"数据库状态: {status['database_status']}")
            print(f"总记录数: {status['total_records']}")
            print(f"最新更新: {status['latest_update'] or '无数据'}")
            print(f"数据新鲜度: {'新鲜' if status['data_is_fresh'] else '过期'}")
            
            if status['hours_since_update']:
                print(f"距离上次更新: {status['hours_since_update']:.1f} 小时")
            
            print(f"最近同步次数: {status['recent_syncs']}")
            print(f"最后同步状态: {status['last_sync_status'] or '无记录'}")
            
            # 显示重复记录信息
            if args.verbose:
                duplicates = dm.get_duplicate_records()
                print(f"重复记录组数: {len(duplicates)}")
                
                if duplicates:
                    print("\n重复记录详情:")
                    for i, dup in enumerate(duplicates[:5]):  # 只显示前5组
                        print(f"  {i+1}. {dup['prod_name']} - {dup['count']} 条重复")
                    
                    if len(duplicates) > 5:
                        print(f"  ... 还有 {len(duplicates) - 5} 组重复记录")
            
            return True
            
        except Exception as e:
            logger.error(f"状态检查失败: {e}")
            print(f"状态检查失败: {e}")
            return False

def clean_data(args):
    """清理数据命令"""
    logger.info("开始数据清理...")
    
    with DataManager() as dm:
        dm.ensure_database_setup()
        
        if args.duplicates:
            # 清理重复记录
            result = dm.clean_duplicates(keep_latest=not args.keep_oldest)
            
            print(f"\n清理结果:")
            print(f"状态: {result['status']}")
            print(f"消息: {result['message']}")
            print(f"删除记录数: {result['deleted_count']}")
            
            return result['status'] == 'success'
        
        return True

def start_api_server(args):
    """启动API服务器"""
    logger.info(f"启动API服务器 {Config.API_HOST}:{Config.API_PORT}")
    
    try:
        import uvicorn
        from api import app
        
        # 确保数据库已初始化
        if not setup_database():
            logger.error("数据库初始化失败，无法启动API服务器")
            return False
        
        # 启动服务器
        if args.reload:
            # 开发模式使用应用导入字符串
            uvicorn.run(
                "api:app",
                host=args.host or Config.API_HOST,
                port=args.port or Config.API_PORT,
                reload=True,
                log_level=args.log_level.lower()
            )
        else:
            # 生产模式直接使用app对象
            uvicorn.run(
                app,
                host=args.host or Config.API_HOST,
                port=args.port or Config.API_PORT,
                log_level=args.log_level.lower()
            )
        
        return True
        
    except Exception as e:
        logger.error(f"API服务器启动失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="新发地价格数据抓取系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s sync --limit 50 --max-pages 10     # 同步数据
  %(prog)s sync --incremental --days 3        # 增量同步最近3天
  %(prog)s sync --product 白菜                # 同步特定产品
  %(prog)s status --verbose                   # 检查详细状态
  %(prog)s clean --duplicates                 # 清理重复记录
  %(prog)s server --reload                    # 启动开发服务器
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 同步命令
    sync_parser = subparsers.add_parser('sync', help='同步数据')
    sync_parser.add_argument('--limit', type=int, default=20, help='每页记录数 (默认: 20)')
    sync_parser.add_argument('--max-pages', type=int, help='最大页数限制')
    sync_parser.add_argument('--days', type=int, help='同步最近几天的数据')
    sync_parser.add_argument('--product', help='产品名称')
    sync_parser.add_argument('--category', help='产品分类ID')
    sync_parser.add_argument('--incremental', action='store_true', help='增量同步模式')
    sync_parser.add_argument('--batch-save', action='store_true', help='使用批量保存模式（默认为立即保存）')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='检查系统状态')
    status_parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    
    # 清理命令
    clean_parser = subparsers.add_parser('clean', help='清理数据')
    clean_parser.add_argument('--duplicates', action='store_true', help='清理重复记录')
    clean_parser.add_argument('--keep-oldest', action='store_true', help='保留最旧的记录（默认保留最新）')
    
    # 服务器命令
    server_parser = subparsers.add_parser('server', help='启动API服务器')
    server_parser.add_argument('--host', help=f'服务器地址 (默认: {Config.API_HOST})')
    server_parser.add_argument('--port', type=int, help=f'服务器端口 (默认: {Config.API_PORT})')
    server_parser.add_argument('--reload', action='store_true', help='开启自动重载 (开发模式)')
    server_parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'], help='日志级别')
    
    # 初始化命令
    init_parser = subparsers.add_parser('init', help='初始化数据库')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 创建日志目录
    import os
    os.makedirs('logs', exist_ok=True)
    
    success = True
    
    try:
        if args.command == 'sync':
            success = sync_data(args)
        elif args.command == 'status':
            success = check_status(args)
        elif args.command == 'clean':
            success = clean_data(args)
        elif args.command == 'server':
            success = start_api_server(args)
        elif args.command == 'init':
            success = setup_database()
        else:
            logger.error(f"未知命令: {args.command}")
            success = False
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        success = False
    except Exception as e:
        logger.error(f"执行命令失败: {e}")
        success = False
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())