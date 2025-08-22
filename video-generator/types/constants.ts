import { z } from "zod";
export const COMP_NAME = "PriceVideo";

// 价格数据类型定义
const PriceDataSchema = z.object({
  id: z.number(),
  prod_name: z.string(),
  avg_price: z.number(),
  pub_date: z.string(),
  prod_pcatid: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
  price_change_1d: z.number().optional(),
  price_change_7d: z.number().optional(),
});

export const CompositionProps = z.object({
  title: z.string(),
  priceData: z.array(PriceDataSchema),
});

export const defaultMyCompProps: z.infer<typeof CompositionProps> = {
  title: "今日农产品价格",
  priceData: [],
};

// 视频配置 - 移动端竖屏格式 (9:16)
export const VIDEO_WIDTH = 1080;
export const VIDEO_HEIGHT = 1920;
export const VIDEO_FPS = 30;

// 时间配置（以帧为单位）
export const TITLE_DURATION = 2 * VIDEO_FPS; // 2秒标题
export const DATA_PAGE_DURATION = 5 * VIDEO_FPS; // 每页数据5秒
export const ENDING_DURATION = 3 * VIDEO_FPS; // 3秒结尾

// 每页显示的数据条数
export const ITEMS_PER_PAGE = 15;

// 计算总时长（标题 + 数据页面 + 结尾）
// 这个值会在运行时根据实际数据量动态计算
export const DURATION_IN_FRAMES = TITLE_DURATION + DATA_PAGE_DURATION + ENDING_DURATION;
