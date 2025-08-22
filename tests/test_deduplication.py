import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PriceData
from crud import PriceDataCRUD, bulk_create_or_update


class TestDeduplication:
    """测试去重功能"""
    
    @pytest.fixture
    def db_session(self):
        """创建测试数据库会话"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_create_duplicate_prevention(self, db_session):
        """测试创建记录时的去重功能"""
        # 准备测试数据
        price_data = {
            'prodName': '苹果',
            'prodCat': '水果',
            'prodCatid': '001',
            'prodPcat': '农产品',
            'prodPcatid': '100',
            'specInfo': '红富士',
            'place': '北京',
            'pubDate': '2024-01-15 10:00:00',
            'lowPrice': '5.0',
            'highPrice': '8.0',
            'avgPrice': '6.5',
            'unitInfo': '斤',
            'status': '正常'
        }
        
        # 第一次创建记录
        record1 = PriceDataCRUD.create(db_session, price_data)
        assert record1 is not None
        assert record1.prod_name == '苹果'
        
        # 尝试创建相同的记录（应该返回已存在的记录）
        record2 = PriceDataCRUD.create(db_session, price_data)
        assert record2.id == record1.id  # 应该返回相同的记录
        
        # 验证数据库中只有一条记录
        all_records = db_session.query(PriceData).all()
        assert len(all_records) == 1
    
    def test_exists_by_unique_key(self, db_session):
        """测试基于唯一键的存在性检查"""
        # 创建测试记录
        price_data = {
            'prodName': '香蕉',
            'prodCat': '水果',
            'prodCatid': '002',
            'prodPcat': '农产品',
            'prodPcatid': '100',
            'specInfo': '进口',
            'place': '海南',
            'pubDate': '2024-01-15 10:00:00',
            'lowPrice': '3.0',
            'highPrice': '5.0',
            'avgPrice': '4.0',
            'unitInfo': '斤',
            'status': '正常'
        }
        
        # 记录不存在时应该返回None
        existing = PriceDataCRUD.exists_by_unique_key(db_session, price_data)
        assert existing is None
        
        # 创建记录
        record = PriceDataCRUD.create(db_session, price_data)
        
        # 记录存在时应该返回记录
        existing = PriceDataCRUD.exists_by_unique_key(db_session, price_data)
        assert existing is not None
        assert existing.id == record.id
    
    def test_bulk_create_or_update_deduplication(self, db_session):
        """测试批量操作的去重功能 - 现在所有字段都是唯一键"""
        # 准备测试数据
        records = [
            {
                'prodName': '橙子',
                'prodCat': '水果',
                'prodCatid': '003',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '脐橙',
                'place': '江西',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '4.0',
                'highPrice': '6.0',
                'avgPrice': '5.0',
                'unitInfo': '斤',
                'status': '正常'
            },
            {
                'prodName': '橙子',
                'prodCat': '水果',
                'prodCatid': '003',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '脐橙',
                'place': '江西',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '4.0',
                'highPrice': '6.0',
                'avgPrice': '5.0',
                'unitInfo': '斤',
                'status': '正常'  # 完全相同的记录 - 应该被去重
            },
            {
                'prodName': '橙子',
                'prodCat': '水果',
                'prodCatid': '003',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '脐橙',
                'place': '江西',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '4.5',  # 价格不同 - 不应该被去重
                'highPrice': '6.0',
                'avgPrice': '5.0',
                'unitInfo': '斤',
                'status': '正常'
            }
        ]
        
        # 执行批量操作
        new_count, updated_count = bulk_create_or_update(db_session, records)
        
        # 应该创建2条新记录，更新1条记录
        assert new_count == 2
        assert updated_count == 1
        
        # 验证数据库中的记录数
        all_records = db_session.query(PriceData).all()
        assert len(all_records) == 2  # 2条不同的记录（价格不同）
    
    def test_different_products_same_date(self, db_session):
        """测试相同日期但不同产品的记录不会被去重"""
        records = [
            {
                'prodName': '苹果',
                'prodCat': '水果',
                'prodCatid': '001',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '红富士',
                'place': '山东',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '5.0',
                'highPrice': '7.0',
                'avgPrice': '6.0',
                'unitInfo': '斤',
                'status': '正常'
            },
            {
                'prodName': '梨子',  # 不同产品
                'prodCat': '水果',
                'prodCatid': '004',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '雪花梨',
                'place': '山东',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '6.0',
                'highPrice': '8.0',
                'avgPrice': '7.0',
                'unitInfo': '斤',
                'status': '正常'
            }
        ]
        
        new_count, updated_count = bulk_create_or_update(db_session, records)
        
        # 应该创建2条新记录，不更新任何记录
        assert new_count == 2
        assert updated_count == 0
        
        # 验证数据库中有2条记录
        all_records = db_session.query(PriceData).all()
        assert len(all_records) == 2
    
    def test_same_product_different_category(self, db_session):
        """测试相同产品不同分类的情况"""
        test_data = [
            {
                'prodName': '苹果',
                'prodCat': '水果',
                'prodCatid': '001',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '红富士',
                'place': '山东',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '5.0',
                'highPrice': '7.0',
                'avgPrice': '6.0',
                'unitInfo': '斤',
                'status': '正常'
            },
            {
                'prodName': '苹果',
                'prodCat': '蔬菜',  # 不同分类
                'prodCatid': '005',
                'prodPcat': '农产品',
                'prodPcatid': '100',
                'specInfo': '红富士',
                'place': '山东',
                'pubDate': '2024-01-15 10:00:00',
                'lowPrice': '6.0',
                'highPrice': '8.0',
                'avgPrice': '7.0',
                'unitInfo': '斤',
                'status': '正常'
            }
        ]
        
        new_count, updated_count = bulk_create_or_update(db_session, test_data)
        
        # 应该创建2条记录，因为分类不同
        assert new_count == 2
        assert updated_count == 0
        
        # 验证数据库中有2条记录
        total_records = db_session.query(PriceData).count()
        assert total_records == 2
    
    def test_any_field_change_creates_unique_record(self, db_session):
        """测试任何字段的变化都会创建新的唯一记录"""
        base_record = {
            'prodName': '西瓜',
            'prodCat': '水果',
            'prodCatid': '006',
            'prodPcat': '农产品',
            'prodPcatid': '100',
            'specInfo': '无籽',
            'place': '新疆',
            'pubDate': '2024-01-15 10:00:00',
            'lowPrice': '2.0',
            'highPrice': '4.0',
            'avgPrice': '3.0',
            'unitInfo': '斤',
            'status': '正常'
        }
        
        # 创建基础记录
        record1 = PriceDataCRUD.create(db_session, base_record)
        assert record1 is not None
        
        # 测试改变不同字段都会创建新记录
        test_cases = [
            ('lowPrice', '2.5'),  # 改变最低价
            ('highPrice', '4.5'),  # 改变最高价
            ('avgPrice', '3.5'),   # 改变平均价
            ('unitInfo', '公斤'),   # 改变单位
            ('status', '缺货'),     # 改变状态
            ('specInfo', '有籽'),   # 改变规格
            ('place', '山东')       # 改变产地
        ]
        
        for field, new_value in test_cases:
            modified_record = base_record.copy()
            modified_record[field] = new_value
            
            # 每个修改都应该创建新记录
            new_record = PriceDataCRUD.create(db_session, modified_record)
            assert new_record is not None
            assert new_record.id != record1.id
        
        # 验证数据库中有8条记录（1个基础 + 7个变化）
        total_records = db_session.query(PriceData).count()
        assert total_records == 8