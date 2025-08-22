import React from "react";
import { Composition } from "remotion";
import { PriceVideo } from "./PriceVideo";
import { calculateVideoDuration } from "../utils/video-duration";
import { PriceChangeData } from "../lib/api";
import {
  COMP_NAME,
  defaultMyCompProps,
  VIDEO_FPS,
  VIDEO_HEIGHT,
  VIDEO_WIDTH,
} from "../../types/constants";

export interface PriceVideoProps {
  title: string;
  priceData: PriceChangeData[];
}

// 模拟数据用于预览
const mockPriceData: PriceChangeData[] = [
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
  },
  {
    prod_name: '梨子',
    avg_price: 5.40,
    change_1d: 3.2,
    change_7d: -0.5
  },
  {
    prod_name: '桃子',
    avg_price: 9.80,
    change_1d: -2.1,
    change_7d: 1.8
  }
];

const videoDuration = calculateVideoDuration(mockPriceData.length);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id={COMP_NAME}
        component={PriceVideo as any}
        durationInFrames={videoDuration}
        fps={VIDEO_FPS}
        width={VIDEO_WIDTH}
        height={VIDEO_HEIGHT}
        defaultProps={{
          title: defaultMyCompProps.title,
          priceData: mockPriceData,
        }}
      />
    </>
  );
};
