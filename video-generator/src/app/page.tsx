"use client";

import { Player } from "@remotion/player";
import type { NextPage } from "next";
import React, { useMemo, useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { z } from "zod";
import {
  defaultMyCompProps,
  CompositionProps,
  VIDEO_FPS,
  VIDEO_HEIGHT,
  VIDEO_WIDTH,
} from "../../types/constants";
import { RenderControls } from "../components/RenderControls";
import { Spacing } from "../components/Spacing";
import { Tips } from "../components/Tips";
import { PriceVideo } from "../remotion/PriceVideo";
import { calculateVideoDuration } from "../utils/video-duration";
import { PriceChangeData, fetchPriceData } from "../lib/api";



const Home: NextPage = () => {
  const searchParams = useSearchParams();
  
  // 从URL参数获取日期和分类，设置默认值
  const currentDate = searchParams.get('date') || new Date().toISOString().split('T')[0];
  const category = searchParams.get('category') || '蔬菜';
  
  const [text, setText] = useState<string>(defaultMyCompProps.title);
  const [priceData, setPriceData] = useState<PriceChangeData[]>([]);
  const [loading, setLoading] = useState(true);

  // 获取真实价格数据
  useEffect(() => {
    const loadPriceData = async () => {
      try {
        setLoading(true);
        const data = await fetchPriceData(currentDate, category);
        setPriceData(data);
        // 根据参数更新标题
        setText(`${currentDate} ${category}价格`);
      } catch (error) {
        console.error('Failed to load price data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPriceData();
  }, [currentDate, category]);

  // 转换数据格式给CompositionProps使用
  const inputProps: z.infer<typeof CompositionProps> = useMemo(() => {
    const compositionData = priceData.map((item, index) => ({
      id: index + 1,
      prod_name: item.prod_name,
      avg_price: item.avg_price,
      pub_date: new Date().toISOString().split('T')[0],
      prod_pcatid: 1000 + index,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      price_change_1d: item.change_1d,
      price_change_7d: item.change_7d,
    }));
    
    return {
      title: text,
      priceData: compositionData,
    };
  }, [text, priceData]);

  // PriceVideo组件使用的数据格式
  const priceVideoProps = useMemo(() => {
    return {
      title: text,
      priceData: priceData,
    };
  }, [text, priceData]);

  const videoDuration = calculateVideoDuration(priceData.length);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px'
      }}>
        正在加载价格数据...
      </div>
    );
  }

  return (
    <div>
      <div className="max-w-screen-md m-auto mb-5">
        <div className="overflow-hidden rounded-geist shadow-[0_0_200px_rgba(0,0,0,0.15)] mb-10 mt-16">
          <Player
            component={PriceVideo}
            inputProps={priceVideoProps}
            durationInFrames={videoDuration}
            fps={VIDEO_FPS}
            compositionHeight={VIDEO_HEIGHT}
            compositionWidth={VIDEO_WIDTH}
            style={{
              // Can't use tailwind class for width since player's default styles take presedence over tailwind's,
              // but not over inline styles
              width: "100%",
            }}
            controls
            autoPlay
            loop
          />
        </div>
        <RenderControls
          text={text}
          setText={setText}
          inputProps={inputProps}
        ></RenderControls>
        <Spacing></Spacing>
        <Spacing></Spacing>
        <Spacing></Spacing>
        <Spacing></Spacing>
        <Tips></Tips>
      </div>
    </div>
  );
};

const HomePage: NextPage = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Home />
    </Suspense>
  );
};

export default HomePage;
