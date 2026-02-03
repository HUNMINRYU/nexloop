"""Hydration/댓글 분석 프롬프트"""
from __future__ import annotations

from core.prompts import PromptTemplate, prompt_registry

HYDRATION_FEATURE_PROMPT = PromptTemplate(
    name="hydration.feature_extraction",
    template="""
Analyze the following user comment and extract engagement features.
Return ONLY a JSON object with values between 0.0 and 1.0.

Comment: "{comment}"

JSON Schema:
{{
    "purchase_intent": float,      # Is the user interested in buying?
    "reply_inducing": float,       # Does this provoke a reply or discussion?
    "constructive_feedback": float,# Is this detailed, specific feedback?
    "sentiment_intensity": float,  # How strong is the emotion?
    "toxicity": float,             # Is this spam/hate speech?
    "keywords": [str]              # Top 2-3 keywords
}}
""".strip(),
)

COMMENT_ANALYSIS_PROMPT = PromptTemplate(
    name="comment.analysis",
    template="""
다음은 제품/서비스 영상에 달린 YouTube 시청자 댓글들입니다.
마케터의 관점에서 이 댓글들을 심층 분석하여 비즈니스 인사이트를 도출해주세요.

### 📝 분석 대상 댓글 (샘플)
{combined_text}

### 🕵️‍♂️ 분석 요청 사항
단순한 요약이 아니라, **'판매 전환'**에 도움이 되는 구체적인 정보를 추출해야 합니다.
다음 JSON 포맷으로 결과를 작성해주세요:

{{
    "customer_sentiment": {{
        "dominant_emotion": "지배적인 감정 (예: 기대감, 실망, 호기심)",
        "sentiment_reason": "위 감정이 나타나는 주된 이유"
    }},
    "deep_pain_points": [
        "고객이 호소하는 구체적인 문제점/불편함 1",
        "고객이 호소하는 구체적인 문제점/불편함 2",
        "고객이 호소하는 구체적인 문제점/불편함 3"
    ],
    "buying_factors": [
        "고객이 제품을 구매하고 싶어하는 핵심 이유 1",
        "고객이 제품을 구매하고 싶어하는 핵심 이유 2"
    ],
    "marketing_hooks": [
        "댓글의 목소리를 반영한 광고 카피 1",
        "댓글의 목소리를 반영한 광고 카피 2",
        "댓글의 목소리를 반영한 광고 카피 3"
    ],
    "faq_candidates": [
        "자주 묻는 질문/오해 1",
        "자주 묻는 질문/오해 2"
    ],
    "executive_summary": "전체 분석 결과를 3문장 내외로 요약 (마케터 보고용)"
}}

반드시 유효한 JSON 형식으로만 응답해주세요.
""".strip(),
)

prompt_registry.register(HYDRATION_FEATURE_PROMPT)
prompt_registry.register(COMMENT_ANALYSIS_PROMPT)

__all__ = ["HYDRATION_FEATURE_PROMPT", "COMMENT_ANALYSIS_PROMPT"]
