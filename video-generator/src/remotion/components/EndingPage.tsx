import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { ENDING_DURATION } from '../../../types/constants';

export const EndingPage: React.FC = () => {
  const frame = useCurrentFrame();
  
  // Logo淡入动画
  const logoOpacity = interpolate(
    frame,
    [0, 30, ENDING_DURATION - 30, ENDING_DURATION],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // Logo缩放动画
  const logoScale = interpolate(
    frame,
    [0, 40],
    [0.5, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // 文字淡入动画（稍微延迟）
  const textOpacity = interpolate(
    frame,
    [20, 50, ENDING_DURATION - 30, ENDING_DURATION],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // 装饰元素旋转动画
  const decorRotation = interpolate(
    frame,
    [0, ENDING_DURATION],
    [0, 360],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: '"Noto Sans CJK SC", "WenQuanYi Zen Hei", system-ui, -apple-system, sans-serif',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* 背景装饰元素 - 移动端优化 */}
      <div
        style={{
          position: 'absolute',
          top: '15%',
          left: '15%',
          width: '60px',
          height: '60px',
          border: '2px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '50%',
          transform: `rotate(${decorRotation}deg)`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          right: '20%',
          width: '50px',
          height: '50px',
          border: '2px solid rgba(255, 255, 255, 0.15)',
          borderRadius: '50%',
          transform: `rotate(${-decorRotation}deg)`,
        }}
      />
      
      {/* Logo容器 */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          opacity: logoOpacity,
          transform: `scale(${logoScale})`,
        }}
      >
        {/* 简单的Logo设计 - 移动端优化 */}
        <div
          style={{
            width: '120px',
            height: '120px',
            background: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
            marginBottom: '30px',
            position: 'relative',
          }}
        >
          {/* Logo内部设计 - 移动端优化 */}
          <div
            style={{
              width: '80px',
              height: '80px',
              background: 'white',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '32px',
              fontWeight: 'bold',
              color: '#667eea',
            }}
          >
            数
          </div>
          
          {/* Logo装饰圆环 - 移动端优化 */}
          <div
            style={{
              position: 'absolute',
              width: '100px',
              height: '100px',
              border: '3px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '50%',
              borderTop: '3px solid white',
              transform: `rotate(${decorRotation * 2}deg)`,
            }}
          />
        </div>
      </div>
      
      {/* 公司名称 - 移动端优化 */}
      <h1
        style={{
          fontSize: '48px',
          fontWeight: 'bold',
          color: 'white',
          textAlign: 'center',
          margin: '20px 0',
          opacity: textOpacity,
          textShadow: '0 4px 8px rgba(0, 0, 0, 0.3)',
          letterSpacing: '0.1em',
        }}
      >
        怀儒数据
      </h1>
      
      {/* 副标题 - 移动端优化 */}
      <p
        style={{
          fontSize: '24px',
          color: 'rgba(255, 255, 255, 0.9)',
          textAlign: 'center',
          margin: 0,
          opacity: textOpacity,
          fontWeight: '300',
          lineHeight: '1.4',
        }}
      >
        专业数据服务提供商
      </p>
      
      {/* 底部装饰线 */}
      <div
        style={{
          position: 'absolute',
          bottom: '80px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '400px',
          height: '2px',
          background: 'linear-gradient(90deg, transparent, white, transparent)',
          opacity: textOpacity,
        }}
      />
      
      {/* 闪烁效果 */}
      <div
        style={{
          position: 'absolute',
          top: '30%',
          right: '15%',
          width: '4px',
          height: '4px',
          background: 'white',
          borderRadius: '50%',
          opacity: interpolate(
            frame,
            [0, 15, 30, 45, 60],
            [0, 1, 0, 1, 0],
            {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'extend',
            }
          ),
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '40%',
          left: '10%',
          width: '3px',
          height: '3px',
          background: 'rgba(255, 255, 255, 0.8)',
          borderRadius: '50%',
          opacity: interpolate(
            frame,
            [10, 25, 40, 55, 70],
            [0, 1, 0, 1, 0],
            {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'extend',
            }
          ),
        }}
      />
    </AbsoluteFill>
  );
};