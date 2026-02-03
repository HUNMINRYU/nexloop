import { useState } from 'react';
import { generateHooks, generateVideo as generateVideoRequest } from '@/lib/api';

interface UseVideoStudioProps {
  selectedProduct: string;
  initialVideoPresets?: any;
}

export function useVideoStudio({
  selectedProduct,
  initialVideoPresets,
}: UseVideoStudioProps) {
  const [videoPresets] = useState(initialVideoPresets);
  const [videoHookStyle, setVideoHookStyle] = useState(initialVideoPresets?.hook_styles?.[0]?.key || '');
  const [videoHookText, setVideoHookText] = useState('');
  const [videoDuration, setVideoDuration] = useState(initialVideoPresets?.durations?.[0] || 8);
  const [videoResolution, setVideoResolution] = useState(initialVideoPresets?.resolutions?.[0] || '720p');
  const [cameraMovement, setCameraMovement] = useState(initialVideoPresets?.camera_movements?.[0]?.key || '');
  const [composition, setComposition] = useState(initialVideoPresets?.compositions?.[0]?.key || '');
  const [lightingMood, setLightingMood] = useState(initialVideoPresets?.lighting_moods?.[0]?.key || '');
  const [audioPreset, setAudioPreset] = useState(initialVideoPresets?.audio_presets?.[0]?.key || '');
  const [sfxInput, setSfxInput] = useState('');
  const [ambientInput, setAmbientInput] = useState('');
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState('');
  const [videoPrompt, setVideoPrompt] = useState('');
  const [videoError, setVideoError] = useState('');
  const [isVideoGenerating, setIsVideoGenerating] = useState(false);

  const handleGenerateVideoHook = async () => {
    if (!selectedProduct || !videoHookStyle) return;
    setVideoError('');
    try {
      const response = await generateHooks({ product_name: selectedProduct, style: videoHookStyle, count: 1 });
      if (response?.hooks?.length) {
        setVideoHookText(response.hooks[0] ?? "");
      }
    } catch (err: any) {
      setVideoError(err.message || '훅 생성에 실패했습니다.');
    }
  };

  const handleGenerateVideo = async () => {
    if (!selectedProduct) {
      setVideoError('제품을 선택해주세요.');
      return;
    }
    if (!videoHookText.trim()) {
      setVideoError('후킹 문구를 입력해주세요.');
      return;
    }
    setIsVideoGenerating(true);
    setVideoError('');
    setGeneratedVideoUrl('');
    setVideoPrompt('');
    try {
      const response = await generateVideoRequest({
        product_name: selectedProduct,
        hook_text: videoHookText,
        duration_seconds: videoDuration,
        resolution: videoResolution,
        camera_movement: cameraMovement,
        composition,
        lighting_mood: lightingMood,
        audio_preset: audioPreset,
        sfx: sfxInput ? sfxInput.split(',').map((v) => v.trim()).filter(Boolean) : [],
        ambient: ambientInput || null,
      });
      setGeneratedVideoUrl(response.url);
      setVideoPrompt(response.prompt);
    } catch (err: any) {
      setVideoError(err.message || '비디오 생성에 실패했습니다.');
    } finally {
      setIsVideoGenerating(false);
    }
  };

  return {
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
  };
}
