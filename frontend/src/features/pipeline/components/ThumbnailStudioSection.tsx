import { Button, Card, Input } from '@/components/ui';

interface ThumbnailStudioSectionProps {
  selectedProduct: string;
  products: string[];
  setSelectedProduct: (val: string) => void;
  hookText: string;
  setHookText: (val: string) => void;
  hookStrategies: any[];
  useHookInput: boolean;
  setUseHookInput: (val: boolean) => void;
  includeTextOverlay: boolean;
  setIncludeTextOverlay: (val: boolean) => void;
  compareItems: any[];
  isComparing: boolean;
  thumbError: string;
  handleGenerateHook: (styleKey: string) => void;
  handleCompareStyles: () => void;
}

export function ThumbnailStudioSection({
  selectedProduct,
  products,
  setSelectedProduct,
  hookText,
  setHookText,
  hookStrategies,
  useHookInput,
  setUseHookInput,
  includeTextOverlay,
  setIncludeTextOverlay,
  compareItems,
  isComparing,
  thumbError,
  handleGenerateHook,
  handleCompareStyles,
}: ThumbnailStudioSectionProps) {
  return (
    <div className="space-y-8">
      <div className="soft-section p-4 space-y-4">
        <h3 className="text-lg font-bold">스타일 비교</h3>
        <p className="text-sm text-[var(--color-muted)]">
          제품·훅을 정한 뒤 한 번에 9종 스타일을 생성해 비교하세요.
        </p>
        <div className="flex flex-wrap items-end gap-4">
          <div className="min-w-[200px]">
            <label className="soft-label text-xs font-bold text-[var(--color-muted)]">제품</label>
            <select
              className="soft-input mt-1 w-full px-3 py-2"
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
            >
              {products.length === 0 && <option>제품 없음</option>}
              {products.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="soft-label text-xs font-bold text-[var(--color-muted)]">훅 텍스트</label>
            <Input
              className="mt-1 w-full"
              value={hookText}
              onChange={(e) => setHookText(e.target.value)}
              placeholder="예: 지금 안 사면 후회할"
            />
          </div>
        </div>
        <div className="space-y-2">
          <label className="soft-label text-xs font-bold text-[var(--color-muted)]">훅 스타일</label>
          <div className="flex flex-wrap gap-2">
            {hookStrategies.map((s) => (
              <Button
                key={s.key}
                type="button"
                variant="secondary"
                className="text-xs px-3 py-1"
                onClick={() => handleGenerateHook(s.key)}
              >
                {s.emoji ? `${s.emoji} ` : ''}{s.name}
              </Button>
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <label className="flex items-center gap-2 font-medium">
            <input type="checkbox" checked={useHookInput} onChange={(e) => setUseHookInput(e.target.checked)} />
            훅 텍스트 직접 입력
          </label>
          <label className="flex items-center gap-2 font-medium">
            <input type="checkbox" checked={includeTextOverlay} onChange={(e) => setIncludeTextOverlay(e.target.checked)} />
            텍스트 오버레이 포함
          </label>
        </div>
        <Button onClick={handleCompareStyles} disabled={isComparing}>
          {isComparing ? '생성 중...' : '스타일 비교 생성 (9종)'}
        </Button>
        {thumbError && <p className="text-sm text-red-500">{thumbError}</p>}
        <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
          {compareItems.map((item, idx) => (
            <div key={idx} className="soft-section p-2 rounded-[var(--radius-md)]">
              <img src={item.url} alt={item.name} className="w-full aspect-[9/16] object-cover rounded-[var(--radius-sm)]" />
              <p className="mt-2 text-xs font-bold">{item.name}</p>
              <p className="text-xs text-[var(--color-muted)] truncate">{item.hook_text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
