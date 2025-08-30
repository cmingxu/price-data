from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from loguru import logger

from models import get_db, create_tables
from crud import PriceDataCRUD, ScrapingLogCRUD, bulk_create_or_update
from scraper import XinfadiScraper

class DataManager:
    """数据管理器 - 负责数据抓取、去重和同步"""
    
    def __init__(self):
        self.scraper = XinfadiScraper()
        logger.info("数据管理器初始化完成")
    
    def ensure_database_setup(self):
        """确保数据库表已创建"""
        try:
            create_tables()
            logger.info("数据库表检查/创建完成")
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise
    
    def sync_data(self, 
                  limit: int = 20,
                  max_pages: Optional[int] = None,
                  days_back: Optional[int] = None,
                  immediate_save: bool = True,
                  **kwargs) -> Dict[str, Any]:
        """同步数据到数据库
        
        Args:
            limit: 每页记录数
            max_pages: 最大页数限制
            days_back: 只同步最近几天的数据
            immediate_save: 是否立即保存每页数据（默认True）
            **kwargs: 其他查询参数
            
        Returns:
            同步结果统计
        """
        
        start_time = datetime.now()
        logger.info(f"开始数据同步 (immediate_save={immediate_save})")
        
        db_gen = get_db()
        db = next(db_gen)
        
        # 统计变量
        total_records = 0
        total_new_count = 0
        total_updated_count = 0
        
        try:
            if immediate_save:
                # 定义保存回调函数
                def save_callback(page_records: List[Dict[str, Any]]) -> int:
                    nonlocal total_records, total_new_count, total_updated_count
                    
                    if not page_records:
                        return 0
                    
                    # 立即保存当前页数据
                    new_count, updated_count = bulk_create_or_update(db, page_records)
                    
                    # 更新统计
                    total_records += len(page_records)
                    total_new_count += new_count
                    total_updated_count += updated_count
                    
                    return new_count + updated_count
                
                # 使用立即保存模式抓取数据
                if days_back:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days_back)
                    
                    self.scraper.scrape_by_date_range(
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        limit=limit,
                        max_pages=max_pages,
                        save_callback=save_callback
                    )
                else:
                    # 抓取所有数据
                    self.scraper.scrape_all(
                        limit=limit,
                        max_pages=max_pages,
                        save_callback=save_callback,
                        **kwargs
                    )
                
                if total_records == 0:
                    logger.warning("未获取到任何数据")
                    return {
                        'status': 'warning',
                        'message': '未获取到任何数据',
                        'total_records': 0,
                        'new_records': 0,
                        'updated_records': 0,
                        'duration': (datetime.now() - start_time).total_seconds()
                    }
                
                new_count = total_new_count
                updated_count = total_updated_count
                records_count = total_records
                
            else:
                # 传统批量保存模式
                if days_back:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days_back)
                    
                    records = self.scraper.scrape_by_date_range(
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        limit=limit,
                        max_pages=max_pages
                    )
                else:
                    # 抓取所有数据
                    records = self.scraper.scrape_all(
                        limit=limit,
                        max_pages=max_pages,
                        **kwargs
                    )
                
                if not records:
                    logger.warning("未获取到任何数据")
                    return {
                        'status': 'warning',
                        'message': '未获取到任何数据',
                        'total_records': 0,
                        'new_records': 0,
                        'updated_records': 0,
                        'duration': (datetime.now() - start_time).total_seconds()
                    }
                
                # 批量创建或更新记录
                new_count, updated_count = bulk_create_or_update(db, records)
                records_count = len(records)
            
            # 记录抓取日志
            ScrapingLogCRUD.create_log(
                db=db,
                total_records=records_count,
                new_records=new_count,
                updated_records=updated_count,
                status='success'
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'message': '数据同步完成',
                'total_records': records_count,
                'new_records': new_count,
                'updated_records': updated_count,
                'duration': duration
            }
            
            logger.info(f"数据同步完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            
            # 记录错误日志
            try:
                ScrapingLogCRUD.create_log(
                    db=db,
                    total_records=0,
                    new_records=0,
                    updated_records=0,
                    status='error',
                    error_message=str(e)
                )
            except:
                pass
            
            return {
                'status': 'error',
                'message': f'数据同步失败: {str(e)}',
                'total_records': 0,
                'new_records': 0,
                'updated_records': 0,
                'duration': (datetime.now() - start_time).total_seconds()
            }
            
        finally:
            db.close()
    
    def sync_incremental(self, days: int = 1) -> Dict[str, Any]:
        """增量同步 - 只同步最近几天的数据
        
        Args:
            days: 同步最近几天的数据
            
        Returns:
            同步结果统计
        """
        
        logger.info(f"开始增量同步，同步最近 {days} 天的数据")
        
        return self.sync_data(
            limit=50,  # 增量同步使用较大的页面大小
            days_back=days
        )
    
    def sync_by_product(self, 
                       prod_name: str = "",
                       prod_catid: str = "",
                       limit: int = 20) -> Dict[str, Any]:
        """按产品同步数据
        
        Args:
            prod_name: 产品名称
            prod_catid: 产品分类ID
            limit: 每页记录数
            
        Returns:
            同步结果统计
        """
        
        logger.info(f"开始按产品同步数据: 产品名称='{prod_name}', 分类ID='{prod_catid}'")
        
        return self.sync_data(
            limit=limit,
            prod_name=prod_name,
            prod_catid=prod_catid
        )
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """检查数据新鲜度
        
        Returns:
            数据新鲜度信息
        """
        
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            stats = PriceDataCRUD.get_statistics(db)
            
            # 检查最新数据时间
            latest_update = stats.get('latest_update')
            if latest_update:
                latest_datetime = datetime.fromisoformat(latest_update.replace('Z', '+00:00'))
                hours_since_update = (datetime.now() - latest_datetime.replace(tzinfo=None)).total_seconds() / 3600
            else:
                hours_since_update = None
            
            # 获取最近的抓取日志
            recent_logs = ScrapingLogCRUD.get_recent_logs(db, limit=5)
            
            return {
                'total_records': stats['total_records'],
                'latest_update': latest_update,
                'hours_since_update': hours_since_update,
                'data_is_fresh': hours_since_update is None or hours_since_update < 24,
                'recent_sync_logs': [
                    {
                        'date': log.scrape_date.isoformat(),
                        'status': log.status,
                        'new_records': log.new_records,
                        'updated_records': log.updated_records,
                        'total_records': log.total_records
                    }
                    for log in recent_logs
                ]
            }
            
        finally:
            db.close()
    
    def get_duplicate_records(self) -> List[Dict[str, Any]]:
        """获取重复记录
        
        Returns:
            重复记录列表
        """
        
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # 查找具有相同产品名称、发布日期和价格的记录
            from sqlalchemy import func
            from models import PriceData
            
            duplicates_query = (
                db.query(
                    PriceData.prod_name,
                    PriceData.pub_date,
                    PriceData.avg_price,
                    func.count(PriceData.id).label('count')
                )
                .group_by(PriceData.prod_name, PriceData.pub_date, PriceData.avg_price)
                .having(func.count(PriceData.id) > 1)
            )
            
            duplicates = duplicates_query.all()
            
            result = []
            for dup in duplicates:
                # 获取具体的重复记录
                records = (
                    db.query(PriceData)
                    .filter(
                        PriceData.prod_name == dup.prod_name,
                        PriceData.pub_date == dup.pub_date,
                        PriceData.avg_price == dup.avg_price
                    )
                    .all()
                )
                
                result.append({
                    'prod_name': dup.prod_name,
                    'pub_date': dup.pub_date.isoformat() if dup.pub_date else None,
                    'avg_price': dup.avg_price,
                    'count': dup.count,
                    'record_ids': [r.id for r in records]
                })
            
            logger.info(f"发现 {len(result)} 组重复记录")
            return result
            
        finally:
            db.close()
    
    def clean_duplicates(self, keep_latest: bool = True) -> Dict[str, Any]:
        """清理重复记录
        
        Args:
            keep_latest: 是否保留最新的记录
            
        Returns:
            清理结果统计
        """
        
        logger.info("开始清理重复记录")
        
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            duplicates = self.get_duplicate_records()
            
            if not duplicates:
                logger.info("未发现重复记录")
                return {
                    'status': 'success',
                    'message': '未发现重复记录',
                    'deleted_count': 0
                }
            
            deleted_count = 0
            
            for dup_group in duplicates:
                record_ids = dup_group['record_ids']
                
                if keep_latest:
                    # 保留ID最大的记录（通常是最新的）
                    record_ids_to_delete = record_ids[:-1]
                else:
                    # 保留ID最小的记录（通常是最早的）
                    record_ids_to_delete = record_ids[1:]
                
                # 删除重复记录
                for record_id in record_ids_to_delete:
                    if PriceDataCRUD.delete(db, record_id):
                        deleted_count += 1
            
            result = {
                'status': 'success',
                'message': f'清理完成，删除了 {deleted_count} 条重复记录',
                'deleted_count': deleted_count,
                'duplicate_groups': len(duplicates)
            }
            
            logger.info(f"重复记录清理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"清理重复记录失败: {e}")
            return {
                'status': 'error',
                'message': f'清理失败: {str(e)}',
                'deleted_count': 0
            }
            
        finally:
            db.close()
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态
        
        Returns:
            同步状态信息
        """
        
        freshness = self.check_data_freshness()
        
        return {
            'database_status': 'connected',
            'total_records': freshness['total_records'],
            'latest_update': freshness['latest_update'],
            'data_is_fresh': freshness['data_is_fresh'],
            'hours_since_update': freshness['hours_since_update'],
            'recent_syncs': len(freshness['recent_sync_logs']),
            'last_sync_status': freshness['recent_sync_logs'][0]['status'] if freshness['recent_sync_logs'] else None
        }
    
    def close(self):
        """关闭资源"""
        self.scraper.close()
        logger.info("数据管理器资源已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
