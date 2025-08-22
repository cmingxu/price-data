from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from models import PriceData, ScrapingLog
from loguru import logger

class PriceDataCRUD:
    """价格数据CRUD操作类"""
    
    @staticmethod
    def create(db: Session, price_data: Dict[str, Any]) -> PriceData:
        """创建价格数据记录"""
        try:
            # 转换价格字段为浮点数
            if 'lowPrice' in price_data and price_data['lowPrice']:
                price_data['low_price'] = float(price_data['lowPrice'])
            if 'highPrice' in price_data and price_data['highPrice']:
                price_data['high_price'] = float(price_data['highPrice'])
            if 'avgPrice' in price_data and price_data['avgPrice']:
                price_data['avg_price'] = float(price_data['avgPrice'])
            
            # 转换日期字段
            if 'pubDate' in price_data and price_data['pubDate']:
                if isinstance(price_data['pubDate'], str):
                    price_data['pub_date'] = datetime.strptime(
                        price_data['pubDate'], '%Y-%m-%d %H:%M:%S'
                    )
                else:
                    price_data['pub_date'] = price_data['pubDate']
            
            # 映射字段名
            db_data = {
                'id': price_data.get('id'),
                'prod_name': price_data.get('prodName'),
                'prod_catid': price_data.get('prodCatid'),
                'prod_cat': price_data.get('prodCat'),
                'prod_pcatid': price_data.get('prodPcatid'),
                'prod_pcat': price_data.get('prodPcat'),
                'low_price': price_data.get('low_price'),
                'high_price': price_data.get('high_price'),
                'avg_price': price_data.get('avg_price'),
                'place': price_data.get('place'),
                'spec_info': price_data.get('specInfo'),
                'unit_info': price_data.get('unitInfo'),
                'pub_date': price_data.get('pub_date'),
                'status': price_data.get('status'),
                'user_id_create': price_data.get('userIdCreate'),
                'user_id_modified': price_data.get('userIdModified'),
                'user_create': price_data.get('userCreate'),
                'user_modified': price_data.get('userModified'),
                'gmt_create': price_data.get('gmtCreate'),
                'gmt_modified': price_data.get('gmtModified')
            }
            
            # 检查是否存在重复记录（基于所有业务字段）
            prod_name = price_data.get('prodName')
            pub_date = price_data.get('pubDate')
            
            if prod_name and pub_date:
                existing_record = PriceDataCRUD.exists_by_unique_key(db, price_data)
                if existing_record:
                    logger.info(f"记录已存在，跳过创建: 产品={prod_name}, 日期={pub_date}")
                    return existing_record
            
            db_obj = PriceData(**db_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"创建价格数据记录: ID={db_obj.id}, 产品={db_obj.prod_name}")
            return db_obj
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建价格数据记录失败: {e}")
            raise
    
    @staticmethod
    def get_unique_products(db: Session, search: Optional[str] = None, limit: int = 50) -> List[str]:
        """获取唯一产品名称列表"""
        try:
            query = db.query(PriceData.prod_name).distinct()
            
            if search:
                query = query.filter(PriceData.prod_name.like(f"%{search}%"))
            
            products = query.limit(limit).all()
            return [product[0] for product in products if product[0]]
            
        except Exception as e:
            logger.error(f"获取产品列表失败: {e}")
            raise
    
    @staticmethod
    def get_categories(db: Session) -> List[Dict[str, Any]]:
        """获取分类列表"""
        try:
            categories = (db.query(PriceData.prod_catid, PriceData.prod_cat, PriceData.prod_pcatid, PriceData.prod_pcat)
                         .distinct()
                         .filter(PriceData.prod_cat.isnot(None))
                         .all())
            
            result = []
            for cat in categories:
                result.append({
                    "catid": cat[0],
                    "cat_name": cat[1],
                    "parent_catid": cat[2],
                    "parent_cat_name": cat[3]
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取分类列表失败: {e}")
            raise
    
    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[PriceData]:
        """根据ID获取价格数据"""
        return db.query(PriceData).filter(PriceData.id == record_id).first()
    
    @staticmethod
    def get_by_ids(db: Session, record_ids: List[int]) -> List[PriceData]:
        """根据ID列表批量获取价格数据"""
        return db.query(PriceData).filter(PriceData.id.in_(record_ids)).all()
    
    @staticmethod
    def exists(db: Session, record_id: int) -> bool:
        """检查记录是否存在"""
        return db.query(PriceData).filter(PriceData.id == record_id).first() is not None
    
    @staticmethod
    def exists_batch(db: Session, record_ids: List[int]) -> List[int]:
        """批量检查记录是否存在，返回已存在的ID列表"""
        existing_records = db.query(PriceData.id).filter(PriceData.id.in_(record_ids)).all()
        return [record.id for record in existing_records]
    
    @staticmethod
    def exists_by_unique_key(db: Session, record_data: Dict[str, Any]) -> Optional[PriceData]:
        """根据所有业务字段检查记录是否存在"""
        # 提取并规范化字段
        prod_name = record_data.get('prodName')
        prod_catid = record_data.get('prodCatid')
        prod_cat = record_data.get('prodCat')
        prod_pcatid = record_data.get('prodPcatid')
        prod_pcat = record_data.get('prodPcat')
        low_price = record_data.get('lowPrice')
        high_price = record_data.get('highPrice')
        avg_price = record_data.get('avgPrice')
        place = record_data.get('place') or ''
        spec_info = record_data.get('specInfo') or ''
        unit_info = record_data.get('unitInfo')
        pub_date = record_data.get('pubDate')
        status = record_data.get('status')
        
        # 转换日期格式
        if isinstance(pub_date, str):
            pub_date = datetime.strptime(pub_date, '%Y-%m-%d %H:%M:%S')
        
        return db.query(PriceData).filter(
            and_(
                PriceData.prod_name == prod_name,
                PriceData.prod_catid == prod_catid,
                PriceData.prod_cat == prod_cat,
                PriceData.prod_pcatid == prod_pcatid,
                PriceData.prod_pcat == prod_pcat,
                PriceData.low_price == low_price,
                PriceData.high_price == high_price,
                PriceData.avg_price == avg_price,
                PriceData.place == place,
                PriceData.spec_info == spec_info,
                PriceData.unit_info == unit_info,
                PriceData.pub_date == pub_date,
                PriceData.status == status
            )
        ).first()
    
    @staticmethod
    def exists_batch_by_unique_key(db: Session, records: List[Dict[str, Any]]) -> Dict[str, PriceData]:
        """批量检查记录是否存在，基于所有业务字段
        
        Returns:
            Dict[unique_key, PriceData]: 已存在记录的映射，key为所有业务字段的组合
        """
        if not records:
            return {}
        
        # 构建查询条件
        conditions = []
        key_mapping = {}
        
        for record in records:
            # 提取所有业务字段
            prod_name = record.get('prodName')
            prod_catid = record.get('prodCatid')
            prod_cat = record.get('prodCat')
            prod_pcatid = record.get('prodPcatid')
            prod_pcat = record.get('prodPcat')
            low_price = record.get('lowPrice')
            high_price = record.get('highPrice')
            avg_price = record.get('avgPrice')
            place = record.get('place') or ''
            spec_info = record.get('specInfo') or ''
            unit_info = record.get('unitInfo')
            pub_date = record.get('pubDate')
            status = record.get('status')
            
            if prod_name and pub_date:  # 最基本的必需字段
                # 转换日期格式
                if isinstance(pub_date, str):
                    pub_date_obj = datetime.strptime(pub_date, '%Y-%m-%d %H:%M:%S')
                    date_str = pub_date
                else:
                    pub_date_obj = pub_date
                    date_str = pub_date_obj.strftime('%Y-%m-%d %H:%M:%S')
                
                # 构建包含所有业务字段的唯一键
                unique_key = f"{prod_name}|{prod_catid}|{prod_cat}|{prod_pcatid}|{prod_pcat}|{low_price}|{high_price}|{avg_price}|{place}|{spec_info}|{unit_info}|{date_str}|{status}"
                key_mapping[unique_key] = record
                
                conditions.append(
                    and_(
                        PriceData.prod_name == prod_name,
                        PriceData.prod_catid == prod_catid,
                        PriceData.prod_cat == prod_cat,
                        PriceData.prod_pcatid == prod_pcatid,
                        PriceData.prod_pcat == prod_pcat,
                        PriceData.low_price == low_price,
                        PriceData.high_price == high_price,
                        PriceData.avg_price == avg_price,
                        PriceData.place == place,
                        PriceData.spec_info == spec_info,
                        PriceData.unit_info == unit_info,
                        PriceData.pub_date == pub_date_obj,
                        PriceData.status == status
                    )
                )
        
        if not conditions:
            return {}
        
        # 执行查询
        existing_records = db.query(PriceData).filter(or_(*conditions)).all()
        
        # 构建结果映射
        result = {}
        for record in existing_records:
            # 确保日期格式一致
            date_str = record.pub_date.strftime('%Y-%m-%d %H:%M:%S') if record.pub_date else ''
            # 构建包含所有业务字段的唯一键
            unique_key = f"{record.prod_name}|{record.prod_catid}|{record.prod_cat}|{record.prod_pcatid}|{record.prod_pcat}|{record.low_price}|{record.high_price}|{record.avg_price}|{record.place}|{record.spec_info}|{record.unit_info}|{date_str}|{record.status}"
            result[unique_key] = record
        
        return result
    
    @staticmethod
    def update(db: Session, record_id: int, update_data: Dict[str, Any]) -> Optional[PriceData]:
        """更新价格数据记录"""
        try:
            db_obj = db.query(PriceData).filter(PriceData.id == record_id).first()
            if not db_obj:
                return None
            
            logger.debug(f"更新记录 ID={record_id}, 更新数据: {update_data}")
            
            # 字段映射
            field_mapping = {
                'prodName': 'prod_name',
                'prodPcatid': 'prod_pcatid', 
                'pubDate': 'pub_date',
                'lowPrice': 'low_price',
                'highPrice': 'high_price',
                'avgPrice': 'avg_price'
            }
            
            # 更新字段
            for field, value in update_data.items():
                # 使用字段映射
                db_field = field_mapping.get(field, field)
                if hasattr(db_obj, db_field):
                    # 处理特殊字段类型
                    if db_field == 'pub_date' and isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    elif db_field in ['low_price', 'high_price', 'avg_price']:
                        value = float(value)
                    
                    setattr(db_obj, db_field, value)
                    logger.debug(f"设置字段 {db_field} = {value}")
            
            db_obj.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_obj)
            
            logger.debug(f"更新价格数据记录: ID={record_id}, 新的avg_price={db_obj.avg_price}")
            return db_obj
            
        except Exception as e:
            db.rollback()
            logger.error(f"更新价格数据记录失败: {e}")
            raise
    
    @staticmethod
    def delete(db: Session, record_id: int) -> bool:
        """删除价格数据记录"""
        try:
            db_obj = db.query(PriceData).filter(PriceData.id == record_id).first()
            if not db_obj:
                return False
            
            db.delete(db_obj)
            db.commit()
            
            logger.debug(f"删除价格数据记录: ID={record_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"删除价格数据记录失败: {e}")
            raise
    
    @staticmethod
    def get_multi(db: Session, 
                  skip: int = 0, 
                  limit: int = 100) -> List[PriceData]:
        """获取多条价格数据记录"""
        return db.query(PriceData).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all(db: Session, 
                skip: int = 0, 
                limit: int = 100,
                order_by: str = 'id',
                order_desc: bool = False) -> List[PriceData]:
        """获取所有价格数据（分页）"""
        query = db.query(PriceData)
        
        # 排序
        if hasattr(PriceData, order_by):
            order_column = getattr(PriceData, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search(db: Session,
               prod_name: Optional[str] = None,
               prod_cat: Optional[str] = None,
               place: Optional[str] = None,
               date_from: Optional[date] = None,
               date_to: Optional[date] = None,
               min_price: Optional[float] = None,
               max_price: Optional[float] = None,
               skip: int = 0,
               limit: int = 100) -> Tuple[List[PriceData], int]:
        """搜索价格数据"""
        query = db.query(PriceData)
        
        # 构建查询条件
        conditions = []
        
        if prod_name:
            conditions.append(PriceData.prod_name.like(f'%{prod_name}%'))
        
        if prod_cat:
            conditions.append(PriceData.prod_cat.like(f'%{prod_cat}%'))
        
        if place:
            conditions.append(PriceData.place.like(f'%{place}%'))
        
        if date_from:
            conditions.append(PriceData.pub_date >= date_from)
        
        if date_to:
            conditions.append(PriceData.pub_date <= date_to)
        
        if min_price is not None:
            conditions.append(PriceData.avg_price >= min_price)
        
        if max_price is not None:
            conditions.append(PriceData.avg_price <= max_price)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        results = query.order_by(desc(PriceData.pub_date)).offset(skip).limit(limit).all()
        
        return results, total
    
    @staticmethod
    def get_latest_by_product(db: Session, prod_name: str, limit: int = 10) -> List[PriceData]:
        """获取指定产品的最新价格数据"""
        return (db.query(PriceData)
                .filter(PriceData.prod_name == prod_name)
                .order_by(desc(PriceData.pub_date))
                .limit(limit)
                .all())
    
    @staticmethod
    def get_price_trend(db: Session, 
                       prod_name: str, 
                       days: int = 30) -> List[PriceData]:
        """获取产品价格趋势数据"""
        date_threshold = datetime.now() - timedelta(days=days)
        
        return (db.query(PriceData)
                .filter(and_(
                    PriceData.prod_name == prod_name,
                    PriceData.pub_date >= date_threshold
                ))
                .order_by(asc(PriceData.pub_date))
                .all())
    
    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """获取数据统计信息"""
        total_records = db.query(PriceData).count()
        
        # 产品数量统计
        product_count = db.query(func.count(func.distinct(PriceData.prod_name))).scalar()
        
        # 分类统计
        category_count = db.query(func.count(func.distinct(PriceData.prod_cat))).scalar()
        
        # 最新更新时间
        latest_update = db.query(func.max(PriceData.pub_date)).scalar()
        
        # 价格范围统计
        price_stats = db.query(
            func.min(PriceData.avg_price),
            func.max(PriceData.avg_price),
            func.avg(PriceData.avg_price)
        ).first()
        
        # 获取日期范围
        date_range_query = db.query(
            func.min(PriceData.pub_date),
            func.max(PriceData.pub_date)
        ).first()
        
        # 获取分类信息
        categories = db.query(
            PriceData.prod_cat,
            func.count(PriceData.id).label('count')
        ).group_by(PriceData.prod_cat).all()
        
        return {
            'total_records': total_records,
            'unique_products': product_count,
            'date_range': {
                'start': date_range_query[0].isoformat() if date_range_query[0] else None,
                'end': date_range_query[1].isoformat() if date_range_query[1] else None
            },
            'latest_update': latest_update.isoformat() if latest_update else None,
            'categories': [
                {'name': cat[0] or '未分类', 'count': cat[1]} 
                for cat in categories
            ],
            'price_stats': {
                'min_price': float(price_stats[0]) if price_stats[0] else None,
                'max_price': float(price_stats[1]) if price_stats[1] else None,
                'avg_price': float(price_stats[2]) if price_stats[2] else None
            }
        }
    
    @staticmethod
    def get_price_trend_data(db: Session, price_id: int, prod_name: str, current_date: datetime) -> Dict:
        """获取价格趋势数据"""
        # 获取当前价格记录
        current_price = db.query(PriceData).filter(PriceData.id == price_id).first()
        if not current_price or not current_price.avg_price:
            return {}
        
        current_avg_price = float(current_price.avg_price)
        
        # 定义时间段
        time_periods = [1, 3, 7, 14, 30]
        trend_data = {}
        
        for days in time_periods:
            # 计算目标日期
            target_date = current_date - timedelta(days=days)
            
            # 查找最接近目标日期的价格记录
            historical_price = db.query(PriceData).filter(
                PriceData.prod_name == prod_name,
                PriceData.pub_date <= target_date,
                PriceData.avg_price.isnot(None)
            ).order_by(PriceData.pub_date.desc()).first()
            
            if historical_price and historical_price.avg_price:
                historical_avg_price = float(historical_price.avg_price)
                
                # 计算价格变化
                price_change = current_avg_price - historical_avg_price
                price_change_percent = (price_change / historical_avg_price * 100) if historical_avg_price != 0 else 0
                
                trend_data[f"change_{days}d"] = round(price_change, 2)
                trend_data[f"change_{days}d_percent"] = round(price_change_percent, 2)
            else:
                trend_data[f"change_{days}d"] = None
                trend_data[f"change_{days}d_percent"] = None
        
        return trend_data

class ScrapingLogCRUD:
    """抓取日志CRUD操作类"""
    
    @staticmethod
    def create_log(db: Session, 
                   total_records: int,
                   new_records: int,
                   updated_records: int,
                   status: str,
                   error_message: Optional[str] = None) -> ScrapingLog:
        """创建抓取日志"""
        try:
            log_entry = ScrapingLog(
                total_records=total_records,
                new_records=new_records,
                updated_records=updated_records,
                status=status,
                error_message=error_message
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            
            logger.info(f"创建抓取日志: 状态={status}, 新增={new_records}, 更新={updated_records}")
            return log_entry
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建抓取日志失败: {e}")
            raise
    
    @staticmethod
    def get_recent_logs(db: Session, limit: int = 10) -> List[ScrapingLog]:
        """获取最近的抓取日志"""
        return (db.query(ScrapingLog)
                .order_by(desc(ScrapingLog.scrape_date))
                .limit(limit)
                .all())
    
    @staticmethod
    def get_logs_by_status(db: Session, status: str, limit: int = 10) -> List[ScrapingLog]:
        """根据状态获取抓取日志"""
        return (db.query(ScrapingLog)
                .filter(ScrapingLog.status == status)
                .order_by(desc(ScrapingLog.scrape_date))
                .limit(limit)
                .all())

# 批量操作辅助函数
def bulk_create_or_update(db: Session, records: List[Dict[str, Any]]) -> Tuple[int, int]:
    """批量创建或更新记录
    
    使用所有业务字段作为唯一键进行去重
    
    Returns:
        Tuple[新增记录数, 更新记录数]
    """
    if not records:
        return 0, 0
    
    new_count = 0
    updated_count = 0

    logger.info(records)
    
    try:
        # 检查哪些记录已存在（基于唯一键）
        existing_records = PriceDataCRUD.exists_batch_by_unique_key(db, records)
        logger.debug(f"找到 {len(existing_records)} 条已存在记录: {list(existing_records.keys())}")
        if len(existing_records) > 0:
            logger.info(existing_records)
        
        # 顺序处理记录，支持同批次内的去重和更新
        created_count = 0
        updated_count = 0
        processed_in_batch = {}  # 跟踪本批次中已处理的记录
        
        for record in records:
            # 提取所有业务字段
            prod_name = record.get('prodName')
            prod_catid = record.get('prodCatid')
            prod_cat = record.get('prodCat')
            prod_pcatid = record.get('prodPcatid')
            prod_pcat = record.get('prodPcat')
            low_price = record.get('lowPrice')
            high_price = record.get('highPrice')
            avg_price = record.get('avgPrice')
            place = record.get('place')
            spec_info = record.get('specInfo')
            unit_info = record.get('unitInfo')
            pub_date = record.get('pubDate')
            status = record.get('status')
            
            # 跳过缺少基本必需字段的记录
            if not prod_name or not pub_date:
                logger.warning(f"跳过缺少关键字段的记录: {record}")
                continue
            
            # 将空字符串规范化为空字符串（确保一致性）
            spec_info = spec_info or ''
            place = place or ''
            
            # 转换日期格式用于构建唯一键
            if isinstance(pub_date, str):
                pub_date_obj = datetime.strptime(pub_date, '%Y-%m-%d %H:%M:%S')
                date_str = pub_date
            else:
                pub_date_obj = pub_date
                date_str = pub_date_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            # 构建包含所有业务字段的唯一键
            unique_key = f"{prod_name}|{prod_catid}|{prod_cat}|{prod_pcatid}|{prod_pcat}|{low_price}|{high_price}|{avg_price}|{place}|{spec_info}|{unit_info}|{date_str}|{status}"
            logger.debug(f"处理记录，唯一键: {unique_key}")
            
            # 检查是否在本批次中已经处理过
            if unique_key in processed_in_batch:
                # 更新本批次中已存在的记录
                existing_id = processed_in_batch[unique_key]
                try:
                    PriceDataCRUD.update(db, existing_id, record)
                    updated_count += 1
                    logger.debug(f"更新本批次记录: {unique_key}")
                except Exception as e:
                    logger.error(f"更新记录失败: {e}")
                continue
            
            # 检查数据库中是否已存在
            if unique_key in existing_records:
                # 更新数据库中已存在的记录
                existing_record = existing_records[unique_key]
                try:
                    PriceDataCRUD.update(db, existing_record.id, record)
                    updated_count += 1
                    processed_in_batch[unique_key] = existing_record.id
                    logger.debug(f"更新数据库记录: {unique_key}")
                except Exception as e:
                    logger.error(f"更新记录失败: {e}")
            else:
                # 创建新记录
                try:
                    new_record = PriceDataCRUD.create(db, record)
                    created_count += 1
                    processed_in_batch[unique_key] = new_record.id
                    logger.debug(f"创建新记录: {unique_key}")
                except Exception as e:
                    logger.error(f"创建记录失败: {e}")
        
        logger.info(f"批量操作完成: 新增 {created_count} 条, 更新 {updated_count} 条, 跳过重复 {len(records) - created_count - updated_count} 条")
        return created_count, updated_count
        
    except Exception as e:
        db.rollback()
        logger.error(f"批量操作失败: {e}")
        raise