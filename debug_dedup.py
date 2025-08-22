#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PriceData
from crud import PriceDataCRUD, bulk_create_or_update
from loguru import logger

# 设置日志级别
logger.remove()
logger.add(sys.stderr, level="DEBUG")

def debug_deduplication():
    # 创建内存数据库
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 准备测试数据
    records = [
        {
            'prodName': '橙子',
            'prodPcatid': '1003',
            'pubDate': '2024-01-15 10:00:00',
            'lowPrice': '4.0',
            'highPrice': '6.0',
            'avgPrice': '5.0'
        },
        {
            'prodName': '橙子',  # 相同产品
            'prodPcatid': '1003',  # 相同分类
            'pubDate': '2024-01-15 10:00:00',  # 相同日期 - 应该被去重
            'lowPrice': '4.5',
            'highPrice': '6.5',
            'avgPrice': '5.5'
        },
        {
            'prodName': '橙子',  # 相同产品
            'prodPcatid': '1003',  # 相同分类
            'pubDate': '2024-01-16 10:00:00',  # 不同日期 - 不应该被去重
            'lowPrice': '4.2',
            'highPrice': '6.2',
            'avgPrice': '5.2'
        }
    ]
    
    print("=== 开始调试去重逻辑 ===")
    
    # 测试 exists_batch_by_unique_key
    print("\n1. 测试 exists_batch_by_unique_key (空数据库):")
    existing = PriceDataCRUD.exists_batch_by_unique_key(db, records)
    print(f"找到已存在记录: {len(existing)} 条")
    print(f"已存在记录键: {list(existing.keys())}")
    
    # 先创建第一条记录
    print("\n2. 创建第一条记录:")
    first_record = PriceDataCRUD.create(db, records[0])
    print(f"创建记录 ID: {first_record.id}")
    
    # 再次测试 exists_batch_by_unique_key
    print("\n3. 测试 exists_batch_by_unique_key (有一条记录):")
    existing = PriceDataCRUD.exists_batch_by_unique_key(db, records)
    print(f"找到已存在记录: {len(existing)} 条")
    print(f"已存在记录键: {list(existing.keys())}")
    
    # 手动构建唯一键看看
    print("\n4. 手动构建唯一键:")
    for i, record in enumerate(records):
        prod_name = record.get('prodName')
        prod_pcatid = record.get('prodPcatid')
        pub_date = record.get('pubDate')
        unique_key = f"{prod_name}|{prod_pcatid}|{pub_date}"
        print(f"记录 {i+1} 唯一键: {unique_key}")
    
    # 查看数据库中的记录
    print("\n5. 数据库中的记录:")
    db_records = db.query(PriceData).all()
    for record in db_records:
        date_str = record.pub_date.strftime('%Y-%m-%d %H:%M:%S') if record.pub_date else ''
        unique_key = f"{record.prod_name}|{record.prod_pcatid}|{date_str}"
        print(f"数据库记录唯一键: {unique_key}")
    
    # 执行批量操作
    print("\n6. 执行批量操作:")
    new_count, updated_count = bulk_create_or_update(db, records)
    print(f"新增: {new_count}, 更新: {updated_count}")
    
    # 最终检查
    print("\n7. 最终数据库记录:")
    final_records = db.query(PriceData).all()
    print(f"总记录数: {len(final_records)}")
    for record in final_records:
        print(f"ID: {record.id}, 产品: {record.prod_name}, 日期: {record.pub_date}, 平均价格: {record.avg_price}")
    
    db.close()

if __name__ == "__main__":
    debug_deduplication()