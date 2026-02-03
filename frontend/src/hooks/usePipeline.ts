import { useEffect, useMemo, useRef, useState } from 'react';
import {
  fetchPipelineResult,
  fetchPipelineStatus,
  fetchProducts,
  runPipeline,
} from '@/lib/api';
import { DUMMY_PRODUCTS } from '@/lib/dummyData';
import { PipelineStatus } from '@/types/api';
import { GeneratedThumbnail, PipelineResultDetails } from '@/types/domain';
import { TaskId } from '@/types/common';
import { usePipelineStore } from '@/store/usePipelineStore';

export default function usePipeline() {
  const isDev = process.env.NODE_ENV === 'development';
  const hasFetchedResultRef = useRef(false);
  
  // Zustand Store 구독
  const {
    selectedProduct, youtubeCount, naverCount, includeComments,
    generateSocial, generateVideo, generateThumbnails, exportToNotion,
    taskId, isRunning, status: pipelineStatus, result: pipelineResult, error: errorMessage,
    setConfiguration, setExecutionState, reset
  } = usePipelineStore();

  // 제품 목록 페칭 (이 부분은 React Query로 대체 가능하지만, 현재 구조 유지하되 products 로컬 상태는 훅 내부에 둠)
  // TODO: 추후 products도 React Query로 전환 권장
  const [products, setProducts] = useState<string[]>([]); // React import 필요

  useEffect(() => {
    let isMounted = true;
    fetchProducts()
      .then((data) => {
        if (!isMounted) return;
        const names = data?.products || [];
        if (names.length > 0) {
          setProducts(names);
          // 초기 선택값이 없을 때만 설정
          if (!selectedProduct && names.length > 0) {
            setConfiguration({ selectedProduct: names[0] });
          }
          return;
        }
        if (isDev) {
          setProducts(DUMMY_PRODUCTS);
          if (!selectedProduct && DUMMY_PRODUCTS.length > 0) {
            setConfiguration({ selectedProduct: DUMMY_PRODUCTS[0] });
          }
          return;
        }
        setProducts([]);
        setConfiguration({ selectedProduct: '' });
        setExecutionState({ error: '제품 목록을 불러오지 못했습니다.' });
      })
      .catch(() => {
        if (!isMounted) return;
        if (isDev) {
          setProducts(DUMMY_PRODUCTS);
          if (!selectedProduct && DUMMY_PRODUCTS.length > 0) {
             setConfiguration({ selectedProduct: DUMMY_PRODUCTS[0] });
          }
          return;
        }
        setProducts([]);
        setConfiguration({ selectedProduct: '' });
        setExecutionState({ error: '제품 목록을 불러오지 못했습니다.' });
      });

    return () => {
      isMounted = false;
    };
  }, []); // 의존성 배열 비움 (마운트 시 1회)

  // Polling 및 EventSource 로직
  useEffect(() => {
    if (!taskId) return;

    let isActive = true;
    let intervalId: ReturnType<typeof setInterval> | undefined;
    let eventSource: EventSource | null = null;

    const fetchResultOnce = async () => {
      if (hasFetchedResultRef.current) return;
      try {
        const result = await fetchPipelineResult(taskId as TaskId);
        if (isActive) {
          setExecutionState({ result });
        }
        hasFetchedResultRef.current = true;
      } catch (err: any) {
        if (isActive) {
          setExecutionState({ error: err.message || '결과를 불러오지 못했습니다.' });
        }
      }
    };

    const handleFinished = async (finalStatus: PipelineStatus) => {
      setExecutionState({ status: finalStatus, isRunning: false });
      await fetchResultOnce();
    };

    const poll = async () => {
      try {
        const currentStatus = await fetchPipelineStatus(taskId as TaskId);
        if (!isActive) return;
        setExecutionState({ status: currentStatus });
        
        const finished = currentStatus?.status === 'success' || currentStatus?.status === 'failed';
        if (finished) {
          await handleFinished(currentStatus);
          if (intervalId) {
            clearInterval(intervalId);
            intervalId = undefined;
          }
        }
      } catch (err: any) {
        if (isActive) {
          setExecutionState({ error: err.message || '상태를 불러오지 못했습니다.' });
        }
      }
    };

    const startPolling = () => {
      poll();
      intervalId = setInterval(poll, 3000);
    };

    if (typeof EventSource !== 'undefined') {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
        eventSource = new EventSource(`${baseUrl}/pipeline/status-stream/${taskId}`);
        eventSource.onmessage = async (event) => {
          if (!isActive) return;
          const streamStatus = JSON.parse(event.data) as PipelineStatus;
          const finished = streamStatus?.status === 'success' || streamStatus?.status === 'failed';
          
          if (finished) {
            if (eventSource) eventSource.close();
            await handleFinished(streamStatus);
          } else {
             setExecutionState({ status: streamStatus });
          }
        };
        eventSource.onerror = () => {
          if (eventSource) eventSource.close();
          if (!intervalId) startPolling();
        };
      } catch {
        startPolling();
      }
    } else {
      startPolling();
    }

    return () => {
      isActive = false;
      if (eventSource) eventSource.close();
      if (intervalId) clearInterval(intervalId);
    };
  }, [taskId, setExecutionState]);

  const handleRunPipeline = async () => {
    if (!selectedProduct || isRunning) return;
    
    setExecutionState({ 
        error: '', 
        result: null, 
        status: null, 
        isRunning: true 
    });
    hasFetchedResultRef.current = false;

    try {
      const response = await runPipeline({
        product_name: selectedProduct,
        youtube_count: youtubeCount,
        naver_count: naverCount,
        include_comments: includeComments,
        generate_social: generateSocial,
        generate_video: generateVideo,
        generate_thumbnails: generateThumbnails,
        export_to_notion: exportToNotion,
      });
      
      const newTaskId = response.task_id;
      setExecutionState({ 
          taskId: newTaskId,
          status: {
            status: 'triggered',
            message: '파이프라인을 시작했습니다.',
            progress: { percentage: 0, message: '대기 중', step: 'initialized' },
            task_id: newTaskId,
          }
      });
    } catch (err: any) {
      setExecutionState({ 
          isRunning: false, 
          error: err.message || '파이프라인 실행에 실패했습니다.' 
      });
    }
  };



// ...

  // Memoized Derived Data
  const thumbnails = useMemo(() => {
    const items: string[] = [];
    const generatedContent = pipelineResult?.result?.generated_content || null;
    if (generatedContent?.thumbnail_url) items.push(generatedContent.thumbnail_url);
    if (Array.isArray(generatedContent?.multi_thumbnails)) {
      generatedContent.multi_thumbnails.forEach((item: GeneratedThumbnail) => {
        if (!item) return;
        const url = item.url || item.thumbnail_url || item.image_url;
        if (url) items.push(url);
      });
    }
    return items;
  }, [pipelineResult]);

  const videoUrls = useMemo(() => {
    const items: string[] = [];
    const generatedContent = pipelineResult?.result?.generated_content || null;
    if (generatedContent?.video_url) items.push(generatedContent.video_url);
    return items;
  }, [pipelineResult]);

  const analyticsData = useMemo(() => {
    const collected = pipelineResult?.result?.collected_data || {};
    const strategy = pipelineResult?.result?.strategy;
    
    // Type guards/checks are now implicitly handled by interfaces, but fallback is safe
    const youtubeItems = collected.youtube_data?.items;
    const naverItems = collected.naver_data?.items;
    
    const visibility = Array.isArray(youtubeItems)
      ? youtubeItems.length
      : Array.isArray(naverItems)
        ? naverItems.length
        : 0;

    const ctrPrecision = strategy?.ctr ?? 0;
    const sentiment = strategy?.sentiment || strategy?.summary || 'N/A';
    return { visibility, ctrPrecision, sentiment };
  }, [pipelineResult]);

  const socialPosts = useMemo(() => {
    return pipelineResult?.result?.strategy?.social_posts || null;
  }, [pipelineResult]);

  return {
    products,
    selectedProduct,
    setSelectedProduct: (val: string) => setConfiguration({ selectedProduct: val }),
    pipelineStatus,
    pipelineResult,
    taskId,
    isRunning,
    errorMessage,
    youtubeCount,
    naverCount,
    includeComments,
    generateSocial,
    generateVideo,
    generateThumbnails,
    exportToNotion,
    setYoutubeCount: (val: number) => setConfiguration({ youtubeCount: val }),
    setNaverCount: (val: number) => setConfiguration({ naverCount: val }),
    setIncludeComments: (val: boolean) => setConfiguration({ includeComments: val }),
    setGenerateSocial: (val: boolean) => setConfiguration({ generateSocial: val }),
    setGenerateVideo: (val: boolean) => setConfiguration({ generateVideo: val }),
    setGenerateThumbnails: (val: boolean) => setConfiguration({ generateThumbnails: val }),
    setExportToNotion: (val: boolean) => setConfiguration({ exportToNotion: val }),
    handleRunPipeline,
    thumbnails,
    videoUrls,
    analyticsData,
    socialPosts,
  };
}
