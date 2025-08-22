from sqlalchemy import Column, Integer, String, DateTime, Float, Text, create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

Base = declarative_base()

class PriceData(Base):
    """新发地价格数据模型"""
    __tablename__ = 'price_data'
    
    # 主键，使用原始API返回的ID
    id = Column(Integer, primary_key=True, index=True)
    
    # 产品信息
    prod_name = Column(String(100), nullable=False, index=True, comment='产品名称')
    prod_catid = Column(Integer, nullable=True, index=True, comment='产品分类ID')
    prod_cat = Column(String(50), nullable=True, index=True, comment='产品分类名称')
    prod_pcatid = Column(Integer, nullable=True, comment='产品父分类ID')
    prod_pcat = Column(String(50), nullable=True, comment='产品父分类名称')
    
    # 价格信息
    low_price = Column(Float, nullable=True, comment='最低价格')
    high_price = Column(Float, nullable=True, comment='最高价格')
    avg_price = Column(Float, nullable=True, index=True, comment='平均价格')
    
    # 产品详情
    place = Column(String(100), nullable=True, comment='产地')
    spec_info = Column(String(200), nullable=True, comment='规格信息')
    unit_info = Column(String(20), nullable=True, comment='单位信息')
    
    # 时间信息
    pub_date = Column(DateTime, nullable=True, index=True, comment='发布日期')
    
    # 系统信息
    status = Column(Integer, nullable=True, comment='状态')
    user_id_create = Column(Integer, nullable=True, comment='创建用户ID')
    user_id_modified = Column(Integer, nullable=True, comment='修改用户ID')
    user_create = Column(String(50), nullable=True, comment='创建用户')
    user_modified = Column(String(50), nullable=True, comment='修改用户')
    gmt_create = Column(DateTime, nullable=True, comment='创建时间')
    gmt_modified = Column(DateTime, nullable=True, comment='修改时间')
    
    # 本地系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment='本地创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='本地更新时间')
    
    # 唯一约束：所有业务字段（排除系统字段）
    __table_args__ = (
        UniqueConstraint(
            'prod_name', 'prod_catid', 'prod_cat', 'prod_pcatid', 'prod_pcat',
            'low_price', 'high_price', 'avg_price', 'place', 'spec_info', 'unit_info',
            'pub_date', 'status',
            name='uq_all_business_fields'
        ),
    )
    
    def __repr__(self):
        return f"<PriceData(id={self.id}, prod_name='{self.prod_name}', avg_price={self.avg_price})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'prod_name': self.prod_name,
            'prod_catid': self.prod_catid,
            'prod_cat': self.prod_cat,
            'prod_pcatid': self.prod_pcatid,
            'prod_pcat': self.prod_pcat,
            'low_price': self.low_price,
            'high_price': self.high_price,
            'avg_price': self.avg_price,
            'place': self.place,
            'spec_info': self.spec_info,
            'unit_info': self.unit_info,
            'pub_date': self.pub_date.isoformat() if self.pub_date else None,
            'status': self.status,
            'user_id_create': self.user_id_create,
            'user_id_modified': self.user_id_modified,
            'user_create': self.user_create,
            'user_modified': self.user_modified,
            'gmt_create': self.gmt_create.isoformat() if self.gmt_create else None,
            'gmt_modified': self.gmt_modified.isoformat() if self.gmt_modified else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ScrapingLog(Base):
    """抓取日志模型"""
    __tablename__ = 'scraping_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_date = Column(DateTime, default=datetime.utcnow, index=True, comment='抓取时间')
    total_records = Column(Integer, nullable=False, comment='总记录数')
    new_records = Column(Integer, nullable=False, comment='新增记录数')
    updated_records = Column(Integer, nullable=False, comment='更新记录数')
    status = Column(String(20), nullable=False, comment='抓取状态')
    error_message = Column(Text, nullable=True, comment='错误信息')
    
    def __repr__(self):
        return f"<ScrapingLog(id={self.id}, scrape_date={self.scrape_date}, status='{self.status}')>"

# 数据库引擎和会话
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()