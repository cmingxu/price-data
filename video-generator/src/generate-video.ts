#!/usr/bin/env node

import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';

import { join } from 'path';
import { fetchPriceData } from './lib/api';
import { calculateVideoDuration } from './utils/video-duration';
import {
  COMP_NAME,
  VIDEO_FPS,
} from '../types/constants';

/**
 * 生成农产品价格视频
 */
async function generatePriceVideo() {
  try {
    console.log('🚀 开始生成农产品价格视频...');
    
    // 1. 获取价格数据
    console.log('📊 正在获取价格数据...');
    const priceData = await fetchPriceData();
    console.log(`✅ 获取到 ${priceData.length} 条价格数据`);
    
    if (priceData.length === 0) {
      throw new Error('没有获取到价格数据');
    }
    
    // 2. 计算视频时长
    const durationInFrames = calculateVideoDuration(priceData.length);
    const durationInSeconds = Math.round(durationInFrames / VIDEO_FPS);
    console.log(`⏱️  视频时长: ${durationInSeconds} 秒 (${durationInFrames} 帧)`);
    
    // 3. 打包Remotion项目
    console.log('📦 正在打包项目...');
    const bundleLocation = await bundle({
      entryPoint: join(process.cwd(), 'src/remotion/index.ts'),
      // 可以添加更多配置选项
    });
    console.log('✅ 项目打包完成');
    
    // 4. 选择组合
    const composition = await selectComposition({
      serveUrl: bundleLocation,
      id: COMP_NAME,
      inputProps: {
        title: '今日农产品价格',
        priceData: priceData,
      },
    });
    
    console.log('🎬 找到视频组合:', composition.id);
    
    // 5. 生成输出文件名
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0];
    const timeStr = today.toTimeString().split(' ')[0].replace(/:/g, '-');
    const outputPath = join(process.cwd(), 'output', `price-video-${dateStr}-${timeStr}.mp4`);
    
    // 6. 渲染视频
    console.log('🎥 开始渲染视频...');
    console.log(`📁 输出路径: ${outputPath}`);
    
    await renderMedia({
      composition,
      serveUrl: bundleLocation,
      codec: 'h264',
      outputLocation: outputPath,
      inputProps: {
        title: '今日农产品价格',
        priceData: priceData,
      },
      onProgress: ({ progress }) => {
        const percentage = Math.round(progress * 100);
        process.stdout.write(`\r🎬 渲染进度: ${percentage}%`);
      },
    });
    
    console.log('\n✅ 视频生成完成!');
    console.log(`📹 视频文件: ${outputPath}`);
    console.log(`📊 包含 ${priceData.length} 条价格数据`);
    console.log(`⏱️  视频时长: ${durationInSeconds} 秒`);
    
  } catch (error) {
    console.error('❌ 视频生成失败:', error);
    process.exit(1);
  }
}

/**
 * 创建输出目录
 */
async function ensureOutputDirectory() {
  const { mkdir } = await import('fs/promises');
  const outputDir = join(process.cwd(), 'output');
  
  try {
    await mkdir(outputDir, { recursive: true });
  } catch {
    // 目录可能已存在，忽略错误
  }
}

// 主函数
async function main() {
  await ensureOutputDirectory();
  await generatePriceVideo();
}

// 如果直接运行此脚本
if (require.main === module) {
  main().catch(console.error);
}

export { generatePriceVideo };