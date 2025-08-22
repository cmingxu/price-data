import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { PriceChangeData, formatPriceChange } from '../../lib/api';
import { DATA_PAGE_DURATION } from '../../../types/constants';

interface DataPageProps {
  data: PriceChangeData[];
  pageNumber: number;
  totalPages: number;
}

export const DataPage: React.FC<DataPageProps> = ({ data, pageNumber, totalPages }) => {
  const frame = useCurrentFrame();
  
  // 页面淡入淡出动画
  const pageOpacity = interpolate(
    frame,
    [0, 20, DATA_PAGE_DURATION - 20, DATA_PAGE_DURATION],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // 表格行动画（逐行出现）
  const getRowOpacity = (index: number) => {
    return interpolate(
      frame,
      [10 + index * 2, 20 + index * 2],
      [0, 1],
      {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      }
    );
  };
  
  const getRowTransform = (index: number) => {
    const translateY = interpolate(
      frame,
      [10 + index * 2, 20 + index * 2],
      [30, 0],
      {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      }
    );
    return `translateY(${translateY}px)`;
  };
  
  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
        padding: '40px 30px',
        fontFamily: '"Noto Sans CJK SC", "WenQuanYi Zen Hei", system-ui, -apple-system, sans-serif',
        opacity: pageOpacity,
      }}
    >
      {/* 页面标题 - 移动端优化 */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          marginBottom: '40px',
          textAlign: 'center',
        }}
      >
        <h2
          style={{
            fontSize: '48px',
            fontWeight: 'bold',
            background: 'linear-gradient(45deg, #4a90e2, #357abd, #2b6cb0)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            margin: '0 0 15px 0',
            lineHeight: '1.2',
            transform: `scale(${interpolate(
              frame,
              [0, 30],
              [0.9, 1],
              {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }
            )})`,
            textShadow: '0 4px 8px rgba(74, 144, 226, 0.3)',
          }}
        >
          农产品价格行情
        </h2>
        <div
          style={{
            fontSize: '24px',
            color: '#4a5568',
            background: 'rgba(255, 255, 255, 0.8)',
            padding: '8px 16px',
            borderRadius: '15px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          }}
        >
          {pageNumber} / {totalPages}
        </div>
      </div>
      
      {/* 表格容器 */}
      <div
        style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
        }}
      >
        {/* 表格头部 - 移动端优化 */}
        <div
          style={{
            display: 'flex',
            background: 'linear-gradient(90deg, #4a90e2, #357abd)',
            color: 'white',
            fontSize: '32px',
          fontWeight: 'bold',
          padding: '20px 0',
          }}
        >
          <div style={{ flex: '2', textAlign: 'center' }}>产品名称</div>
          <div style={{ flex: '1.5', textAlign: 'center' }}>平均价格</div>
          <div style={{ flex: '1.5', textAlign: 'center' }}>昨日变化</div>
          <div style={{ flex: '1.5', textAlign: 'center' }}>7日变化</div>
        </div>
        
        {/* 表格数据行 */}
        {data.map((item, index) => (
          <div
            key={`${item.prod_name}-${index}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '20px 20px',
              borderBottom: index < data.length - 1 ? '2px solid #e2e8f0' : 'none',
              backgroundColor: index % 2 === 0 ? '#f8fafc' : 'white',
              opacity: getRowOpacity(index),
              transform: getRowTransform(index),
            }}
          >
            {/* 产品名称 - 移动端优化 */}
            <div
              style={{
                flex: '2',
                fontSize: '30px',
                fontWeight: '700',
                color: '#2d3748',
                textAlign: 'center',
              }}
            >
              {item.prod_name}
            </div>
            
            {/* 平均价格 - 移动端优化 */}
            <div
              style={{
                flex: '1.5',
                fontSize: '30px',
                fontWeight: '600',
                color: '#2b6cb0',
                textAlign: 'center',
              }}
            >
              ¥{item.avg_price.toFixed(2)}{item.unit_info ? `/${item.unit_info}` : ''}
            </div>
            
            {/* 昨日变化 - 移动端优化 */}
            <div
              style={{
                flex: '1.5',
                fontSize: '30px',
                fontWeight: '600',
                textAlign: 'center',
                color: item.change_1d !== undefined 
                  ? (item.change_1d > 0 ? '#38a169' : item.change_1d < 0 ? '#e53e3e' : '#4a5568')
                  : '#4a5568',
              }}
            >
              {formatPriceChange(item.change_1d)}
            </div>
            
            {/* 7日变化 - 移动端优化 */}
            <div
              style={{
                flex: '1.5',
                fontSize: '30px',
                fontWeight: '600',
                textAlign: 'center',
                color: item.change_7d !== undefined 
                  ? (item.change_7d > 0 ? '#38a169' : item.change_7d < 0 ? '#e53e3e' : '#4a5568')
                  : '#4a5568',
              }}
            >
              {formatPriceChange(item.change_7d)}
            </div>
          </div>
        ))}
      </div>
      
      {/* 底部装饰 */}
      <div
        style={{
          position: 'absolute',
          bottom: '40px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '12px',
        }}
      >
        {Array.from({ length: totalPages }, (_, i) => (
          <div
            key={i}
            style={{
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: i + 1 === pageNumber ? '#4a90e2' : '#cbd5e0',
              transition: 'all 0.3s ease',
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};