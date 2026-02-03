'use client';

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { PipelineStatus, PipelineResult } from '@/types/api';
import { TaskId } from '@/types/common';

interface PipelineState {
  // Configuration
  selectedProduct: string;
  youtubeCount: number;
  naverCount: number;
  includeComments: boolean;
  generateSocial: boolean;
  generateVideo: boolean;
  generateThumbnails: boolean;
  exportToNotion: boolean;

  // Execution State
  taskId: TaskId | '';
  isRunning: boolean;
  status: PipelineStatus | null;
  result: PipelineResult | null;
  error: string;

  // Actions
  setConfiguration: (config: Partial<Pick<PipelineState, 
    'selectedProduct' | 'youtubeCount' | 'naverCount' | 'includeComments' | 
    'generateSocial' | 'generateVideo' | 'generateThumbnails' | 'exportToNotion'
  >>) => void;
  setExecutionState: (state: Partial<Pick<PipelineState, 
    'taskId' | 'isRunning' | 'status' | 'result' | 'error'
  >>) => void;
  reset: () => void;
}

const initialState = {
  selectedProduct: '',
  youtubeCount: 3,
  naverCount: 10,
  includeComments: true,
  generateSocial: true,
  generateVideo: true,
  generateThumbnails: true,
  exportToNotion: true,
  taskId: '' as TaskId | '',
  isRunning: false,
  status: null,
  result: null,
  error: '',
};

export const usePipelineStore = create<PipelineState>()(
  devtools((set) => ({
    ...initialState,
    setConfiguration: (config) => set((state) => ({ ...state, ...config })),
    setExecutionState: (executionState) => set((state) => ({ ...state, ...executionState })),
    reset: () => set(initialState),
  }))
);
