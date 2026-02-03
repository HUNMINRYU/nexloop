"""소셜 미디어 프롬프트"""
from __future__ import annotations

from core.prompts import PromptTemplate, prompt_registry

SOCIAL_MEDIA_PROMPT = PromptTemplate(
    name="social.media.posts",
    template="""
당신은 소셜 미디어 마케팅 전문가입니다. 다음 제품 정보를 바탕으로 각 채널별 맞춤형 포스팅 문구를 생성해주세요.

## 제품 정보
- 제품명: {product_name}
- 핵심 전략: {summary}

## X-Algorithm 핵심 인사이트 (고객의 실제 목소리)
{insights_text}

## 요청 사항
1. 인스타그램(Instagram): 비주얼 중심, 감성적인 문구, 해시태그 포함
2. 트위터(X): 짧고 강렬한 훅, 바이럴 유도, 핵심 키워드 중심
3. 블로그(Blog): 상세한 정보 전달, 신뢰감 있는 톤, 구조화된 설명

반드시 다음 JSON 형식으로 응답하세요:
{{
    "instagram": {{
        "caption": "인스타그램 문구",
        "hashtags": ["#태그1", "#태그2"]
    }},
    "twitter": {{
        "content": "트위터 문구"
    }},
    "blog": {{
        "title": "블로그 제목",
        "content": "블로그 요약 본문"
    }}
}}
""".strip(),
)

prompt_registry.register(SOCIAL_MEDIA_PROMPT)

__all__ = ["SOCIAL_MEDIA_PROMPT"]
