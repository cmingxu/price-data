import { NextRequest, NextResponse } from 'next/server';
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { join } from 'path';
import { mkdir } from 'fs/promises';
import { calculateVideoDuration } from '../../../utils/video-duration';
import {
  COMP_NAME,
  VIDEO_FPS,
  VIDEO_HEIGHT,
  VIDEO_WIDTH,
} from '../../../../types/constants';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, targetDate, category } = body;

    if (!title) {
      return NextResponse.json(
        { error: '缺少必要参数: title' },
        { status: 400 }
      );
    }

    // Fetch price data internally
    console.log('🔍 正在获取价格数据...');
    const apiURL = process.env.API_URL || "http://localhost:8000";
    let priceDataUrl = `${apiURL}/api/prices?trending=true&limit=1000`;
    
    if (targetDate) {
      priceDataUrl += `&date_from=${targetDate}&date_to=${targetDate}`;
    }
    
    if (category) {
      priceDataUrl += `&prod_cat=${encodeURIComponent(category)}`;
    }

    const priceResponse = await fetch(priceDataUrl);
    if (!priceResponse.ok) {
      throw new Error(`Failed to fetch price data: ${priceResponse.status}`);
    }

    const rawPriceData = await priceResponse.json();
    
    // Transform to PriceChangeData format
    const priceData = rawPriceData.map((item: {
      prod_name: string;
      avg_price: number;
      trend_data?: { change_1d?: number; change_7d?: number };
      unit_info: string;
    }) => ({
      prod_name: item.prod_name,
      avg_price: item.avg_price,
      change_1d: item.trend_data?.change_1d || 0,
      change_7d: item.trend_data?.change_7d || 0,
      unit_info: item.unit_info,
    }));

    if (priceData.length === 0) {
      return NextResponse.json(
        { error: '没有找到符合条件的价格数据' },
        { status: 400 }
      );
    }

    console.log('🚀 开始生成视频...');
    console.log(`📊 价格数据条数: ${priceData.length}`);

    // 计算视频时长
    const durationInFrames = calculateVideoDuration(priceData.length);
    const durationInSeconds = Math.round(durationInFrames / VIDEO_FPS);
    console.log(`⏱️  视频时长: ${durationInSeconds} 秒`);

    // 确保输出目录存在
    const outputDir = join(process.cwd(), 'output', targetDate);
    await mkdir(outputDir, { recursive: true });

    // 打包Remotion项目
    console.log('📦 正在打包项目...');
    const bundleLocation = await bundle({
      entryPoint: join(process.cwd(), 'remotion/index.ts'),
      webpackOverride: (config) => {
        // 添加必要的webpack配置
        config.resolve = config.resolve || {};
        config.resolve.fallback = {
          ...config.resolve.fallback,
          fs: false,
          path: false,
          os: false,
          crypto: false,
          stream: false,
          buffer: false,
          util: false,
        };
        // 忽略可选依赖
        if (!config.externals) {
          config.externals = {};
        }
        if (typeof config.externals === 'object' && !Array.isArray(config.externals)) {
          config.externals = {
            ...config.externals,
            'uglify-js': 'uglify-js',
            '@swc/core': '@swc/core',
          };
        }
        return config;
      },
    });
    console.log('✅ 项目打包完成');

    // 选择组合
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: COMP_NAME,
      inputProps: {
        title,
        priceData,
      },
    });

    console.log('🎬 找到视频组合:', composition.id);

    // 生成带日期的文件名
    const dateStr = targetDate || new Date().toISOString().split('T')[0];
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[1];
    const outputPath = join(outputDir, `price-video-${dateStr}-${timestamp}-${category}.mp4`);

    // 渲染视频
    console.log('🎥 开始渲染视频...');
    console.log(`📁 输出路径: ${outputPath}`);

    await renderMedia({
      composition: {
        ...composition,
        durationInFrames,
        fps: VIDEO_FPS,
        height: VIDEO_HEIGHT,
        width: VIDEO_WIDTH,
      },
      serveUrl: bundleLocation,
      codec: 'h264',
      outputLocation: outputPath,
      inputProps: {
        title,
        priceData,
      },
      onProgress: ({ progress }) => {
        const percentage = Math.round(progress * 100);
        console.log(`🎬 渲染进度: ${percentage}%`);
      },
    });

    console.log('✅ 视频生成完成!');

    return NextResponse.json({
      success: true,
      message: '视频生成成功',
      outputPath,
      dataCount: priceData.length,
      durationInSeconds,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('❌ 视频生成失败:', error);
    
    return NextResponse.json(
      {
        error: '视频生成失败',
        message: error instanceof Error ? error.message : '未知错误',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: '农产品价格视频生成API',
    usage: 'POST /api/generate-video',
    parameters: {
      title: 'string - 视频标题',
      targetDate: '2023-10-01 - 可选，指定日期',
      category: '蔬菜 - 可选，指定分类',
    },
  });
}