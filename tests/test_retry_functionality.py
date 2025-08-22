#!/usr/bin/env python3
"""
测试重试功能的脚本
"""

import unittest
from unittest.mock import patch, Mock
import requests
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import XinfadiScraper
from config import Config

class TestRetryFunctionality(unittest.TestCase):
    """测试重试功能"""
    
    def setUp(self):
        self.scraper = XinfadiScraper()
    
    def tearDown(self):
        self.scraper.close()
    
    @patch('scraper.time.sleep')  # Mock sleep to speed up tests
    @patch('requests.Session.post')
    def test_retry_on_connection_error(self, mock_post, mock_sleep):
        """测试连接错误时的重试机制"""
        # 模拟前4次连接失败，第5次成功
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'list': [{'test': 'data'}], 'count': 1}
        
        mock_post.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            mock_response  # 第5次成功
        ]
        
        # 执行请求
        result = self.scraper._make_request({'test': 'data'})
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result['list'][0]['test'], 'data')
        
        # 验证重试了5次
        self.assertEqual(mock_post.call_count, 5)
        
        # 验证sleep被调用了4次（前4次失败后都会sleep）
        self.assertEqual(mock_sleep.call_count, 4)
        
        # 验证每次sleep的时间都是配置的间隔
        for call in mock_sleep.call_args_list:
            self.assertEqual(call[0][0], Config.RETRY_INTERVAL)
    
    @patch('scraper.time.sleep')
    @patch('requests.Session.post')
    def test_retry_on_timeout_error(self, mock_post, mock_sleep):
        """测试超时错误时的重试机制"""
        # 模拟前3次超时，第4次成功
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'list': [], 'count': 0}
        
        mock_post.side_effect = [
            requests.exceptions.Timeout("Request timeout"),
            requests.exceptions.Timeout("Request timeout"),
            requests.exceptions.Timeout("Request timeout"),
            mock_response  # 第4次成功
        ]
        
        result = self.scraper._make_request({'test': 'data'})
        
        self.assertIsNotNone(result)
        self.assertEqual(mock_post.call_count, 4)
        self.assertEqual(mock_sleep.call_count, 3)
    
    @patch('scraper.time.sleep')
    @patch('requests.Session.post')
    def test_max_retries_exceeded(self, mock_post, mock_sleep):
        """测试超过最大重试次数后返回None"""
        # 模拟所有5次尝试都失败
        mock_post.side_effect = [
            requests.exceptions.ConnectionError("Connection failed")
        ] * Config.RETRY_MAX_ATTEMPTS
        
        result = self.scraper._make_request({'test': 'data'})
        
        # 验证返回None
        self.assertIsNone(result)
        
        # 验证尝试了最大次数
        self.assertEqual(mock_post.call_count, Config.RETRY_MAX_ATTEMPTS)
        
        # 验证sleep被调用了4次（最后一次失败后不会sleep）
        self.assertEqual(mock_sleep.call_count, Config.RETRY_MAX_ATTEMPTS - 1)
    
    @patch('requests.Session.post')
    def test_no_retry_on_json_decode_error(self, mock_post):
        """测试JSON解析错误时不重试"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        mock_post.return_value = mock_response
        
        result = self.scraper._make_request({'test': 'data'})
        
        # 验证返回None
        self.assertIsNone(result)
        
        # 验证只调用了一次（没有重试）
        self.assertEqual(mock_post.call_count, 1)
    
    @patch('requests.Session.post')
    def test_first_attempt_success(self, mock_post):
        """测试第一次尝试就成功的情况"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'list': [{'success': True}], 'count': 1}
        
        mock_post.return_value = mock_response
        
        result = self.scraper._make_request({'test': 'data'})
        
        # 验证成功返回数据
        self.assertIsNotNone(result)
        self.assertEqual(result['list'][0]['success'], True)
        
        # 验证只调用了一次
        self.assertEqual(mock_post.call_count, 1)

if __name__ == '__main__':
    unittest.main()