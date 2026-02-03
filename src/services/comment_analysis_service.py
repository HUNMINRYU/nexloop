"""
댓글 분석 서비스
YouTube 댓글에서 마케팅 인사이트 추출
"""

import re
from collections import Counter
from typing import Optional

from api import validate_json_output
from core.prompts import prompt_registry
from core.prompts import hydration_prompts  # noqa: F401
from utils.logger import get_logger, log_llm_fail, log_llm_request, log_llm_response, log_step, log_success

logger = get_logger(__name__)


# === 감정 분석 키워드 ===
POSITIVE_KEYWORDS = [
    "좋아요",
    "최고",
    "대박",
    "추천",
    "만족",
    "효과",
    "짱",
    "굿",
    "감사",
    "완벽",
    "훌륭",
    "사랑",
    "최애",
    "인생템",
    "갓",
    "미쳤",
    "쩔어",
    "good",
    "great",
    "best",
    "love",
    "amazing",
    "perfect",
    "awesome",
]

NEGATIVE_KEYWORDS = [
    "별로",
    "실망",
    "환불",
    "사기",
    "후회",
    "안됨",
    "효과없",
    "가짜",
    "최악",
    "비추",
    "쓰레기",
    "돈낭비",
    "짜증",
    "불만",
    "구림",
    "bad",
    "worst",
    "hate",
    "terrible",
    "scam",
    "fake",
    "disappointed",
]

PAIN_KEYWORDS = [
    "고민",
    "문제",
    "어려",
    "힘들",
    "귀찮",
    "불편",
    "답답",
    "스트레스",
    "무서",
    "걱정",
    "짜증",
    "못",
    "안되",
    "왜",
    "어떻게",
    "도와",
]

QUESTION_PATTERNS = [
    r"어디서\s*(?:사|구매|구입)",
    r"얼마(?:예요|에요|인가요|야)",
    r"효과\s*(?:있|없|좋|어때)",
    r"추천\s*(?:해|좀|부탁)",
    r"\?$",  # 물음표로 끝나는 문장
]


class CommentAnalysisService:
    """YouTube 댓글 분석 서비스 (Hybrid: Rule-based + AI)"""

    def __init__(self, gemini_client=None) -> None:
        """
        Args:
            gemini_client: AI 기반 심층 분석 시 사용 (필수)
        """
        self._gemini = gemini_client
        self.pipeline: Optional["PipelineOrchestrator"] = None

        # X-Algorithm Pipeline 초기화
        if self._gemini:
            from services.pipeline import (
                CommentSource,
                EngagementScorer,
                FeatureHydrator,
                PipelineOrchestrator,
                QualityFilter,
                TopInsightSelector,
            )

            self.pipeline = PipelineOrchestrator(
                source=CommentSource(),
                hydrator=FeatureHydrator(gemini_client),  # gemini_client 재사용
                quality_filter=QualityFilter(),
                scorer=EngagementScorer(),
                selector=TopInsightSelector(),
            )
        else:
            self.pipeline = None

    def analyze_comments(self, comments: list[dict]) -> dict:
        """
        댓글 기본 분석 (Rule-based Fast Analysis)
        """
        log_step("댓글 기본 분석", "시작", f"{len(comments)}개 댓글")

        if not comments:
            return self._empty_result()

        # 댓글 텍스트 추출
        texts = [c.get("text", "") for c in comments if c.get("text")]

        # 각 분석 수행
        sentiment = self._analyze_sentiment(texts)
        pain_points = self._extract_pain_points(texts)
        gain_points = self._extract_gain_points(texts)
        questions = self._extract_questions(texts)
        keywords = self._extract_keywords(texts)

        result = {
            "total_comments": len(comments),
            "sentiment": sentiment,
            "pain_points": pain_points,
            "gain_points": gain_points,
            "questions": questions,
            "top_keywords": keywords,
            "summary": self._generate_summary(sentiment, pain_points, gain_points),
            "ai_analysis": None,  # AI 분석 결과 공간 확보
        }

        log_success(
            f"댓글 기본 분석 완료: 긍정 {sentiment['positive']}%, 부정 {sentiment['negative']}%"
        )
        return result

    def analyze_with_ai(self, comments: list[dict]) -> dict:
        """
        AI를 활용한 심층 댓글 분석 (Deep Analysis)
        - Rule-based 분석 결과에 AI 인사이트를 통합합니다.
        """
        # 1. 기본 분석 먼저 수행
        base_result = self.analyze_comments(comments)

        if not self._gemini or not comments:
            return base_result

        # [NEW] X-Algorithm Pipeline 실행
        if self.pipeline:
            try:
                import asyncio

                # 이미 실행 중인 이벤트 루프가 있는지 확인
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # 이미 루프가 있으면 (예: Streamlit이 비동기로 도는 경우) create_task 등을 써야 하는데,
                    # 동기 함수 내라서 await를 못 씀.
                    # 이 경우엔 nest_asyncio 같은 게 필요한데, 일단 간단히 run_pipeline이 async이므로
                    # 동기 래퍼가 필요함.
                    # 여기서는 안전하게 별도 스레드나 nest_asyncio를 가정하지 않고,
                    # 만약 루프가 없다면 run()을, 있다면... 복잡함.
                    # 간단하게: Streamlit은 보통 메인 스레드에서 돌고 루프가 없는 경우가 많음.
                    pipeline_result = self._run_async(self.pipeline.run_pipeline(comments))
                else:
                    pipeline_result = self._run_async(self.pipeline.run_pipeline(comments))

                if pipeline_result and "insights" in pipeline_result:
                    base_result["x_algorithm_insights"] = pipeline_result["insights"]
                    base_result["x_algorithm_stats"] = pipeline_result["stats"]
                    log_success(
                        f"X-Algorithm Pipeline 완료: {len(pipeline_result['insights'])}개 인사이트 도출"
                    )

            except Exception as e:
                logger.error(f"X-Algorithm Pipeline Error: {e}")

        log_step("AI 심층 분석", "Gemini Pro", "고객 니즈/페인포인트 추출 중...")

        # 2. 분석용 텍스트 준비 (상위 50~100개 댓글 w/ filtering)
        # 너무 짧은 댓글(3글자 미만) 제외
        valid_comments = [
            c.get("text", "") for c in comments if len(c.get("text", "")) > 3
        ]
        sample_texts = valid_comments[:70]  # 비용 최적화를 위해 상위 70개만 분석
        combined_text = "\n- ".join(sample_texts)
        log_llm_request("댓글 심층 분석", f"댓글 {len(sample_texts)}개 요약, 프롬프트 {len(combined_text)}자")

        # 3. 프롬프트 엔지니어링 (Insight Extraction)
        prompt = prompt_registry.get("comment.analysis").render(
            combined_text=combined_text
        )

        try:
            # 4. Gemini 호출 (Retry Logic 포함)
            response_text = self._gemini.generate_text(prompt, temperature=0.4)

            # 5. 결과 검증 및 정화
            ai_data = validate_json_output(
                response_text, required_fields=["deep_pain_points", "marketing_hooks"]
            )

            # 6. 결과 통합
            base_result["ai_analysis"] = ai_data

            # AI 요약이 있다면 최상위 요약 덮어쓰기 (더 정확하므로)
            if "executive_summary" in ai_data:
                base_result["summary"] = f"[AI] {ai_data['executive_summary']}"

            log_llm_response("댓글 심층 분석", f"응답 {len(response_text)}자, 인사이트 추출 완료")
            log_success("AI 심층 분석 완료")
            return base_result

        except Exception as e:
            log_llm_fail("댓글 심층 분석", str(e))
            logger.error(f"AI 댓글 분석 실패: {e}")
            # 실패 시 기본 결과 반환 (서비스 중단 방지)
            base_result["ai_analysis"] = {"error": str(e)}
            return base_result

    def _run_async(self, coro):
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()

        return asyncio.run(coro)

    def _empty_result(self) -> dict:
        """빈 결과 반환"""
        return {
            "total_comments": 0,
            "sentiment": {"positive": 0, "negative": 0, "neutral": 100},
            "pain_points": [],
            "gain_points": [],
            "questions": [],
            "top_keywords": [],
            "summary": "분석할 댓글이 없습니다.",
            "ai_analysis": None,
        }

    def _analyze_sentiment(self, texts: list[str]) -> dict:
        """감정 분석 (긍정/부정/중립 비율)"""
        positive_count = 0
        negative_count = 0

        for text in texts:
            text_lower = text.lower()

            has_positive = any(kw in text_lower for kw in POSITIVE_KEYWORDS)
            has_negative = any(kw in text_lower for kw in NEGATIVE_KEYWORDS)

            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative and not has_positive:
                negative_count += 1

        total = len(texts) if texts else 1
        neutral_count = total - positive_count - negative_count

        return {
            "positive": round(positive_count / total * 100, 1),
            "negative": round(negative_count / total * 100, 1),
            "neutral": round(neutral_count / total * 100, 1),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
        }

    def _extract_pain_points(self, texts: list[str], max_count: int = 5) -> list[str]:
        """페인포인트 추출"""
        pain_comments = []

        for text in texts:
            # 페인 키워드가 포함된 댓글 수집
            if any(kw in text for kw in PAIN_KEYWORDS):
                # 너무 짧은 댓글 제외
                if len(text) > 10:
                    pain_comments.append(text[:100])  # 100자로 제한

        # 중복 제거 및 상위 N개 반환
        unique_pains = list(set(pain_comments))
        return unique_pains[:max_count]

    def _extract_gain_points(self, texts: list[str], max_count: int = 5) -> list[str]:
        """긍정적 피드백(Gain Points) 추출"""
        gain_comments = []

        for text in texts:
            # 긍정 키워드가 포함된 댓글 수집
            if any(kw in text.lower() for kw in POSITIVE_KEYWORDS):
                if len(text) > 10:
                    gain_comments.append(text[:100])

        unique_gains = list(set(gain_comments))
        return unique_gains[:max_count]

    def _extract_questions(self, texts: list[str], max_count: int = 5) -> list[str]:
        """자주 묻는 질문 추출"""
        questions = []

        for text in texts:
            # 질문 패턴 매칭
            for pattern in QUESTION_PATTERNS:
                if re.search(pattern, text):
                    if len(text) > 5 and len(text) < 200:
                        questions.append(text)
                    break

        unique_questions = list(set(questions))
        return unique_questions[:max_count]

    def _extract_keywords(self, texts: list[str], max_count: int = 10) -> list[dict]:
        """핵심 키워드 추출"""
        # 모든 텍스트 합치기
        all_text = " ".join(texts)

        # 간단한 단어 빈도 분석 (2글자 이상)
        words = re.findall(r"[가-힣a-zA-Z]{2,}", all_text)

        # 불용어 제거
        stopwords = {
            "그리고",
            "하지만",
            "그래서",
            "근데",
            "이거",
            "저거",
            "the",
            "and",
            "is",
            "it",
        }
        filtered_words = [w for w in words if w.lower() not in stopwords]

        # 빈도 계산
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(max_count)

        return [{"word": word, "count": count} for word, count in top_words]

    def _generate_summary(
        self,
        sentiment: dict,
        pain_points: list[str],
        gain_points: list[str],
    ) -> str:
        """분석 요약 생성"""
        positive_pct = sentiment["positive"]
        negative_pct = sentiment["negative"]

        # 감정 요약
        if positive_pct > 60:
            sentiment_summary = "전반적으로 매우 긍정적인 반응"
        elif positive_pct > 40:
            sentiment_summary = "긍정적 반응이 우세"
        elif negative_pct > 40:
            sentiment_summary = "부정적 반응에 주의 필요"
        else:
            sentiment_summary = "중립적인 반응이 대다수"

        # 페인포인트 요약
        pain_summary = ""
        if pain_points:
            pain_summary = f" 주요 고민: {len(pain_points)}개 발견."

        return f"{sentiment_summary}.{pain_summary}"

    def get_marketing_phrases(self, comments: list[dict]) -> list[str]:
        """
        마케팅에 활용할 수 있는 고객 언어 추출

        Args:
            comments: YouTube 댓글 리스트

        Returns:
            마케팅 문구로 활용 가능한 표현들
        """
        phrases = []

        for comment in comments:
            text = comment.get("text", "")
            likes = comment.get("likes", 0)

            # 좋아요가 많은 긍정적 댓글에서 문구 추출
            if likes >= 5 and any(kw in text.lower() for kw in POSITIVE_KEYWORDS):
                # 인용할 만한 짧은 문장 추출
                sentences = re.split(r"[.!?]", text)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if 10 < len(sentence) < 50:
                        phrases.append(f'"{sentence}"')

        return phrases[:10]  # 상위 10개
