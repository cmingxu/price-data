'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { useSearchParams } from 'next/navigation';
import { fetchPriceData, PriceChangeData } from '../../lib/api';
import { calculateVideoDuration } from '../../utils/video-duration';
import { VIDEO_FPS } from '../../../types/constants';

function GenerateVideoPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [priceData, setPriceData] = useState<PriceChangeData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>(
    searchParams.get('date') || new Date().toISOString().split('T')[0]
  );
  const [selectedCategory, setSelectedCategory] = useState<string>(
    searchParams.get('category') || '蔬菜'
  );

  // 有效的分类选项
  const categories = [
    { value: '', label: '全部分类' },
    { value: '肉禽蛋', label: '肉禽蛋' },
    { value: '水果', label: '水果' },
    { value: '蔬菜', label: '蔬菜' },
    { value: '水产', label: '水产' }
  ];

  // 获取价格数据
  const loadPriceData = async (date?: string, category?: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchPriceData(date, category);
      setPriceData(data);
      
      if (date && data.length === 0) {
        setError(`没有找到 ${date} 的价格数据`);
      }
      if (category && data.length === 0) {
        setError(`没有找到 ${category} 分类的价格数据`);
      }
    } catch (err) {
      setError('获取价格数据失败');
      console.error('Error loading price data:', err);
    } finally {
      setLoading(false);
    }
  };

  // 处理日期选择
  const handleDateChange = (date: string) => {
    setSelectedDate(date);
    loadPriceData(date, selectedCategory);
  };

  // 处理分类选择
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    loadPriceData(selectedDate, category);
  };

  // 跳转到指定日期页面
  const navigateToDatePage = () => {
    if (selectedDate) {
      router.push(`/generate/${selectedDate}`);
    }
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
          title: selectedDate 
            ? `${selectedDate} ${selectedCategory || '农产品'}价格` 
            : `今日${selectedCategory || '农产品'}价格`,
          targetDate: selectedDate,
          category: selectedCategory,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setSuccess(`视频生成成功! 文件路径: ${result.outputPath}`);
    } catch (err) {
      setError('视频生成失败: ' + (err as Error).message);
    } finally {
      setGenerating(false);
    }
  };

  // 页面加载时自动获取数据
  useEffect(() => {
    loadPriceData(selectedDate, selectedCategory);
  }, []);

  const videoDuration = priceData.length > 0 ? Math.round(calculateVideoDuration(priceData.length) / VIDEO_FPS) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            农产品价格视频生成器
          </h1>
          <p className="text-xl text-gray-600">
            基于实时价格数据生成专业的价格行情视频
          </p>
        </div>

        {/* 数据概览卡片 */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">视频生成设置</h2>
          
          <div className="mb-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择分类
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => handleCategoryChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-full md:w-auto"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择日期 (可选，留空则使用最新数据)
              </label>
              <div className="flex gap-4 items-center">
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => handleDateChange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {selectedDate && (
                  <button
                    onClick={navigateToDatePage}
                    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    跳转到专用页面
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-blue-600">{priceData.length}</div>
              <div className="text-sm text-gray-600">产品数量</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-green-600">{videoDuration}s</div>
              <div className="text-sm text-gray-600">预计时长</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-purple-600">
                {selectedCategory || '全部'}
              </div>
              <div className="text-sm text-gray-600">产品分类</div>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => loadPriceData(selectedDate, selectedCategory)}
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {loading ? '加载中...' : '刷新数据'}
            </button>
            
            <button
              onClick={generateVideo}
              disabled={generating || priceData.length === 0}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {generating ? '生成中...' : '生成视频'}
            </button>
          </div>
        </div>

        {/* 错误提示 */}
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

        {/* 成功提示 */}
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

        {/* 价格数据表格 */}
        {priceData.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">价格数据预览</h2>
            
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
                  {priceData.slice(0, 10).map((item) => (
                    <tr key={item.prod_name}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.prod_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ¥{item.avg_price.toFixed(2)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                        item.change_1d !== undefined
                          ? item.change_1d > 0
                            ? 'text-green-600'
                            : item.change_1d < 0
                            ? 'text-red-600'
                            : 'text-gray-500'
                          : 'text-gray-500'
                      }`}>
                        {item.change_1d !== undefined
                          ? `${item.change_1d > 0 ? '+' : ''}${item.change_1d.toFixed(1)}%`
                          : '--'}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                        item.change_7d !== undefined
                          ? item.change_7d > 0
                            ? 'text-green-600'
                            : item.change_7d < 0
                            ? 'text-red-600'
                            : 'text-gray-500'
                          : 'text-gray-500'
                      }`}>
                        {item.change_7d !== undefined
                          ? `${item.change_7d > 0 ? '+' : ''}${item.change_7d.toFixed(1)}%`
                          : '--'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {priceData.length > 10 && (
                <div className="mt-4 text-center text-gray-500">
                  还有 {priceData.length - 10} 条数据...
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function GenerateVideoPageWithSuspense() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <GenerateVideoPage />
    </Suspense>
  );
}