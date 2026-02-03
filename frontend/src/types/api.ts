import { TaskId, GcsPath, TeamId, RoleId } from './common';

export interface PipelineStatus {
  status: 'triggered' | 'pending' | 'running' | 'success' | 'failed';
  message: string;
  progress: {
    percentage: number;
    message: string;
    step: string;
  };
  task_id: TaskId;
}

import { PipelineResultDetails } from './domain';

export interface PipelineResult {
  task_id: TaskId;
  product: string;
  status: 'success' | 'failed';
  result?: PipelineResultDetails;
}

export interface ThumbnailStyle {
  key: string;
  name: string;
  description: string;
}

export interface HookStrategy {
  key: string;
  name: string;
  emoji?: string;
}

export interface VideoPresets {
  hook_styles: Array<HookStrategy & { description: string }>;
  camera_movements: Array<{ key: string; name_ko: string; description: string }>;
  compositions: Array<{ key: string; name_ko: string }>;
  lighting_moods: Array<{ key: string; name_ko: string }>;
  audio_presets: Array<{ key: string; name_ko: string }>;
  durations: number[];
  resolutions: string[];
}

export interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  actor: string;
  details: Record<string, any>;
}

export interface Role {
  id: RoleId;
  name: string;
  description?: string | null;
}

export interface Team {
  id: TeamId;
  name: string;
}
