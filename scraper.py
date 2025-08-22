import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from ratelimit import limits, sleep_and_retry
from loguru import logger
from config import Config

class XinfadiScraper:
    """新发地价格数据抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.REQUEST_HEADERS)
        self.session.headers['Referer'] = Config.XINFADI_REFERER
        self.api_url = Config.XINFADI_API_URL
        
        # 设置请求超时
        self.timeout = Config.REQUEST_TIMEOUT
        
        logger.info("新发地数据抓取器初始化完成")
    
    @sleep_and_retry
    @limits(calls=Config.RATE_LIMIT_CALLS, period=Config.RATE_LIMIT_PERIOD)
    def _make_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送POST请求，带有速率限制和重试机制"""
        
        # Debug: 显示真实请求路径和参数
        logger.info(f"🌐 Real request path: {self.api_url}")
        logger.info(f"📋 Request parameters: {data}")
        
        for attempt in range(Config.RETRY_MAX_ATTEMPTS):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{Config.RETRY_MAX_ATTEMPTS}")
                
                response = self.session.post(
                    self.api_url,
                    data=data,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                
                # 检查响应内容类型
                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type:
                    logger.warning(f"响应内容类型不是JSON: {content_type}")
                
                result = response.json()
                logger.info(f"✅ Request successful, returned {len(result.get('list', []))} records")
                
                return result
                
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout, 
                    requests.exceptions.HTTPError) as e:
                # 网络相关错误，需要重试
                is_last_attempt = attempt == Config.RETRY_MAX_ATTEMPTS - 1
                
                if is_last_attempt:
                    logger.error(f"❌ Network error after {Config.RETRY_MAX_ATTEMPTS} attempts: {e}")
                    return None
                else:
                    logger.warning(f"⚠️  Network error on attempt {attempt + 1}: {e}")
                    logger.info(f"⏳ Retrying in {Config.RETRY_INTERVAL} seconds...")
                    time.sleep(Config.RETRY_INTERVAL)
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                return None
            except Exception as e:
                logger.error(f"未知错误: {e}")
                return None
        
        return None
    
    def scrape_page(self, 
                   limit: int = 20,
                   current: int = 1,
                   pub_date_start_time: str = "",
                   pub_date_end_time: str = "",
                   prod_pcatid: str = "",
                   prod_catid: str = "",
                   prod_name: str = "") -> Optional[Dict[str, Any]]:
        """抓取单页数据
        
        Args:
            limit: 每页记录数
            current: 页码
            pub_date_start_time: 开始日期
            pub_date_end_time: 结束日期
            prod_pcatid: 产品父分类ID
            prod_catid: 产品分类ID
            prod_name: 产品名称
            
        Returns:
            API响应数据或None
        """
        
        form_data = {
            'limit': str(limit),
            'current': str(current),
            'pubDateStartTime': pub_date_start_time,
            'pubDateEndTime': pub_date_end_time,
            'prodPcatid': prod_pcatid,
            'prodCatid': prod_catid,
            'prodName': prod_name
        }
        
        return self._make_request(form_data)
    
    def scrape_all_pages(self, 
                        limit: int = 20,
                        max_pages: Optional[int] = None,
                        save_callback: Optional[callable] = None,
                        **kwargs) -> List[Dict[str, Any]]:
        """抓取所有页面数据
        
        Args:
            limit: 每页记录数
            max_pages: 最大页数限制
            save_callback: 保存回调函数，如果提供则立即保存每页数据
            **kwargs: 其他查询参数
            
        Returns:
            所有数据记录列表（如果使用save_callback，返回空列表）
        """
        
        all_records = []
        current_page = 1
        total_count = None
        total_pages = 0
        total_saved = 0
        
        # Debug: 显示当前抓取计划
        plan_info = f"📋 Current scraping plan: limit={limit}, max_pages={max_pages or 'unlimited'}"
        if kwargs:
            plan_info += f", filters={kwargs}"
        if save_callback:
            plan_info += ", immediate_save=True"
        logger.info(plan_info)
        logger.info("🚀 Starting to scrape all pages data")
        
        while True:
            # Debug: 显示当前页面和剩余页面信息
            if total_pages > 0:
                pages_left = total_pages - current_page
                logger.info(f"📄 Current page: {current_page}/{total_pages} | Pages left: {pages_left}")
            else:
                logger.info(f"📄 Current page: {current_page} (total pages unknown)")
            
            # 抓取当前页
            result = self.scrape_page(limit=limit, current=current_page, **kwargs)
            
            if not result:
                logger.error(f"❌ Page {current_page} scraping failed")
                break
            
            # 获取总记录数（第一次请求时）
            if total_count is None:
                total_count = result.get('count', 0)
                total_pages = (total_count + limit - 1) // limit
                logger.info(f"📊 Total records: {total_count}, Total pages: {total_pages}")
                
                # 如果设置了最大页数限制
                if max_pages and total_pages > max_pages:
                    total_pages = max_pages
                    logger.info(f"⚠️  Limited max pages to: {max_pages}")
            
            # 获取当前页数据
            page_records = result.get('list', [])
            
            # 如果提供了保存回调函数，立即保存当前页数据
            if save_callback and page_records:
                try:
                    saved_count = save_callback(page_records)
                    total_saved += saved_count
                    logger.info(f"💾 Page {current_page} saved: {saved_count} records (total saved: {total_saved})")
                except Exception as e:
                    logger.error(f"❌ Failed to save page {current_page} data: {e}")
                    # 继续处理下一页，不中断整个抓取过程
            else:
                # 如果没有保存回调，则缓存到内存中
                all_records.extend(page_records)
            
            logger.info(f"✅ Page {current_page} completed: {len(page_records)} records retrieved")
            
            # 检查是否还有更多页面
            if len(page_records) < limit:
                logger.info("🏁 Reached the last page")
                break
            
            # 检查页数限制
            if max_pages and current_page >= max_pages:
                logger.info(f"🛑 Reached max pages limit: {max_pages}")
                break
            
            current_page += 1
            
            # 添加延迟，避免请求过快
            logger.info("⏳ Waiting 1 second before next request...")
            time.sleep(1)
        
        if save_callback:
            logger.info(f"🎉 Scraping completed! Total records saved: {total_saved}")
            return []  # 返回空列表，因为数据已经保存
        else:
            logger.info(f"🎉 Scraping completed! Total records retrieved: {len(all_records)}")
            return all_records
    
    def scrape_by_date_range(self, 
                           start_date: str, 
                           end_date: str,
                           limit: int = 20,
                           max_pages: Optional[int] = None,
                           save_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """按日期范围抓取数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 每页记录数
            max_pages: 最大页数限制
            save_callback: 保存回调函数，如果提供则立即保存每页数据
            
        Returns:
            指定日期范围内的所有数据记录（如果使用save_callback，返回空列表）
        """
        
        logger.info(f"📅 Scraping by date range: {start_date} to {end_date}")
        logger.info(f"🎯 Plan: Date range scraping with limit={limit}, max_pages={max_pages or 'unlimited'}")
        
        return self.scrape_all_pages(
            limit=limit,
            max_pages=max_pages,
            save_callback=save_callback,
            pub_date_start_time=start_date,
            pub_date_end_time=end_date
        )
    
    def scrape_by_product(self, 
                         prod_name: str = "",
                         prod_catid: str = "",
                         limit: int = 20,
                         max_pages: Optional[int] = None,
                         save_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """按产品抓取数据
        
        Args:
            prod_name: 产品名称
            prod_catid: 产品分类ID
            limit: 每页记录数
            max_pages: 最大页数限制
            save_callback: 保存回调函数，如果提供则立即保存每页数据
            
        Returns:
            指定产品的所有数据记录（如果使用save_callback，返回空列表）
        """
        
        logger.info(f"🛒 Scraping by product: name='{prod_name}', category_id='{prod_catid}'")
        logger.info(f"🎯 Plan: Product scraping with limit={limit}, max_pages={max_pages or 'unlimited'}")
        
        return self.scrape_all_pages(
            limit=limit,
            max_pages=max_pages,
            save_callback=save_callback,
            prod_name=prod_name,
            prod_catid=prod_catid
        )
    
    def scrape_latest(self, days: int = 7, limit: int = 20, save_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """抓取最近几天的数据
        
        Args:
            days: 最近天数
            limit: 每页记录数
            save_callback: 保存回调函数，如果提供则立即保存每页数据
            
        Returns:
            最近几天的所有数据记录（如果使用save_callback，返回空列表）
        """
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"⏰ Scraping latest {days} days data: {start_date_str} to {end_date_str}")
        logger.info(f"🎯 Plan: Latest data scraping with limit={limit}")
        
        return self.scrape_by_date_range(start_date_str, end_date_str, limit, save_callback=save_callback)
    
    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("抓取器会话已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
