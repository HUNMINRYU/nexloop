import { Button, Input } from '@/components/ui';
import { Toggle } from './Toggle';

interface PipelineControlSectionProps {
  selectedProduct: string;
  products: string[];
  setSelectedProduct: (val: string) => void;
  handleRunPipeline: () => void;
  isRunning: boolean;
  youtubeCount: number;
  setYoutubeCount: (val: number) => void;
  naverCount: number;
  setNaverCount: (val: number) => void;
  includeComments: boolean;
  setIncludeComments: (val: boolean) => void;
  generateSocial: boolean;
  setGenerateSocial: (val: boolean) => void;
  generateVideo: boolean;
  setGenerateVideo: (val: boolean) => void;
  generateThumbnails: boolean;
  setGenerateThumbnails: (val: boolean) => void;
  exportToNotion: boolean;
  setExportToNotion: (val: boolean) => void;
  pipelineStatus: any;
  progressPercent: number;
  errorMessage: string;
  approvalStatus: string | null;
  canApprove: boolean;
  handleApproval: (status: 'approved' | 'rejected') => void;
  isUpdatingApproval: boolean;
  approvalMessage: string;
}

export function PipelineControlSection({
  selectedProduct,
  products,
  setSelectedProduct,
  handleRunPipeline,
  isRunning,
  youtubeCount,
  setYoutubeCount,
  naverCount,
  setNaverCount,
  includeComments,
  setIncludeComments,
  generateSocial,
  setGenerateSocial,
  generateVideo,
  setGenerateVideo,
  generateThumbnails,
  setGenerateThumbnails,
  exportToNotion,
  setExportToNotion,
  pipelineStatus,
  progressPercent,
  errorMessage,
  approvalStatus,
  canApprove,
  handleApproval,
  isUpdatingApproval,
  approvalMessage,
}: PipelineControlSectionProps) {
  return (
    <div className="flex flex-col gap-4 soft-section p-4">
      <label className="soft-label font-bold">제품 선택</label>
      <div className="flex flex-wrap items-center gap-4">
        <select className="soft-input px-4 py-2" value={selectedProduct} onChange={(e) => setSelectedProduct(e.target.value)}>
          {products.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <Button onClick={handleRunPipeline} disabled={!selectedProduct || isRunning}>
          {isRunning ? '실행 중...' : '실행'}
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="soft-section p-3">
          <label className="soft-label text-xs font-bold text-[var(--color-muted)]">YouTube 결과 수</label>
          <Input type="number" min={1} max={10} value={youtubeCount} onChange={(e) => setYoutubeCount(Number(e.target.value))} className="mt-2 w-full" />
        </div>
        <div className="soft-section p-3">
          <label className="soft-label text-xs font-bold text-[var(--color-muted)]">Naver 결과 수</label>
          <Input type="number" min={5} max={30} value={naverCount} onChange={(e) => setNaverCount(Number(e.target.value))} className="mt-2 w-full" />
        </div>
        <div className="grid grid-cols-2 gap-2 md:col-span-2">
          <Toggle label="댓글 분석" checked={includeComments} onChange={setIncludeComments} />
          <Toggle label="SNS 소재" checked={generateSocial} onChange={setGenerateSocial} />
          <Toggle label="비디오 생성" checked={generateVideo} onChange={setGenerateVideo} />
          <Toggle label="썸네일 생성" checked={generateThumbnails} onChange={setGenerateThumbnails} />
          <Toggle label="Notion 내보내기" checked={exportToNotion} onChange={setExportToNotion} />
        </div>
      </div>
      {errorMessage && <p className="text-sm text-red-500">{errorMessage}</p>}
      <div className="soft-section p-3">
        <div className="flex justify-between text-sm">
          <span>{pipelineStatus?.message || '대기 중'}</span>
          <span>{progressPercent}%</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-slate-200 overflow-hidden">
          <div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${progressPercent}%` }} />
        </div>
      </div>
      <div className="soft-section p-3 space-y-3">
        <div className="flex justify-between text-sm font-medium">
          <span>승인 상태</span>
          <span className="capitalize text-[var(--color-primary)]">{approvalStatus || '대기 중'}</span>
        </div>
        {canApprove && (
          <div className="flex gap-2">
            <Button onClick={() => handleApproval('approved')} disabled={isUpdatingApproval}>승인</Button>
            <Button variant="outline" onClick={() => handleApproval('rejected')} disabled={isUpdatingApproval}>거부</Button>
          </div>
        )}
        {approvalMessage && <p className="text-xs text-[var(--color-muted)]">{approvalMessage}</p>}
      </div>
    </div>
  );
}
