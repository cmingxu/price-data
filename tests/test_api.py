#!/usr/bin/env python3
"""
新发地价格数据API测试

测试所有API端点的功能性和错误处理
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app
from models import Base, PriceData, get_db
from config import Config
from crud import PriceDataCRUD

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_price_data.db"

# 创建测试数据库引擎
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 测试客户端
client = TestClient(app)

@pytest.fixture(scope="session")
def setup_test_database():
    """设置测试数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=test_engine)
    
    # 插入测试数据
    db = TestSessionLocal()
    
    test_data = [
        {
            "id": 1,
            "prodName": "苹果",
            "prodCat": "水果",
            "prodCatid": 1,
            "prodPcat": "新鲜水果",
            "prodPcatid": 10,
            "lowPrice": "8.0",
            "highPrice": "12.0",
            "avgPrice": "10.0",
            "specInfo": "富士苹果",
            "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "place": "山东"
        },
        {
            "id": 2,
            "prodName": "香蕉",
            "prodCat": "水果",
            "prodCatid": 1,
            "prodPcat": "新鲜水果",
            "prodPcatid": 10,
            "lowPrice": "5.0",
            "highPrice": "8.0",
            "avgPrice": "6.5",
            "specInfo": "进口香蕉",
            "pubDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "place": "菲律宾"
        },
        {
            "id": 3,
            "prodName": "白菜",
            "prodCat": "蔬菜",
            "prodCatid": 2,
            "prodPcat": "叶菜类",
            "prodPcatid": 20,
            "lowPrice": "2.0",
            "highPrice": "3.5",
            "avgPrice": "2.8",
            "specInfo": "大白菜",
            "pubDate": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "place": "河北"
        }
    ]
    
    for data in test_data:
        PriceDataCRUD.create(db, data)
    
    db.close()
    yield
    
    # 清理测试数据库
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_price_data.db"):
        os.remove("test_price_data.db")

@pytest.fixture
def override_get_db():
    """覆盖数据库依赖"""
    def _get_test_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    from api import get_db
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

class TestHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check(self, setup_test_database, override_get_db):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"

class TestPricesEndpoint:
    """价格数据端点测试"""
    
    def test_get_prices_default(self, setup_test_database, override_get_db):
        """测试获取价格数据（默认参数）"""
        response = client.get("/api/prices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0
    
    def test_get_prices_with_limit(self, setup_test_database, override_get_db):
        """测试获取价格数据（指定限制）"""
        response = client.get("/api/prices?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
    
    def test_get_prices_with_offset(self, setup_test_database, override_get_db):
        """测试获取价格数据（指定偏移）"""
        response = client.get("/api/prices?skip=1&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
    
    def test_get_prices_invalid_limit(self, setup_test_database, override_get_db):
        """测试无效的限制参数"""
        response = client.get("/api/prices?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_get_prices_large_limit(self, setup_test_database, override_get_db):
        """测试过大的限制参数"""
        response = client.get("/api/prices?limit=1001")
        assert response.status_code == 422  # Validation error
    
    def test_get_prices_negative_skip(self, setup_test_database, override_get_db):
        """测试负数跳过参数"""
        response = client.get("/api/prices?skip=-1")
        assert response.status_code == 422  # Validation error

class TestProductsEndpoint:
    """产品端点测试"""
    
    def test_get_products(self, setup_test_database, override_get_db):
        """测试获取产品列表"""
        response = client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert isinstance(data["products"], list)
    
    def test_get_products_with_search(self, setup_test_database, override_get_db):
        """测试搜索产品"""
        response = client.get("/api/products?search=苹果")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert isinstance(data["products"], list)

class TestStatisticsEndpoint:
    """统计端点测试"""
    
    def test_get_statistics(self, setup_test_database, override_get_db):
        """测试获取统计信息"""
        response = client.get("/api/statistics")
        assert response.status_code == 200
        data = response.json()
        
        # 检查必需字段
        required_fields = [
            "total_records", "unique_products", "date_range", 
            "latest_update", "categories"
        ]
        for field in required_fields:
            assert field in data
        
        # 检查数据类型
        assert isinstance(data["total_records"], int)
        assert isinstance(data["unique_products"], int)
        assert isinstance(data["categories"], list)
        assert data["total_records"] >= 0
        assert data["unique_products"] >= 0

class TestCategoriesEndpoint:
    """分类端点测试"""
    
    def test_get_categories(self, setup_test_database, override_get_db):
        """测试获取分类列表"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)

class TestCreatePriceEndpoint:
    """创建价格数据端点测试"""
    
    def test_create_price_data(self, setup_test_database, override_get_db):
        """测试创建价格数据"""
        new_price_data = {
            "prod_name": "测试产品",
            "prod_cat": "测试分类",
            "prod_catid": 999,
            "prod_pcat": "测试父分类",
            "prod_pcatid": 99,
            "low_price": 10.0,
            "high_price": 15.0,
            "avg_price": 12.5,
            "spec_info": "测试规格",
            "unit_info": "测试单位",
            "pub_date": datetime.now().isoformat(),
            "place": "测试产地"
        }
        
        response = client.post("/api/prices", json=new_price_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["prod_name"] == "测试产品"
    
    def test_create_price_data_invalid(self, setup_test_database, override_get_db):
        """测试创建无效价格数据"""
        invalid_data = {
            "prod_name": "",  # 空名称
            # 缺少必需字段
        }
        
        response = client.post("/api/prices", json=invalid_data)
        assert response.status_code == 422  # Validation error

class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_endpoint(self, setup_test_database, override_get_db):
        """测试不存在的端点"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, setup_test_database, override_get_db):
        """测试不允许的HTTP方法"""
        response = client.delete("/api/prices")
        assert response.status_code == 405  # Method not allowed

class TestAsyncEndpoints:
    """异步端点测试"""
    
    @pytest.mark.asyncio
    async def test_async_health_check(self, setup_test_database, override_get_db):
        """测试异步健康检查"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_async_get_prices(self, setup_test_database, override_get_db):
        """测试异步获取价格数据"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/prices?limit=5")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

if __name__ == "__main__":
    # 运行测试
    pytest.main(["-v", __file__])