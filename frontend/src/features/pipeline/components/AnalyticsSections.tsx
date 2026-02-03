import { Button, Card, Input } from '@/components/ui';

export function PerformanceSection({
  tasks,
  selectedTaskId,
  setSelectedTaskId,
  ctrTitle,
  setCtrTitle,
  ctrThumbDesc,
  setCtrThumbDesc,
  ctrCompetitors,
  setCtrCompetitors,
  handleCtrPredict,
  ctrResult,
}: any) {
  return (
    <div className="space-y-4">
      <div className="soft-section p-4 space-y-3">
        <label className="soft-label text-xs font-bold">작업 선택</label>
        <select className="soft-input w-full p-2" value={selectedTaskId} onChange={(e) => setSelectedTaskId(e.target.value)}>
          {tasks.map((t: any) => <option key={t.task_id} value={t.task_id}>{t.product} ({t.task_id})</option>)}
        </select>
        <Input value={ctrTitle} onChange={(e) => setCtrTitle(e.target.value)} placeholder="영상 제목" />
        <textarea className="soft-input w-full p-2 h-24" value={ctrThumbDesc} onChange={(e) => setCtrThumbDesc(e.target.value)} placeholder="썸네일 설명" />
        <textarea className="soft-input w-full p-2 h-24" value={ctrCompetitors} onChange={(e) => setCtrCompetitors(e.target.value)} placeholder="경쟁자 제목 (줄바꿈 구분)" />
        <Button onClick={handleCtrPredict}>CTR 예측</Button>
      </div>
      {ctrResult && (
        <Card className="p-4">
          <p className="font-bold">예상 CTR: {ctrResult.predicted_ctr}% ({ctrResult.grade})</p>
          {/* ... Breakdown visualization ... */}
        </Card>
      )}
    </div>
  );
}

export function AiInsightsSection({
  tasks,
  selectedTaskId,
  setSelectedTaskId,
  handleStrategyAnalysis,
  handleCommentAnalysis,
  strategy,
  commentAnalysis,
  analysisError,
}: any) {
  return (
    <div className="space-y-4">
      <div className="soft-section p-4 space-y-3">
        <label className="soft-label text-xs font-bold">작업 선택</label>
        <select className="soft-input w-full p-2" value={selectedTaskId} onChange={(e) => setSelectedTaskId(e.target.value)}>
          {tasks.map((t: any) => <option key={t.task_id} value={t.task_id}>{t.product} ({t.task_id})</option>)}
        </select>
        <div className="flex gap-2">
          <Button onClick={handleStrategyAnalysis}>전략 분석</Button>
          <Button variant="secondary" onClick={() => handleCommentAnalysis('basic')}>댓글 기본</Button>
          <Button variant="secondary" onClick={() => handleCommentAnalysis('deep')}>댓글 심층</Button>
        </div>
        {analysisError && <p className="text-sm text-red-500">{analysisError}</p>}
      </div>
      {strategy && <Card className="p-4"><p className="font-bold">전략 요약</p><p>{strategy.summary}</p></Card>}
      {commentAnalysis && <Card className="p-4"><p className="font-bold">댓글 감성</p><p>긍정: {commentAnalysis.sentiment.positive}%</p></Card>}
    </div>
  );
}
