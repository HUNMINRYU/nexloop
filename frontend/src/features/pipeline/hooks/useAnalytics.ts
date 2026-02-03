import { useState, useEffect, useMemo } from 'react';
import usePipelineHistory from '@/hooks/usePipelineHistory';
import { fetchPipelineResult, analyzeStrategy, analyzeCommentsBasic, analyzeCommentsDeep, predictCtr } from '@/lib/api';
import { DUMMY_ANALYTICS } from '@/lib/dummyData';
import { PipelineResult } from '@/types/api';
import { TaskId } from '@/types/common';

export function useAnalytics(slug: string) {
  const { tasks, error, isLoading, isDummy } = usePipelineHistory();
  const [results, setResults] = useState<Record<string, PipelineResult>>({});
  const [selectedTaskId, setSelectedTaskId] = useState<TaskId | ''>('');
  const [strategy, setStrategy] = useState<any>(null);
  const [commentAnalysis, setCommentAnalysis] = useState<any>(null);
  const [analysisError, setAnalysisError] = useState('');
  const [ctrTitle, setCtrTitle] = useState('');
  const [ctrThumbDesc, setCtrThumbDesc] = useState('');
  const [ctrCompetitors, setCtrCompetitors] = useState('');
  const [ctrResult, setCtrResult] = useState<any>(null);

  useEffect(() => {
    if (!slug || tasks.length === 0) return;
    const taskIds = tasks.map((task) => task.task_id).filter(Boolean);
    Promise.all(
      taskIds.map((taskId) =>
        fetchPipelineResult(taskId as TaskId).then((data) => ({ taskId, data })).catch(() => null)
      )
    ).then((items) => {
      const mapped: Record<string, PipelineResult> = {};
      items.forEach((item) => {
        if (item) mapped[item.taskId] = item.data;
      });
      setResults(mapped);
    });
  }, [slug, tasks]);

  useEffect(() => {
    if (!selectedTaskId && tasks.length > 0) {
      const firstTaskId = tasks[0]?.task_id;
      if (firstTaskId) {
        setSelectedTaskId(firstTaskId);
      }
    }
  }, [selectedTaskId, tasks]);

  const performanceItems = useMemo(() => {
    if (slug !== 'performance') return [];
    return tasks.map((task, idx) => {
      const result = results[task.task_id];
      const strategy = result?.result?.strategy;
      const hasResult = !!result;
      return {
        taskId: task.task_id as TaskId,
        product: task.product,
        ctr: typeof strategy?.ctr === 'number' 
          ? strategy.ctr 
          : (isDummy && !hasResult ? DUMMY_ANALYTICS.ctrPrecision + idx * 0.5 : 0),
        summary: strategy?.summary || (isDummy && !hasResult ? `샘플 요약: ${task.product} 성과 데이터` : ''),
      };
    });
  }, [results, slug, tasks, isDummy]);

  const handleStrategyAnalysis = async () => {
    if (!selectedTaskId) return;
    setAnalysisError('');
    try {
      const response = await analyzeStrategy(selectedTaskId);
      setStrategy(response.strategy);
    } catch (err: any) {
      setAnalysisError(err.message || 'AI 분석에 실패했습니다.');
    }
  };

  const handleCommentAnalysis = async (type: 'basic' | 'deep') => {
    if (!selectedTaskId) return;
    setAnalysisError('');
    try {
      const response = type === 'basic' ? await analyzeCommentsBasic(selectedTaskId) : await analyzeCommentsDeep(selectedTaskId);
      setCommentAnalysis(response.analysis);
    } catch (err: any) {
      setAnalysisError(err.message || '댓글 분석에 실패했습니다.');
    }
  };

  const handleCtrPredict = async () => {
    if (!selectedTaskId || !ctrTitle.trim()) {
      setAnalysisError('제목과 작업을 선택해주세요.');
      return;
    }
    setAnalysisError('');
    try {
      const response = await predictCtr({
        task_id: selectedTaskId,
        title: ctrTitle,
        thumbnail_description: ctrThumbDesc,
        competitor_titles: ctrCompetitors.split('\n').map((v) => v.trim()).filter(Boolean),
      });
      setCtrResult(response.prediction);
    } catch (err: any) {
      setAnalysisError(err.message || 'CTR 예측에 실패했습니다.');
    }
  };

  return {
    tasks,
    isLoading,
    error,
    selectedTaskId,
    setSelectedTaskId,
    performanceItems,
    strategy,
    commentAnalysis,
    analysisError,
    ctrTitle,
    setCtrTitle,
    ctrThumbDesc,
    setCtrThumbDesc,
    ctrCompetitors,
    setCtrCompetitors,
    ctrResult,
    handleStrategyAnalysis,
    handleCommentAnalysis,
    handleCtrPredict,
  };
}
