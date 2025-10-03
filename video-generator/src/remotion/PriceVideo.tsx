import React, { useMemo } from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from 'remotion';
import { TitlePage } from './components/TitlePage';
import { DataPage } from './components/DataPage';
import { EndingPage } from './components/EndingPage';
import { PriceChangeData } from '../lib/api';
import {
  TITLE_DURATION,
  DATA_PAGE_DURATION,
  ENDING_DURATION,
  ITEMS_PER_PAGE,
} from '../../types/constants';

interface PriceVideoProps {
  title: string;
  priceData: PriceChangeData[];
}

export const PriceVideo: React.FC<PriceVideoProps> = ({ title, priceData }) => {
  const { durationInFrames, fps } = useVideoConfig();
  
  // 将数据分页
  const dataPages = useMemo(() => {
    const pages: PriceChangeData[][] = [];
    for (let i = 0; i < priceData.length; i += ITEMS_PER_PAGE) {
      pages.push(priceData.slice(i, i + ITEMS_PER_PAGE));
    }
    return pages;
  }, [priceData]);
  const totalDataDuration = dataPages.length * DATA_PAGE_DURATION;
  // BGM循环设置 - 假设BGM长度为30秒
  const bgmDurationSeconds = 14;
  const bgmDurationFrames = bgmDurationSeconds * fps;
  const videoDurationSeconds = durationInFrames / fps;
  const loopCount = Math.ceil(videoDurationSeconds / bgmDurationSeconds);
  
  console.log('PriceVideo 渲染: ', {
    title,
    totalItems: priceData.length,
    totalPages: dataPages.length,
    videoDurationSeconds,
    bgmDurationSeconds,
    loopCount,
  });
  
  return (
    <AbsoluteFill>
      {/* 背景音乐 - 循环播放 */}
      {Array.from({ length: loopCount }, (_, index) => (
        <Sequence
          key={index}
          from={index * bgmDurationFrames}
          durationInFrames={Math.min(bgmDurationFrames, durationInFrames - index * bgmDurationFrames)}
        >
          <Audio
            src={staticFile('bgm.mp3')}
            volume={0.2}
          />
        </Sequence>
      ))}
      
      {/* 标题页面 (0-2秒) */}
      <Sequence durationInFrames={TITLE_DURATION}>
        <TitlePage title={title} />
      </Sequence>
      
      {/* 数据页面 (2秒开始，每页5秒) */}
      {dataPages.map((pageData, index) => (
        <Sequence
          key={index}
          from={TITLE_DURATION + index * DATA_PAGE_DURATION}
          durationInFrames={DATA_PAGE_DURATION}
        >
          <DataPage
            title={title}
            data={pageData}
            pageNumber={index + 1}
            totalPages={dataPages.length}
          />
        </Sequence>
      ))}
      
      {/* 结尾页面 (最后3秒) */}
      <Sequence
        from={TITLE_DURATION + totalDataDuration}
        durationInFrames={ENDING_DURATION}
      >
        <EndingPage />
      </Sequence>
    </AbsoluteFill>
  );
};