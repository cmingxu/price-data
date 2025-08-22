import {
  TITLE_DURATION,
  DATA_PAGE_DURATION,
  ENDING_DURATION,
  ITEMS_PER_PAGE,
} from '../../types/constants';

export const calculateVideoDuration = (dataLength: number): number => {
  const totalPages = Math.ceil(dataLength / ITEMS_PER_PAGE);
  return TITLE_DURATION + (totalPages * DATA_PAGE_DURATION) + ENDING_DURATION;
};