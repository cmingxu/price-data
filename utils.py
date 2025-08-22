#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块

包含:
- 日志配置
- 错误处理
- 数据验证
- 通用工具函数
"""

import os
import sys
import traceback
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from functools import wraps
from loguru import logger

from config import Config

def setup_logging(log_level: str = Config.LOG_LEVEL, log_dir: str = "logs"):
    """配置日志系统
    
    Args:
        log_level: 日志级别
        log_dir: 日志目录
    """
    
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件输出 - 应用日志
    logger.add(
        os.path.join(log_dir, "app_{time:YYYY-MM-DD}.log"),
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    # 文件输出 - 错误日志
    logger.add(
        os.path.join(log_dir, "error_{time:YYYY-MM-DD}.log"),
        rotation="1 day",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        encoding="utf-8"
    )
    
    # 文件输出 - 数据抓取日志
    logger.add(
        os.path.join(log_dir, "scraping_{time:YYYY-MM-DD}.log"),
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: "scraping" in record["extra"],
        encoding="utf-8"
    )
    
    logger.info(f"日志系统初始化完成，级别: {log_level}")

def log_execution_time(func):
    """记录函数执行时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        func_name = f"{func.__module__}.{func.__name__}"
        
        try:
            logger.debug(f"开始执行 {func_name}")
            result = func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"完成执行 {func_name}，耗时: {duration:.3f}秒")
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"执行 {func_name} 失败，耗时: {duration:.3f}秒，错误: {e}")
            raise
    
    return wrapper

def handle_exceptions(default_return=None, log_error=True):
    """异常处理装饰器
    
    Args:
        default_return: 异常时的默认返回值
        log_error: 是否记录错误日志
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"函数 {func.__name__} 执行异常: {e}")
                    logger.debug(f"异常详情: {traceback.format_exc()}")
                
                return default_return
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """失败重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间倍数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 第 {attempt + 1} 次执行失败: {e}，"
                            f"{current_delay:.1f}秒后重试"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"函数 {func.__name__} 执行失败，已达到最大重试次数 {max_retries}"
                        )
            
            raise last_exception
        return wrapper
    return decorator

class ValidationError(Exception):
    """数据验证异常"""
    pass

def validate_price_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证价格数据
    
    Args:
        data: 价格数据字典
        
    Returns:
        验证后的数据
        
    Raises:
        ValidationError: 数据验证失败
    """
    
    required_fields = [
        'prod_name', 'prod_catid', 'prod_cat', 'prod_pcatid', 'prod_pcat',
        'low_price', 'high_price', 'avg_price', 'pub_date'
    ]
    
    # 检查必需字段
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValidationError(f"缺少必需字段: {field}")
    
    # 验证产品名称
    if not isinstance(data['prod_name'], str) or not data['prod_name'].strip():
        raise ValidationError("产品名称必须是非空字符串")
    
    # 验证分类ID
    try:
        data['prod_catid'] = int(data['prod_catid'])
        data['prod_pcatid'] = int(data['prod_pcatid'])
    except (ValueError, TypeError):
        raise ValidationError("分类ID必须是整数")
    
    # 验证价格
    try:
        data['low_price'] = float(data['low_price'])
        data['high_price'] = float(data['high_price'])
        data['avg_price'] = float(data['avg_price'])
        
        if data['low_price'] < 0 or data['high_price'] < 0 or data['avg_price'] < 0:
            raise ValidationError("价格不能为负数")
        
        if data['low_price'] > data['high_price']:
            raise ValidationError("最低价格不能大于最高价格")
        
        if not (data['low_price'] <= data['avg_price'] <= data['high_price']):
            raise ValidationError("平均价格应在最低价格和最高价格之间")
            
    except (ValueError, TypeError):
        raise ValidationError("价格必须是数字")
    
    # 验证日期
    if isinstance(data['pub_date'], str):
        try:
            # 尝试解析日期字符串
            if 'T' in data['pub_date'] or ' ' in data['pub_date']:
                # 包含时间的格式
                data['pub_date'] = datetime.fromisoformat(data['pub_date'].replace('Z', '+00:00'))
            else:
                # 只有日期的格式
                data['pub_date'] = datetime.strptime(data['pub_date'], '%Y-%m-%d')
        except ValueError:
            raise ValidationError("日期格式无效")
    elif not isinstance(data['pub_date'], (datetime, date)):
        raise ValidationError("发布日期必须是日期或日期时间对象")
    
    # 清理可选字段
    optional_fields = ['place', 'spec_info', 'unit_info']
    for field in optional_fields:
        if field in data and data[field] is not None:
            data[field] = str(data[field]).strip() or None
    
    return data

def safe_convert_to_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的浮点数
    """
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"无法将 {value} 转换为浮点数，使用默认值 {default}")
        return default

def safe_convert_to_int(value: Any, default: int = 0) -> int:
    """安全转换为整数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的整数
    """
    try:
        if value is None or value == '':
            return default
        return int(float(value))  # 先转为float再转为int，处理"1.0"这样的字符串
    except (ValueError, TypeError):
        logger.warning(f"无法将 {value} 转换为整数，使用默认值 {default}")
        return default

def format_datetime(dt: Union[datetime, date, str, None], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        格式化后的字符串
    """
    if dt is None:
        return None
    
    try:
        if isinstance(dt, str):
            # 尝试解析字符串
            if 'T' in dt or ' ' in dt:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(dt, '%Y-%m-%d')
        elif isinstance(dt, date) and not isinstance(dt, datetime):
            dt = datetime.combine(dt, datetime.min.time())
        
        return dt.strftime(format_str)
    except (ValueError, AttributeError) as e:
        logger.warning(f"日期格式化失败: {e}")
        return str(dt)

def clean_string(value: Any, max_length: Optional[int] = None) -> Optional[str]:
    """清理字符串
    
    Args:
        value: 要清理的值
        max_length: 最大长度限制
        
    Returns:
        清理后的字符串
    """
    if value is None:
        return None
    
    # 转换为字符串并去除首尾空白
    cleaned = str(value).strip()
    
    if not cleaned:
        return None
    
    # 限制长度
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length].strip()
        logger.debug(f"字符串被截断到 {max_length} 个字符")
    
    return cleaned

def calculate_statistics(values: List[Union[int, float]]) -> Dict[str, float]:
    """计算统计信息
    
    Args:
        values: 数值列表
        
    Returns:
        统计信息字典
    """
    if not values:
        return {
            'count': 0,
            'sum': 0.0,
            'mean': 0.0,
            'min': 0.0,
            'max': 0.0,
            'median': 0.0
        }
    
    values = [float(v) for v in values if v is not None]
    
    if not values:
        return {
            'count': 0,
            'sum': 0.0,
            'mean': 0.0,
            'min': 0.0,
            'max': 0.0,
            'median': 0.0
        }
    
    sorted_values = sorted(values)
    count = len(values)
    
    # 计算中位数
    if count % 2 == 0:
        median = (sorted_values[count // 2 - 1] + sorted_values[count // 2]) / 2
    else:
        median = sorted_values[count // 2]
    
    return {
        'count': count,
        'sum': sum(values),
        'mean': sum(values) / count,
        'min': min(values),
        'max': max(values),
        'median': median
    }

def create_response(success: bool = True, 
                   message: str = "", 
                   data: Any = None, 
                   error: str = "",
                   **kwargs) -> Dict[str, Any]:
    """创建标准响应格式
    
    Args:
        success: 是否成功
        message: 消息
        data: 数据
        error: 错误信息
        **kwargs: 其他字段
        
    Returns:
        响应字典
    """
    response = {
        'success': success,
        'timestamp': datetime.now().isoformat(),
        **kwargs
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return response

def get_file_size(file_path: str) -> int:
    """获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def ensure_directory(dir_path: str) -> bool:
    """确保目录存在
    
    Args:
        dir_path: 目录路径
        
    Returns:
        是否成功创建或已存在
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"创建目录失败 {dir_path}: {e}")
        return False

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total: int, description: str = "处理中"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
        self.last_log_time = self.start_time
        self.log_interval = 10  # 每10秒记录一次进度
    
    def update(self, increment: int = 1):
        """更新进度"""
        self.current += increment
        
        now = datetime.now()
        if (now - self.last_log_time).total_seconds() >= self.log_interval:
            self.log_progress()
            self.last_log_time = now
    
    def log_progress(self):
        """记录进度"""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            if self.current > 0:
                eta = (elapsed / self.current) * (self.total - self.current)
                eta_str = f"，预计剩余: {eta:.0f}秒"
            else:
                eta_str = ""
            
            logger.bind(scraping=True).info(
                f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)，"
                f"已用时: {elapsed:.0f}秒{eta_str}"
            )
        else:
            logger.bind(scraping=True).info(f"{self.description}: {self.current} 项已处理")
    
    def finish(self):
        """完成进度跟踪"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.bind(scraping=True).info(
            f"{self.description}完成: {self.current}/{self.total}，总用时: {elapsed:.0f}秒"
        )