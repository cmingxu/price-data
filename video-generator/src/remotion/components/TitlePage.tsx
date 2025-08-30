import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { TITLE_DURATION } from '../../../types/constants';

interface TitlePageProps {
  title: string;
}

export const TitlePage: React.FC<TitlePageProps> = ({ title }) => {
  const frame = useCurrentFrame();
  
  // 标题淡入动画
  const titleOpacity = interpolate(
    frame,
    [0, 20, TITLE_DURATION - 20, TITLE_DURATION],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // 标题缩放动画
  const titleScale = interpolate(
    frame,
    [0, 30],
    [0.8, 1],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // 日期淡入动画（稍微延迟）
  const dateOpacity = interpolate(
    frame,
    [10, 30, TITLE_DURATION - 20, TITLE_DURATION],
    [0, 1, 1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  // 获取当前日期
  const currentDate = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });
  
  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: '"Noto Sans CJK SC", "WenQuanYi Zen Hei", system-ui, -apple-system, sans-serif',
      }}
    >
      <div style={{
        position: 'absolute',
        top: '20%',
        left: '50%',
        transform: 'translate(-50%, -50%) skew(-10deg)',
        border: '4px solid #000',
        textAlign: 'center',
        fontSize: '24px',
        color: 'red',
        backgroundColor: 'yellow',
        padding: '30px 42px',
        borderRadius: '12px',
        opacity: 1,
        fontWeight: 'bold',
        fontFamily: 'Arial, sans-serif',
        fontStyle: 'normal',
        fontSize: '6em',
        letterSpacing: '0.1em',
      }}>
        { title }
      </div>
      {/* 装饰性背景元素 - 适配移动端 */}
      <div
        style={{
          position: 'absolute',
          top: '8%',
          left: '15%',
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          background: 'rgba(74, 144, 226, 0.1)',
          opacity: titleOpacity * 0.5,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          right: '20%',
          width: '100px',
          height: '100px',
          borderRadius: '50%',
          background: 'rgba(129, 236, 236, 0.1)',
          opacity: titleOpacity * 0.3,
        }}
      />
      
      {/* 主标题 - 移动端优化 */}
      <h1
        style={{
          fontSize: '80px',
          fontWeight: 'bold',
          background: 'linear-gradient(45deg, #4a90e2, #357abd, #2b6cb0, #81ecec)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          textAlign: 'center',
          margin: 0,
          opacity: titleOpacity,
          transform: `scale(${titleScale}) rotateY(${interpolate(
            frame,
            [0, 60],
            [10, 0],
            {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }
          )}deg)`,
          textShadow: '0 8px 16px rgba(74, 144, 226, 0.4)',
          letterSpacing: '0.05em',
          lineHeight: '1.1',
          maxWidth: '90%',
          filter: `hue-rotate(${interpolate(
            frame,
            [0, TITLE_DURATION],
            [0, 30],
            {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }
          )}deg)`,
        }}
      >
        {title}
      </h1>
      
      {/* 日期 - 移动端优化 */}
      <p
        style={{
          fontSize: '32px',
          background: 'linear-gradient(90deg, #4a5568, #2b6cb0)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          textAlign: 'center',
          margin: '30px 0 0 0',
          opacity: dateOpacity,
          fontWeight: '400',
          maxWidth: '85%',
          transform: `translateY(${interpolate(
            frame,
            [10, 40],
            [20, 0],
            {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }
          )}px)`,
        }}
      >
        {currentDate}
      </p>
      
      {/* 装饰线条 - 移动端优化 */}
      <div
        style={{
          width: '200px',
          height: '3px',
          background: 'linear-gradient(90deg, #4a90e2, #81ecec)',
          marginTop: '40px',
          borderRadius: '2px',
          opacity: dateOpacity,
          transform: `scaleX(${interpolate(
            frame,
            [30, 60],
            [0, 1],
            {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }
          )})`,
        }}
      />
    </AbsoluteFill>
  );
};
