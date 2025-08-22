from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field
from loguru import logger

from models import get_db, PriceData as PriceDataModel
from crud import PriceDataCRUD, ScrapingLogCRUD
from data_manager import DataManager
from config import Config

# Pydantic 模型
class PriceDataResponse(BaseModel):
    """价格数据响应模型"""
    id: int
    prod_name: str
    prod_catid: Optional[int] = None
    prod_cat: Optional[str] = None
    prod_pcatid: Optional[int] = None
    prod_pcat: Optional[str] = None
    low_price: Optional[float] = None
    high_price: Optional[float] = None
    avg_price: Optional[float] = None
    place: Optional[str] = None
    spec_info: Optional[str] = None
    unit_info: Optional[str] = None
    pub_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PriceTrendData(BaseModel):
    """价格趋势数据模型"""
    change_1d: Optional[float] = Field(None, description="1天价格变化")
    change_3d: Optional[float] = Field(None, description="3天价格变化")
    change_7d: Optional[float] = Field(None, description="7天价格变化")
    change_14d: Optional[float] = Field(None, description="14天价格变化")
    change_30d: Optional[float] = Field(None, description="30天价格变化")
    change_1d_percent: Optional[float] = Field(None, description="1天价格变化百分比")
    change_3d_percent: Optional[float] = Field(None, description="3天价格变化百分比")
    change_7d_percent: Optional[float] = Field(None, description="7天价格变化百分比")
    change_14d_percent: Optional[float] = Field(None, description="14天价格变化百分比")
    change_30d_percent: Optional[float] = Field(None, description="30天价格变化百分比")

class PriceDataWithTrendResponse(BaseModel):
    """带趋势数据的价格响应模型"""
    id: int
    prod_name: str
    prod_catid: Optional[int] = None
    prod_cat: Optional[str] = None
    prod_pcatid: Optional[int] = None
    prod_pcat: Optional[str] = None
    low_price: Optional[float] = None
    high_price: Optional[float] = None
    avg_price: Optional[float] = None
    place: Optional[str] = None
    spec_info: Optional[str] = None
    unit_info: Optional[str] = None
    pub_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    trend_data: Optional[PriceTrendData] = None
    
    class Config:
        from_attributes = True

class PriceDataCreate(BaseModel):
    """创建价格数据模型"""
    prod_name: str = Field(..., description="产品名称")
    prod_catid: int = Field(..., description="产品分类ID")
    prod_cat: str = Field(..., description="产品分类")
    prod_pcatid: int = Field(..., description="产品父分类ID")
    prod_pcat: str = Field(..., description="产品父分类")
    low_price: float = Field(..., description="最低价格")
    high_price: float = Field(..., description="最高价格")
    avg_price: float = Field(..., description="平均价格")
    place: Optional[str] = Field(None, description="产地")
    spec_info: Optional[str] = Field(None, description="规格信息")
    unit_info: Optional[str] = Field(None, description="单位信息")
    pub_date: datetime = Field(..., description="发布日期")

class SyncRequest(BaseModel):
    """同步请求模型"""
    limit: int = Field(20, description="每页记录数", ge=1, le=100)
    max_pages: Optional[int] = Field(None, description="最大页数限制", ge=1)
    days_back: Optional[int] = Field(None, description="同步最近几天的数据", ge=1)
    prod_name: Optional[str] = Field(None, description="产品名称")
    prod_catid: Optional[str] = Field(None, description="产品分类ID")

class SyncResponse(BaseModel):
    """同步响应模型"""
    status: str
    message: str
    total_records: int
    new_records: int
    updated_records: int
    duration: float

class StatisticsResponse(BaseModel):
    """统计响应模型"""
    total_records: int
    unique_products: int
    date_range: Dict[str, Optional[str]]
    latest_update: Optional[str]
    categories: List[Dict[str, Any]]

# 创建 FastAPI 应用
app = FastAPI(
    title="新发地价格数据API",
    description="新发地农产品价格数据抓取和管理系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 全局数据管理器实例
data_manager = None

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global data_manager
    data_manager = DataManager()
    data_manager.ensure_database_setup()
    logger.info("FastAPI 应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global data_manager
    if data_manager:
        data_manager.close()
    logger.info("FastAPI 应用关闭完成")

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 价格数据查询接口
@app.get("/api/prices")
async def get_prices(
    skip: int = Query(0, description="跳过记录数", ge=0),
    limit: int = Query(20, description="返回记录数", ge=1, le=1000),
    prod_name: Optional[str] = Query(None, description="产品名称（模糊搜索）"),
    prod_cat: Optional[str] = Query(None, description="产品分类（模糊搜索）"),
    date_from: Optional[date] = Query(None, description="开始日期"),
    date_to: Optional[date] = Query(None, description="结束日期"),
    min_price: Optional[float] = Query(None, description="最低价格", ge=0),
    max_price: Optional[float] = Query(None, description="最高价格", ge=0),
    trending: bool = Query(False, description="是否包含价格趋势数据"),
    db: Session = Depends(get_db)
):
    """获取价格数据列表"""
    try:
        filters = {}
        if prod_name:
            filters['prod_name'] = prod_name
        if prod_cat:
            filters['prod_cat'] = prod_cat
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price
        
        # 根据是否有过滤条件选择合适的方法
        if any(filters.values()):
            # 使用search方法处理过滤条件
            prices, total = PriceDataCRUD.search(
                db, 
                prod_name=filters.get('prod_name'),
                prod_cat=filters.get('prod_cat'),
                place=None,  # place filter not implemented in API
                date_from=filters.get('date_from'),
                date_to=filters.get('date_to'),
                min_price=filters.get('min_price'),
                max_price=filters.get('max_price'),
                skip=skip,
                limit=limit
            )
        else:
            # 使用get_multi方法获取所有数据
            prices = PriceDataCRUD.get_multi(db, skip=skip, limit=limit)
        
        if trending:
            # 为每个价格记录计算趋势数据
            prices_with_trend = []
            for price in prices:
                trend_data = PriceDataCRUD.get_price_trend_data(db, price.id, price.prod_name, price.pub_date)
                price_dict = {
                    "id": price.id,
                    "prod_name": price.prod_name,
                    "prod_catid": price.prod_catid,
                    "prod_cat": price.prod_cat,
                    "prod_pcatid": price.prod_pcatid,
                    "prod_pcat": price.prod_pcat,
                    "low_price": price.low_price,
                    "high_price": price.high_price,
                    "avg_price": price.avg_price,
                    "place": price.place,
                    "spec_info": price.spec_info,
                    "unit_info": price.unit_info,
                    "pub_date": price.pub_date,
                    "created_at": price.created_at,
                    "updated_at": price.updated_at,
                    "trend_data": trend_data
                }
                prices_with_trend.append(price_dict)
            return prices_with_trend
        else:
            return prices
    except Exception as e:
        logger.error(f"获取价格数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取价格数据失败: {str(e)}")

@app.get("/api/prices/{price_id}", response_model=PriceDataResponse)
async def get_price(price_id: int, db: Session = Depends(get_db)):
    """获取单个价格数据"""
    price = PriceDataCRUD.get(db, price_id)
    if not price:
        raise HTTPException(status_code=404, detail="价格数据不存在")
    return price

@app.post("/api/prices", response_model=PriceDataResponse, status_code=201)
async def create_price(price_data: PriceDataCreate, db: Session = Depends(get_db)):
    """创建价格数据"""
    try:
        # 转换Pydantic模型数据为CRUD期望的格式
        data_dict = price_data.model_dump()
        crud_data = {
            'prodName': data_dict['prod_name'],
            'prodCatid': data_dict['prod_catid'],
            'prodCat': data_dict['prod_cat'],
            'prodPcatid': data_dict['prod_pcatid'],
            'prodPcat': data_dict['prod_pcat'],
            'lowPrice': str(data_dict['low_price']),
            'highPrice': str(data_dict['high_price']),
            'avgPrice': str(data_dict['avg_price']),
            'place': data_dict.get('place'),
            'specInfo': data_dict.get('spec_info'),
            'unitInfo': data_dict.get('unit_info'),
            'pubDate': data_dict['pub_date'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(data_dict['pub_date'], 'strftime') else str(data_dict['pub_date'])
        }
        price = PriceDataCRUD.create(db, crud_data)
        return price
    except Exception as e:
        logger.error(f"创建价格数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建价格数据失败: {str(e)}")

@app.put("/api/prices/{price_id}", response_model=PriceDataResponse)
async def update_price(price_id: int, price_data: PriceDataCreate, db: Session = Depends(get_db)):
    """更新价格数据"""
    existing_price = PriceDataCRUD.get(db, price_id)
    if not existing_price:
        raise HTTPException(status_code=404, detail="价格数据不存在")
    
    try:
        updated_price = PriceDataCRUD.update(db, price_id, price_data.dict())
        return updated_price
    except Exception as e:
        logger.error(f"更新价格数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新价格数据失败: {str(e)}")

@app.delete("/api/prices/{price_id}")
async def delete_price(price_id: int, db: Session = Depends(get_db)):
    """删除价格数据"""
    existing_price = PriceDataCRUD.get(db, price_id)
    if not existing_price:
        raise HTTPException(status_code=404, detail="价格数据不存在")
    
    try:
        success = PriceDataCRUD.delete(db, price_id)
        if success:
            return {"message": "价格数据删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
    except Exception as e:
        logger.error(f"删除价格数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除价格数据失败: {str(e)}")

# 统计接口
@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """获取数据统计信息"""
    try:
        stats = PriceDataCRUD.get_statistics(db)
        return StatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

# 数据同步接口
@app.post("/api/sync", response_model=SyncResponse)
async def sync_data(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    run_in_background: bool = Query(False, description="是否在后台运行")
):
    """同步数据"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    sync_params = sync_request.dict(exclude_none=True)
    
    if run_in_background:
        # 后台运行
        background_tasks.add_task(data_manager.sync_data, **sync_params)
        return SyncResponse(
            status="started",
            message="数据同步已在后台启动",
            total_records=0,
            new_records=0,
            updated_records=0,
            duration=0.0
        )
    else:
        # 同步运行
        try:
            result = data_manager.sync_data(**sync_params)
            return SyncResponse(**result)
        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            raise HTTPException(status_code=500, detail=f"数据同步失败: {str(e)}")

@app.post("/api/sync/incremental")
async def sync_incremental(
    background_tasks: BackgroundTasks,
    days: int = Query(1, description="同步最近几天的数据", ge=1, le=30),
    run_in_background: bool = Query(True, description="是否在后台运行")
):
    """增量同步数据"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    if run_in_background:
        background_tasks.add_task(data_manager.sync_incremental, days)
        return {"status": "started", "message": f"增量同步已启动，将同步最近 {days} 天的数据"}
    else:
        try:
            result = data_manager.sync_incremental(days)
            return result
        except Exception as e:
            logger.error(f"增量同步失败: {e}")
            raise HTTPException(status_code=500, detail=f"增量同步失败: {str(e)}")

@app.get("/api/sync/status")
async def get_sync_status():
    """获取同步状态"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    try:
        status = data_manager.get_sync_status()
        return status
    except Exception as e:
        logger.error(f"获取同步状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取同步状态失败: {str(e)}")

# 数据管理接口
@app.get("/api/duplicates")
async def get_duplicates():
    """获取重复记录"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    try:
        duplicates = data_manager.get_duplicate_records()
        return {"duplicates": duplicates, "count": len(duplicates)}
    except Exception as e:
        logger.error(f"获取重复记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取重复记录失败: {str(e)}")

@app.post("/api/duplicates/clean")
async def clean_duplicates(
    keep_latest: bool = Query(True, description="是否保留最新记录")
):
    """清理重复记录"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=500, detail="数据管理器未初始化")
    
    try:
        result = data_manager.clean_duplicates(keep_latest=keep_latest)
        return result
    except Exception as e:
        logger.error(f"清理重复记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理重复记录失败: {str(e)}")

# 产品和分类接口
@app.get("/api/products")
async def get_products(
    search: Optional[str] = Query(None, description="搜索产品名称"),
    limit: int = Query(50, description="返回记录数", ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取产品列表"""
    try:
        products = PriceDataCRUD.get_unique_products(db, search=search, limit=limit)
        return {"products": products}
    except Exception as e:
        logger.error(f"获取产品列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取产品列表失败: {str(e)}")

@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取分类列表"""
    try:
        categories = PriceDataCRUD.get_categories(db)
        return {"categories": categories}
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")

# 抓取日志接口
@app.get("/api/logs")
async def get_scraping_logs(
    skip: int = Query(0, description="跳过记录数", ge=0),
    limit: int = Query(20, description="返回记录数", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取抓取日志"""
    try:
        logs = ScrapingLogCRUD.get_recent_logs(db, skip=skip, limit=limit)
        return {
            "logs": [
                {
                    "id": log.id,
                    "scrape_date": log.scrape_date.isoformat(),
                    "total_records": log.total_records,
                    "new_records": log.new_records,
                    "updated_records": log.updated_records,
                    "status": log.status,
                    "error_message": log.error_message,
                    "duration": log.duration
                }
                for log in logs
            ]
        }
    except Exception as e:
        logger.error(f"获取抓取日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取抓取日志失败: {str(e)}")

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level="info"
    )