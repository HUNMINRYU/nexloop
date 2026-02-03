export interface YouTubeItem {
  id: string;
  title: string;
  viewCount: string | number;
  likeCount: string | number;
  commentCount: string | number;
  publishedAt: string;
  thumbnail: string;
  channelTitle: string;
  url: string;
  description?: string;
  comments?: Array<{
    author: string;
    text: string;
    likeCount: number;
    publishedAt: string;
  }>;
}

export interface NaverItem {
  title: string;
  link: string;
  description: string;
  bloggername: string;
  bloggerlink: string;
  postdate: string;
}

export interface CollectedData {
  youtube_data?: {
    items: YouTubeItem[];
    metadata?: any;
  };
  naver_data?: {
    items: NaverItem[];
    lastBuildDate?: string;
    total?: number;
  };
  top_insights?: Array<{
    content: string;
    source: string;
    score?: number;
  }>;
}

export interface MarketingStrategy {
  summary: string;
  target_audience: {
    demographics: string[];
    interests: string[];
    pain_points: string[];
  };
  unique_selling_point: string[];
  hook_suggestions: string[];
  content_direction: string[];
  competitor_analysis: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
  };
  ctr?: number;
  sentiment?: string;
  social_posts?: {
    instagram?: {
      caption: string;
      hashtags: string[];
    };
    twitter?: {
      content: string;
    };
    blog?: {
      title: string;
      content: string;
    };
  };
}

export interface GeneratedThumbnail {
  url?: string;
  thumbnail_url?: string; // Unified access might be needed
  image_url?: string;
  style?: string;
}

export interface GeneratedContent {
  thumbnail_data?: string; // base64 or internal
  thumbnail_url?: string;
  multi_thumbnails?: GeneratedThumbnail[];
  video_url?: string;
  video_bytes?: string; // base64
}

export interface PipelineResultDetails {
  approval_status: 'draft' | 'pending_review' | 'approved' | 'rejected';
  product_name: string;
  config?: any;
  collected_data?: CollectedData;
  strategy?: MarketingStrategy;
  generated_content?: GeneratedContent;
  prompt_log?: Record<string, any>;
  audit_trail?: Array<{
    action: string;
    by: string;
    at: string;
  }>;
  upload_status?: string;
  upload_errors?: string[];
  duration_seconds?: number;
  error_message?: string;
}
