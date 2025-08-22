'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { fetchPriceData, PriceChangeData, formatPriceChange, getPriceChangeColor } from '../../../lib/api';
import { calculateVideoDuration } from '../../../utils/video-duration';

export default function GenerateVideoPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const date = params.date as string;
  const initialCategory = searchParams.get('category') || '';
  
  const [priceData, setPriceData] = useState<PriceChangeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);

  // 有效的分类选项
  const categories = [
    { value: '', label: '全部分类' },
    { value: '肉禽蛋', label: '肉禽蛋' },
    { value: '水果', label: '水果' },
    { value: '蔬菜', label: '蔬菜' },
    { value: '水产', label: '水产' }
  ];

  // 验证日期格式
  const isValidDate = (dateString: string): boolean => {
    const regex = /^\d{4}-\d{2}-\d{2}$/;
    if (!regex.test(dateString)) return false;
    
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date.getTime());
  };

  // 获取价格数据
  const loadPriceData = async (category?: string) => {
    if (!isValidDate(date)) {
      setError('无效的日期格式，请使用 YYYY-MM-DD 格式');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchPriceData(date, category || selectedCategory);
      setPriceData(data);
      
      if (data.length === 0) {
        const categoryText = category || selectedCategory;
        setError(`没有找到 ${date} ${categoryText ? `${categoryText}分类` : ''}的价格数据`);
      }
    } catch (err) {
      setError('获取价格数据失败');
      console.error('Error loading price data:', err);
    } finally {
      setLoading(false);
    }
  };

  // 处理分类选择
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    loadPriceData(category);
  };

  // 生成视频
  const generateVideo = async () => {
    setGenerating(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: `${date} ${selectedCategory || '农产品'}价格`,
          targetDate: date,
          category: selectedCategory,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setSuccess(`视频生成成功！文件保存为: ${result.filename}`);
    } catch (err) {
      setError('视频生成失败');
      console.error('Error generating video:', err);
    } finally {
      setGenerating(false);
    }
  };

  // 页面加载时获取数据
  useEffect(() => {
    if (date) {
      loadPriceData();
    }
  }, [date]);

  const videoDuration = priceData.length > 0 ? calculateVideoDuration(priceData.length) : 0;
  const videoDurationSeconds = Math.round(videoDuration / 30); // 假设30fps

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            农产品价格视频生成器
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            为 <span className="font-semibold text-indigo-600">{date}</span> {selectedCategory && <span className="font-semibold text-purple-600">{selectedCategory}分类</span>} 生成价格视频
          </p>

          {/* 分类选择 */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">视频生成设置</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择分类
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => handleCategoryChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 w-full md:w-auto"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 数据概览 */}
          {priceData.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">数据概览</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-indigo-600">{priceData.length}</div>
                  <div className="text-sm text-gray-600">产品数量</div>
                </div>
                <div className="bg-white rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">{videoDurationSeconds}s</div>
                  <div className="text-sm text-gray-600">预计视频时长</div>
                </div>
                <div className="bg-white rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {selectedCategory || '全部'}
                  </div>
                  <div className="text-sm text-gray-600">产品分类</div>
                </div>
              </div>
            </div>
          )}

          {/* 错误信息 */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex">
                <div className="text-red-600">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* 成功信息 */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex">
                <div className="text-green-600">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-green-800">{success}</p>
                </div>
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <button
              onClick={() => loadPriceData()}
              disabled={loading}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
            >
              {loading ? '加载中...' : '重新加载数据'}
            </button>
            
            <button
              onClick={generateVideo}
              disabled={generating || priceData.length === 0}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200"
            >
              {generating ? '生成中...' : '生成视频'}
            </button>
          </div>

          {/* 价格数据预览表格 */}
          {priceData.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800">价格数据预览</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        产品名称
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        平均价格
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        昨日变化
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        7日变化
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {priceData.slice(0, 10).map((item, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {item.prod_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ¥{item.avg_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`font-medium ${getPriceChangeColor(item.change_1d)}`}>
                            {formatPriceChange(item.change_1d)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`font-medium ${getPriceChangeColor(item.change_7d)}`}>
                            {formatPriceChange(item.change_7d)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {priceData.length > 10 && (
                  <div className="px-6 py-3 bg-gray-50 text-sm text-gray-500 text-center">
                    显示前10条，共{priceData.length}条数据
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}