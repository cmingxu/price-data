#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试价格趋势API功能
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, get_db
from models import Base, PriceData
from config import Config

# 创建测试数据库
engine = create_engine(Config.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class TestTrendingAPI:
    """测试价格趋势API"""
    
    def test_prices_without_trending(self):
        """测试不带trending参数的价格查询"""
        response = client.get("/api/prices?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            # 检查返回的字段不包含trend_data
            assert "trend_data" not in data[0]
            # 检查基本字段存在
            required_fields = ["id", "prod_name", "avg_price", "pub_date"]
            for field in required_fields:
                assert field in data[0]
    
    def test_prices_with_trending_false(self):
        """测试trending=false的价格查询"""
        response = client.get("/api/prices?limit=3&trending=false")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            # 检查返回的字段不包含trend_data
            assert "trend_data" not in data[0]
    
    def test_prices_with_trending_true(self):
        """测试trending=true的价格查询"""
        response = client.get("/api/prices?limit=3&trending=true")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            # 检查返回的字段包含trend_data
            assert "trend_data" in data[0]
            
            trend_data = data[0]["trend_data"]
            assert isinstance(trend_data, dict)
            
            # 检查趋势数据字段
            expected_trend_fields = [
                "change_1d", "change_1d_percent",
                "change_3d", "change_3d_percent",
                "change_7d", "change_7d_percent",
                "change_14d", "change_14d_percent",
                "change_30d", "change_30d_percent"
            ]
            
            for field in expected_trend_fields:
                assert field in trend_data
                # 值可以是None或数字
                assert trend_data[field] is None or isinstance(trend_data[field], (int, float))
    
    def test_prices_with_trending_and_filters(self):
        """测试带过滤条件和trending的价格查询"""
        response = client.get("/api/prices?limit=1&trending=true&prod_name=白萝卜")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if data:
            # 检查产品名称过滤生效
            assert "白萝卜" in data[0]["prod_name"]
            # 检查包含趋势数据
            assert "trend_data" in data[0]
            assert isinstance(data[0]["trend_data"], dict)
    
    def test_trending_data_structure(self):
        """测试趋势数据结构的完整性"""
        response = client.get("/api/prices?limit=1&trending=true")
        assert response.status_code == 200
        
        data = response.json()
        if data:
            price_record = data[0]
            
            # 检查基本价格字段
            basic_fields = [
                "id", "prod_name", "prod_catid", "prod_cat",
                "low_price", "high_price", "avg_price",
                "pub_date", "created_at", "updated_at"
            ]
            
            for field in basic_fields:
                assert field in price_record
            
            # 检查趋势数据字段
            assert "trend_data" in price_record
            trend_data = price_record["trend_data"]
            
            # 检查所有时间段的变化数据
            time_periods = ["1d", "3d", "7d", "14d", "30d"]
            for period in time_periods:
                change_field = f"change_{period}"
                percent_field = f"change_{period}_percent"
                
                assert change_field in trend_data
                assert percent_field in trend_data
                
                # 如果有数据，应该是数字类型
                if trend_data[change_field] is not None:
                    assert isinstance(trend_data[change_field], (int, float))
                if trend_data[percent_field] is not None:
                    assert isinstance(trend_data[percent_field], (int, float))
    
    def test_trending_with_different_limits(self):
        """测试不同limit值下的trending功能"""
        for limit in [1, 5, 10]:
            response = client.get(f"/api/prices?limit={limit}&trending=true")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= limit
            
            # 每条记录都应该有趋势数据
            for record in data:
                assert "trend_data" in record
                assert isinstance(record["trend_data"], dict)

if __name__ == "__main__":
    pytest.main(["-v", __file__])