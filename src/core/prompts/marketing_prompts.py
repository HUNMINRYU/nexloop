"""마케팅 분석 프롬프트"""
from __future__ import annotations

from core.prompts import PromptTemplate, prompt_registry

MARKETING_ANALYSIS_PROMPT = PromptTemplate(
    name="marketing.analysis",
    template="""
당신은 전문 마케팅 분석가입니다. 다음 데이터를 분석하여 마케팅 인사이트를 제공해주세요.

## 분석 대상 제품
제품명: {product_name}

## X-Algorithm 핵심 인사이트 (유튜브 댓글 분석 결과)
{top_insights_json}
*참고: 위 인사이트는 AI가 실제 고객 반응에서 추출한 고가치 정보입니다. 전략 수립 시 최우선적으로 반영하세요.*

## 시장 트렌드 (GCP Search 결과)
{market_trends_json}

## YouTube 데이터 (트렌드 및 경쟁 영상)
{youtube_data_json}

## 네이버 데이터 (쇼핑 + 블로그 + 뉴스)
{naver_data_json}

## 분석 요청
다음 형식으로 분석 결과를 JSON으로 반환해주세요:

{{
    "target_audience": {{
        "primary": "주요 타겟 고객층",
        "secondary": "2차 타겟 고객층",
        "pain_points": ["고객 페인 포인트 1", "페인 포인트 2", "페인 포인트 3"],
        "desires": ["고객이 원하는 것 1", "원하는 것 2", "원하는 것 3"]
    }},
    "competitor_analysis": {{
        "price_range": "가격대 분석",
        "key_features": ["주요 경쟁 기능 1", "기능 2", "기능 3"],
        "differentiators": ["차별화 포인트 1", "포인트 2"]
    }},
    "content_strategy": {{
        "trending_topics": ["인기 주제 1", "주제 2", "주제 3"],
        "content_types": ["효과적인 콘텐츠 유형 1", "유형 2"],
        "posting_tips": ["포스팅 팁 1", "팁 2"]
    }},
    "hook_suggestions": [
        "훅 문구 제안 1",
        "훅 문구 제안 2",
        "훅 문구 제안 3",
        "훅 문구 제안 4",
        "훅 문구 제안 5"
    ],
    "keywords": ["키워드 1", "키워드 2", "키워드 3", "키워드 4", "키워드 5"],
    "summary": "전체 분석 요약 (2-3문장)"
}}
""".strip(),
)

prompt_registry.register(MARKETING_ANALYSIS_PROMPT)

__all__ = ["MARKETING_ANALYSIS_PROMPT"]
