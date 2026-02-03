"""CTR 예측 프롬프트"""
from __future__ import annotations

from core.prompts import PromptTemplate, prompt_registry

CTR_PREDICTION_PROMPT = PromptTemplate(
    name="ctr.prediction",
    template="""
다음 YouTube 영상 제목의 CTR(클릭률) 잠재력을 분석하세요.
{insights_text}
## 분석 대상 제목
"{title}"

## 카테고리
{category}

## 분석 요청
1. 이 제목의 강점 3가지
2. 개선이 필요한 부분 3가지 (제공된 '핵심 인사이트'를 반영하여 고객의 결핍을 채워줄 수 있는 방향 권장)
3. A/B 테스트용 대안 제목 3가지 제안
4. 예상 CTR 범위 (낮음/보통/높음/매우높음)

간결하게 답변하세요.
""".strip(),
)

prompt_registry.register(CTR_PREDICTION_PROMPT)

__all__ = ["CTR_PREDICTION_PROMPT"]
