export interface PriceData {
  id: number;
  prod_name: string;
  avg_price: number;
  pub_date: string;
}

export interface PriceTrendData {
  change_1d?: number;
  change_3d?: number;
  change_7d?: number;
  change_14d?: number;
  change_30d?: number;
  change_1d_percent?: number;
  change_3d_percent?: number;
  change_7d_percent?: number;
  change_14d_percent?: number;
  change_30d_percent?: number;
}

export interface PriceDataWithTrend {
  id: number;
  prod_name: string;
  prod_catid?: number;
  prod_cat?: string;
  prod_pcatid?: number;
  prod_pcat?: string;
  low_price?: number;
  high_price?: number;
  avg_price: number;
  place?: string;
  spec_info?: string;
  unit_info?: string;
  pub_date?: string;
  created_at: string;
  updated_at: string;
  trend_data?: PriceTrendData;
}

export interface PriceChangeData {
  prod_name: string;
  avg_price: number;
  change_1d: number;
  change_7d: number;
  unit_info?: string;
}

/**
 * 获取指定日期和分类的价格数据
 */
export async function fetchPriceData(targetDate?: string, category?: string): Promise<PriceChangeData[]> {
  try {
    let url = '/api/prices?trending=true&limit=1000';
    
    if (targetDate) {
      // 如果指定了日期，获取该日期的数据
      url += `&date_from=${targetDate}&date_to=${targetDate}`;
    }
    
    if (category) {
      // 如果指定了分类，按分类筛选
      url += `&prod_cat=${encodeURIComponent(category)}`;
    }
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data: PriceDataWithTrend[] = await response.json();
    
    // 转换为PriceChangeData格式
    const priceChanges: PriceChangeData[] = data.map((item) => ({
      prod_name: item.prod_name,
      avg_price: item.avg_price,
      change_1d: item.trend_data?.change_1d || 0,
      change_7d: item.trend_data?.change_7d || 0,
      unit_info: item.unit_info,
    }));
    
    return priceChanges;
  } catch (error) {
    console.error('Error fetching price data:', error);
    return getMockPriceData();
  }
}

/**
 * 模拟价格数据（用作fallback）
 */
function getMockPriceData(): PriceChangeData[] {
  return [
    {
      prod_name: '苹果',
      avg_price: 8.50,
      change_1d: 2.5,
      change_7d: -1.2
    },
    {
      prod_name: '橙子',
      avg_price: 6.80,
      change_1d: -0.8,
      change_7d: 3.1
    },
    {
      prod_name: '香蕉',
      avg_price: 4.20,
      change_1d: 1.5,
      change_7d: -2.3
    },
    {
      prod_name: '西瓜',
      avg_price: 3.60,
      change_1d: 0.0,
      change_7d: 4.2
    },
    {
      prod_name: '葡萄',
      avg_price: 12.30,
      change_1d: -1.2,
      change_7d: 0.8
    }
  ];
}

/**
 * 格式化价格变化显示
 */
export function formatPriceChange(change: number | undefined): string {
  if (change === undefined) return '--';
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(1)}%`;
}

/**
 * 获取价格变化的颜色类名
 */
export function getPriceChangeColor(change: number | undefined): string {
  if (change === undefined) return 'text-gray-500';
  if (change > 0) return 'text-green-500';
  if (change < 0) return 'text-red-500';
  return 'text-gray-500';
}