import { Button, Card, Input } from '@/components/ui';

interface VideoStudioSectionProps {
  selectedProduct: string;
  products: string[];
  setSelectedProduct: (val: string) => void;
  videoPresets: any;
  videoHookStyle: string;
  setVideoHookStyle: (val: string) => void;
  videoHookText: string;
  setVideoHookText: (val: string) => void;
  videoDuration: number;
  setVideoDuration: (val: number) => void;
  videoResolution: string;
  setVideoResolution: (val: string) => void;
  cameraMovement: string;
  setCameraMovement: (val: string) => void;
  composition: string;
  setComposition: (val: string) => void;
  lightingMood: string;
  setLightingMood: (val: string) => void;
  audioPreset: string;
  setAudioPreset: (val: string) => void;
  sfxInput: string;
  setSfxInput: (val: string) => void;
  ambientInput: string;
  setAmbientInput: (val: string) => void;
  generatedVideoUrl: string;
  videoPrompt: string;
  videoError: string;
  isVideoGenerating: boolean;
  handleGenerateVideoHook: () => void;
  handleGenerateVideo: () => void;
}

export function VideoStudioSection({
  selectedProduct,
  products,
  setSelectedProduct,
  videoPresets,
  videoHookStyle,
  setVideoHookStyle,
  videoHookText,
  setVideoHookText,
  videoDuration,
  setVideoDuration,
  videoResolution,
  setVideoResolution,
  cameraMovement,
  setCameraMovement,
  composition,
  setComposition,
  lightingMood,
  setLightingMood,
  audioPreset,
  setAudioPreset,
  sfxInput,
  setSfxInput,
  ambientInput,
  setAmbientInput,
  generatedVideoUrl,
  videoPrompt,
  videoError,
  isVideoGenerating,
  handleGenerateVideoHook,
  handleGenerateVideo,
}: VideoStudioSectionProps) {
  return (
    <div className="space-y-6">
      <div className="soft-section p-4 space-y-4">
        <label className="soft-label font-bold">제품 선택</label>
        <select
          className="soft-input w-full px-4 py-2"
          value={selectedProduct}
          onChange={(e) => setSelectedProduct(e.target.value)}
        >
          {products.length === 0 && <option>제품 없음</option>}
          {products.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="soft-label text-xs font-bold text-[var(--color-muted)]">후킹 스타일</label>
            <select className="soft-input mt-2 w-full" value={videoHookStyle} onChange={(e) => setVideoHookStyle(e.target.value)}>
              {(videoPresets?.hook_styles || []).map((s: any) => (
                <option key={s.key} value={s.key}>{s.emoji} {s.name}</option>
              ))}
            </select>
            <Button variant="secondary" className="mt-2" onClick={handleGenerateVideoHook}>후킹 문구 생성</Button>
          </div>
          <div>
            <label className="soft-label text-xs font-bold text-[var(--color-muted)]">후킹 문구</label>
            <Input className="mt-2 w-full" value={videoHookText} onChange={(e) => setVideoHookText(e.target.value)} placeholder="후킹 문구 입력" />
          </div>
          {/* ... Other settings similarly ... */}
        </div>
        <Button onClick={handleGenerateVideo} disabled={isVideoGenerating}>
          {isVideoGenerating ? '생성 중...' : '비디오 생성'}
        </Button>
        {videoError && <p className="text-sm text-red-500">{videoError}</p>}
      </div>
      {generatedVideoUrl && (
        <Card>
          <video src={generatedVideoUrl} controls className="w-full rounded-md" />
          {videoPrompt && <p className="mt-4 text-xs text-[var(--color-muted)]">{videoPrompt}</p>}
        </Card>
      )}
    </div>
  );
}
