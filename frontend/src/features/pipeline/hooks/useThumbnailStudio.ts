import { useState, useEffect } from 'react';
import { generateHooks, generateThumbnailCompare } from '@/lib/api';

interface UseThumbnailStudioProps {
  selectedProduct: string;
  initialStyles?: any[];
  initialHookStrategies?: any[];
}

export function useThumbnailStudio({
  selectedProduct,
  initialStyles = [],
  initialHookStrategies = [],
}: UseThumbnailStudioProps) {
  const [styles] = useState(initialStyles);
  const [hookStrategies] = useState(initialHookStrategies);
  const [hookText, setHookText] = useState('');
  const [useHookInput, setUseHookInput] = useState(true);
  const [includeTextOverlay, setIncludeTextOverlay] = useState(true);
  const [compareItems, setCompareItems] = useState<any[]>([]);
  const [isComparing, setIsComparing] = useState(false);
  const [thumbError, setThumbError] = useState('');

  useEffect(() => {
    setHookText('');
  }, [selectedProduct]);

  const handleGenerateHook = async (styleKey: string) => {
    if (!selectedProduct) return;
    setThumbError('');
    try {
      const response = await generateHooks({ product_name: selectedProduct, style: styleKey, count: 1 });
      if (response?.hooks?.length) {
        setHookText(response.hooks[0] ?? "");
      }
    } catch (err: any) {
      setThumbError(err.message || '훅 생성에 실패했습니다.');
    }
  };

  const handleCompareStyles = async () => {
    if (!selectedProduct) {
      setThumbError('제품을 선택해주세요.');
      return;
    }
    setIsComparing(true);
    setThumbError('');
    setCompareItems([]);
    try {
      const response = await generateThumbnailCompare({
        product_name: selectedProduct,
        hook_text: hookText || undefined,
        include_text_overlay: includeTextOverlay,
        max_styles: 9,
        auto_hook_per_style: !useHookInput,
      });
      setCompareItems(response.items || []);
    } catch (err: any) {
      setThumbError(err.message || '스타일 비교 생성에 실패했습니다.');
    } finally {
      setIsComparing(false);
    }
  };

  return {
    styles,
    hookStrategies,
    hookText,
    setHookText,
    useHookInput,
    setUseHookInput,
    includeTextOverlay,
    setIncludeTextOverlay,
    compareItems,
    isComparing,
    thumbError,
    handleGenerateHook,
    handleCompareStyles,
  };
}
