#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试价格趋势功能
"""

import requests
import json
from datetime import datetime, timedelta

def test_trending_api():
    """测试价格趋势API"""
    base_url = "http://localhost:8000"
    
    print("=== 测试价格趋势功能 ===")
    
    # 测试不带trending参数的请求
    print("\n1. 测试普通价格查询（不带trending参数）")
    response = requests.get(f"{base_url}/api/prices", params={
        "limit": 3
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回 {len(data)} 条记录")
        if data:
            print(f"第一条记录字段: {list(data[0].keys())}")
            print(f"是否包含trend_data: {'trend_data' in data[0]}")
    else:
        print(f"请求失败: {response.status_code}")
    
    # 测试带trending=false参数的请求
    print("\n2. 测试trending=false")
    response = requests.get(f"{base_url}/api/prices", params={
        "limit": 3,
        "trending": False
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回 {len(data)} 条记录")
        if data:
            print(f"第一条记录字段: {list(data[0].keys())}")
            print(f"是否包含trend_data: {'trend_data' in data[0]}")
    else:
        print(f"请求失败: {response.status_code}")
    
    # 测试带trending=true参数的请求
    print("\n3. 测试trending=true")
    response = requests.get(f"{base_url}/api/prices", params={
        "limit": 3,
        "trending": True
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回 {len(data)} 条记录")
        if data:
            print(f"第一条记录字段: {list(data[0].keys())}")
            print(f"是否包含trend_data: {'trend_data' in data[0]}")
            
            if 'trend_data' in data[0] and data[0]['trend_data']:
                trend_data = data[0]['trend_data']
                print(f"趋势数据字段: {list(trend_data.keys())}")
                print("趋势数据示例:")
                for key, value in trend_data.items():
                    print(f"  {key}: {value}")
            else:
                print("趋势数据为空或不存在")
                
            # 显示完整的第一条记录
            print("\n完整记录示例:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False, default=str))
    else:
        print(f"请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
    
    # 测试特定产品的趋势数据
    print("\n4. 测试特定产品的趋势数据")
    response = requests.get(f"{base_url}/api/prices", params={
        "limit": 1,
        "trending": True,
        "prod_name": "白萝卜"
    })
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"产品: {data[0]['prod_name']}")
            print(f"当前平均价格: {data[0]['avg_price']}")
            print(f"发布日期: {data[0]['pub_date']}")
            
            if data[0]['trend_data']:
                print("价格变化趋势:")
                trend = data[0]['trend_data']
                for period in ['1d', '3d', '7d', '14d', '30d']:
                    change = trend.get(f'change_{period}')
                    percent = trend.get(f'change_{period}_percent')
                    if change is not None:
                        print(f"  {period}: {change:+.2f} ({percent:+.2f}%)")
                    else:
                        print(f"  {period}: 无数据")
            else:
                print("无趋势数据")
        else:
            print("未找到匹配的产品")
    else:
        print(f"请求失败: {response.status_code}")

if __name__ == "__main__":
    test_trending_api()