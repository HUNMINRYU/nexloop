"""
후킹 서비스
AI 기반 마케팅 후킹 문구 자동 생성
"""

from utils.logger import get_logger, log_llm_fail, log_llm_request, log_llm_response, log_step, log_success

logger = get_logger(__name__)

# === 훅 전략 프리셋 (9종, UI 표기용 label + LLM 프롬프트용 instruction) ===
HOOK_STRATEGIES = [
    {"key": "curiosity", "label": "Curiosity (호기심)", "instruction": "Write a clickbait hook that teases a secret or hidden truth without revealing it immediately. Make the user curious."},
    {"key": "loss_aversion", "label": "Loss Aversion (손실 회피)", "instruction": "Emphasize the negative consequences or money/health lost by NOT using the product. Focus on pain points."},
    {"key": "social_proof", "label": "Social Proof (사회적 증명)", "instruction": "Highlight popularity, user reviews, or 'everyone is doing it' mentality. Use numbers or rankings."},
    {"key": "authority", "label": "Authority (권위)", "instruction": "Use a tone of expert recommendation, scientific backing, or official certification to build trust."},
    {"key": "scarcity", "label": "Scarcity (희소성)", "instruction": "Emphasize limited quantity, limited stock, or exclusive access to make the product feel rare."},
    {"key": "zeigarnik", "label": "Zeigarnik (미완성 효과)", "instruction": "Start a sentence but leave the conclusion open-ended (ellipsis...), forcing the user to click to finish the thought."},
    {"key": "urgency", "label": "Urgency (긴급성)", "instruction": "Create a sense of immediate time pressure. Use words like 'Now', 'Today only', 'Ends soon'."},
    {"key": "negativity", "label": "Negativity (공포/충격)", "instruction": "Shock the viewer with a scary fact or worst-case scenario related to the pest problem. High emotional impact."},
    {"key": "benefit", "label": "Benefit (즉각적 혜택)", "instruction": "Focus purely on the positive, instant result. No fluff, just the dream outcome realized immediately."},
]

# === 후킹 스타일 템플릿 (LLM 폴백·비디오 등에서 사용) ===
HOOK_STYLES = {
    "curiosity": {
        "name": "호기심형",
        "emoji": "🤔",
        "templates": [
            "99%가 모르는 {product}의 비밀",
            "{product} 이렇게 쓰면 효과 2배",
            "전문가들만 아는 {product} 활용법",
            "{benefit} 하려면 이것만 기억하세요",
        ],
        "description": "시청자의 호기심을 자극하여 끝까지 시청하게 만듦",
    },
    "fear": {
        "name": "공포형",
        "emoji": "😱",
        "templates": [
            "이거 안 쓰면 {pain_point} 계속됩니다",
            "{pain_point} 방치하면 이렇게 됩니다",
            "아직도 {wrong_method} 하세요? 큰일납니다",
            "{product} 없이 버티다간...",
        ],
        "description": "문제를 방치했을 때의 결과를 보여줌",
    },
    "reversal": {
        "name": "반전형",
        "emoji": "😮",
        "templates": [
            "처음엔 의심했는데... {benefit}",
            "솔직히 안 믿었어요, 근데 {result}",
            "이게 된다고? {product} 써보니까...",
            "거짓말인 줄 알았는데 {benefit} 실화",
        ],
        "description": "의심에서 확신으로의 전환 스토리",
    },
    "question": {
        "name": "질문형",
        "emoji": "❓",
        "templates": [
            "{pain_point} 고민이시죠?",
            "혹시 {pain_point} 때문에 고민 중이세요?",
            "{wrong_method} 하고 계신가요?",
            "{benefit} 원하시나요?",
        ],
        "description": "시청자의 고민에 공감하며 시작",
    },
    "urgency": {
        "name": "긴급형",
        "emoji": "⚡",
        "templates": [
            "지금 안 보면 후회합니다",
            "오늘만 공개되는 {product} 비법",
            "이 영상 내리기 전에 꼭 보세요",
            "{benefit} 원하면 지금 당장!",
        ],
        "description": "긴급함을 강조하여 즉시 행동 유도",
    },
    # === 심리 모델 (Marketing Psychology) ===
    "loss_aversion": {
        "name": "손실 회피형",
        "emoji": "📉",
        "templates": [
            "이 기회 놓치면 {loss} 손해봅니다",
            "오늘 지나면 혜택이 사라져요",
            "남들 다 {benefit} 받는데 혼자만...",
            "지금 안 쓰면 나중에 후회합니다",
        ],
        "description": "얻는 기쁨보다 잃는 고통이 2배 더 크다는 심리 활용",
    },
    "social_proof": {
        "name": "사회적 증거형",
        "emoji": "👥",
        "templates": [
            "이미 10만 명이 선택한 {product}",
            "왜 다들 {product} 이야기만 할까요?",
            "인기 폭발! {product} 써본 사람들 반응",
            "요즘 핫한 {product}, 이유가 있네요",
        ],
        "description": "남들도 다 쓴다! 대세감을 조성하여 안심시킴",
    },
    "authority": {
        "name": "권위 활용형",
        "emoji": "👨‍⚕️",
        "templates": [
            "전문가가 추천하는 {product} 사용법",
            "업계 1위가 {product} 선택한 이유",
            "의사/전문가들도 인정한 {benefit} 비결",
            "연구 결과로 증명된 {product} 효과",
        ],
        "description": "권위자의 추천이나 데이터를 통해 신뢰도 확보",
    },
    "scarcity": {
        "name": "희소성 강조형",
        "emoji": "⏳",
        "templates": [
            "딱 100개만 남았습니다",
            "지금 아니면 구할 수 없는 {product}",
            "재입고 문의 폭주! 품절 임박",
            "이번 달만 가능한 {benefit} 혜택",
        ],
        "description": "부족함을 강조하여 소유욕과 긴박감 자극",
    },
    "zeigarnik": {
        "name": "미완성 효과형",
        "emoji": "🧩",
        "templates": [
            "{product}의 숨겨진 기능 하나만 알면...",
            "이것만 알았어도 {pain_point} 없었을 텐데",
            "딱 하나만 바꿨는데 {benefit} 대박남",
            "99%가 놓치고 있는 {product} 사용 꿀팁",
        ],
        "description": "문장을 미완성처럼 느끼게 하여 궁금증 극대화",
    },
    "negativity": {
        "name": "공포/충격형",
        "emoji": "😱",
        "templates": [
            "자면서 바퀴벌레 먹을 확률 70%",
            "이거 안 쓰면 {pain_point} 계속됩니다",
            "{pain_point} 방치하면 이렇게 됩니다",
            "{product} 없이 버티다간...",
        ],
        "description": "부정적 상황(공포, 혐오)을 보여주어 해결책을 찾게 함",
    },
    "benefit": {
        "name": "즉각적 혜택형",
        "emoji": "✨",
        "templates": [
            "뿌리자마자 1초 만에 전멸",
            "{product} 하나로 {benefit}",
            "복잡한 과정 없이 {benefit}",
            "바로 느껴지는 {benefit}",
        ],
        "description": "복잡한 과정 없이 바로 얻을 수 있는 보상 강조",
    },
}


class HookService:
    """AI 기반 후킹 문구 생성 서비스"""

    def __init__(self, gemini_client=None) -> None:
        """
        Args:
            gemini_client: AI 기반 맞춤 후킹 생성 시 사용 (선택)
        """
        self._gemini = gemini_client

    def get_available_styles(self) -> list[dict]:
        """사용 가능한 후킹 스타일 목록 반환 (9종, UI 표기용 label)"""
        result = []
        for s in HOOK_STRATEGIES:
            key = s["key"]
            style = HOOK_STYLES.get(key, {})
            result.append({
                "key": key,
                "name": s["label"],
                "emoji": style.get("emoji", ""),
                "description": style.get("description", ""),
            })
        return result

    def generate_hooks(
        self,
        style: str,
        product: dict,
        pain_points: list[str] = None,
        count: int = 3,
    ) -> list[str]:
        """
        특정 스타일의 후킹 문구 생성.
        LLM에 제품·제품설명을 전달해 생성 요청하고, 실패 시 템플릿 폴백.
        """
        p_name = product.get("name", "제품")
        p_desc = (product.get("description") or "").strip()
        p_target = (product.get("target") or "").strip()
        strategy = next((s for s in HOOK_STRATEGIES if s["key"] == style), None)
        style_normalized = style if style in HOOK_STYLES else "curiosity"
        style_name = HOOK_STYLES[style_normalized]["name"]
        instruction = strategy["instruction"] if strategy else None

        # 1) LLM에 제품·제품설명 전달 후 훅 생성 요청
        if self._gemini and hasattr(self._gemini, "generate_text"):
            log_llm_request(
                "훅 생성",
                f"LLM에게 제품·제품설명 전달, 스타일: {style_name}({style}), {count}개 요청 (제품: {p_name})",
            )
            strategy_instruction = (
                f"\n[Copywriting strategy (follow this)]\n{instruction}\n"
                if instruction else ""
            )
            prompt = f"""당신은 숏폼 광고 훅 문구 전문가입니다. 아래 제품 정보를 보고, "{style_name}" 스타일에 맞는 썸네일/광고용 훅 문구를 한글로 정확히 {count}개만 생성하세요.{strategy_instruction}

[제품 정보]
- 제품명: {p_name}
- 제품 설명: {p_desc or "(없음)"}
- 대상: {p_target or "(없음)"}

[규칙]
- 각 줄에 훅 문구 하나만 출력 (번호·불릿 없이)
- 10~15자 이내로 짧고 강렬하게
- 마크다운·코드블록 없이 텍스트만 출력

[출력 예시]
지금 안 쓰면 후회합니다
이미 10만 명이 선택한 {p_name}
"""
            try:
                response = self._gemini.generate_text(prompt, temperature=0.6)
                lines = [line.strip() for line in (response or "").strip().split("\n") if line.strip()]
                # 번호/불릿 제거
                hooks = []
                for line in lines[: count + 5]:
                    clean = line.lstrip("0123456789.-) ").strip()
                    if clean and len(clean) <= 25:
                        hooks.append(clean)
                        if len(hooks) >= count:
                            break
                if hooks:
                    log_llm_response("훅 생성", f"LLM이 제품·설명 반영해 {len(hooks)}개 생성 완료")
                    return hooks[:count]
            except Exception as e:
                log_llm_fail("훅 생성", str(e))
                logger.warning(f"LLM 훅 생성 실패, 템플릿 폴백: {e}")

        # 2) 폴백: 템플릿 기반 생성
        log_step("후킹 생성", style, f"제품: {p_name} (템플릿 폴백)")
        style_data = HOOK_STYLES[style_normalized]
        templates = style_data["templates"]
        p_benefit = product.get("benefit") or p_desc or p_target or "효과를 경험"
        if len(p_benefit) > 20:
            p_benefit = p_benefit[:18].rsplit(" ", 1)[0] or p_benefit[:18]
        pain_point = "고민"
        if pain_points and len(pain_points) > 0:
            pain_point = pain_points[0]
        elif product.get("pain_points"):
            pain_point = product["pain_points"][0]
        elif p_target:
            pain_point = p_target if len(p_target) <= 8 else p_target.replace("모든 ", "").split("/")[0].strip()
        format_kwargs = {
            "product": p_name,
            "benefit": p_benefit,
            "pain_point": pain_point,
            "wrong_method": "기존 방법",
            "result": "진짜 효과가 있더라",
            "loss": "큰",
            "count": "10만",
            "discount": "30",
        }
        hooks = [templates[i].format(**format_kwargs) for i in range(min(count, len(templates)))]
        log_success(f"{len(hooks)}개 후킹 문구 생성 완료 (템플릿)")
        return hooks

    # === Marketing Psychology Methods (Skill 적용) ===

    def generate_loss_aversion_hooks(self, product: dict, count: int = 3) -> list[str]:
        """손실 회피(Loss Aversion) 모델 적용 훅 생성"""
        return self.generate_hooks("loss_aversion", product, count=count)

    def generate_social_proof_hooks(self, product: dict, count: int = 3) -> list[str]:
        """사회적 증거(Social Proof) 모델 적용 훅 생성"""
        return self.generate_hooks("social_proof", product, count=count)

    def generate_authority_hooks(self, product: dict, count: int = 3) -> list[str]:
        """권위(Authority) 모델 적용 훅 생성"""
        return self.generate_hooks("authority", product, count=count)

    def generate_scarcity_hooks(self, product: dict, count: int = 3) -> list[str]:
        """희소성(Scarcity) 모델 적용 훅 생성"""
        return self.generate_hooks("scarcity", product, count=count)

    def generate_zeigarnik_hooks(self, product: dict, count: int = 3) -> list[str]:
        """자이가르닉(Zeigarnik) 효과 모델 적용 훅 생성"""
        return self.generate_hooks("zeigarnik", product, count=count)

    def generate_multi_style_hooks(
        self,
        product: dict,
        pain_points: list[str] = None,
        styles: list[str] = None,
    ) -> dict[str, list[str]]:
        """
        여러 스타일의 후킹 문구 일괄 생성

        Args:
            product: 제품 정보
            pain_points: 페인포인트 목록
            styles: 생성할 스타일 목록 (None이면 전체)

        Returns:
            {스타일: [후킹문구들]} 딕셔너리
        """
        if styles is None:
            styles = list(HOOK_STYLES.keys())

        results = {}
        for style in styles:
            results[style] = self.generate_hooks(
                style=style,
                product=product,
                pain_points=pain_points,
                count=2,  # 각 스타일당 2개
            )

        return results

    async def generate_ai_hooks(
        self,
        product: dict,
        pain_points: list[str],
        target_audience: dict,
        count: int = 5,
    ) -> list[str]:
        """
        AI(Gemini)를 활용한 맞춤 후킹 문구 생성

        Args:
            product: 제품 정보
            pain_points: 고객 페인포인트
            target_audience: 타겟 오디언스 정보
            count: 생성할 후킹 수

        Returns:
            AI가 생성한 후킹 문구 리스트
        """
        if not self._gemini:
            # AI 클라이언트 없으면 템플릿 기반으로 폴백
            return self.generate_hooks("curiosity", product, pain_points, count)

        prompt = f"""
당신은 숏폼 영상 마케팅 전문가입니다.
다음 제품에 대해 시청자의 시선을 사로잡는 후킹 문구 {count}개를 생성하세요.

## 제품 정보
- 제품명: {product.get("name", "N/A")}
- 카테고리: {product.get("category", "N/A")}
- 핵심 효과: {product.get("benefit", "N/A")}

## 타겟 오디언스
- 주요 타겟: {target_audience.get("primary", "일반 소비자")}
- 페인포인트: {", ".join(pain_points[:3]) if pain_points else "없음"}

## 요구사항
1. 첫 3초 안에 시청자를 사로잡아야 함
2. 15자 이내로 간결하게
3. 감정을 자극하는 단어 사용
4. 다양한 스타일 (호기심, 공포, 질문, 반전 등) 혼합

## 출력 형식
각 줄에 하나의 후킹 문구만 출력 (이모지 포함)
"""
        log_llm_request("AI 훅 생성", f"제품: {product.get('name', 'N/A')}, {count}개")
        try:
            response = await self._gemini.generate_text_async(prompt)
            hooks = [line.strip() for line in response.split("\n") if line.strip()]
            hooks = hooks[:count]
            log_llm_response("AI 훅 생성", f"{len(hooks)}개 생성 완료")
            return hooks
        except Exception as e:
            log_llm_fail("AI 훅 생성", str(e))
            logger.warning(f"AI 후킹 생성 실패, 템플릿 사용: {e}")
            return self.generate_hooks("curiosity", product, pain_points, count)

    def get_best_hooks_for_video(
        self,
        product: dict,
        video_style: str = "dramatic",
        pain_points: list[str] = None,
    ) -> list[dict]:
        """
        비디오 스타일에 맞는 최적의 후킹 조합 반환

        Args:
            product: 제품 정보
            video_style: 비디오 스타일 (dramatic, calm, horror 등)
            pain_points: 페인포인트

        Returns:
            [{style, hook, recommended_for}] 리스트
        """
        # 비디오 스타일별 추천 후킹 스타일
        style_mapping = {
            "dramatic": ["urgency", "reversal", "negativity"],
            "calm": ["question", "curiosity", "social_proof"],
            "horror": ["negativity", "urgency", "question"],
            "commercial": ["curiosity", "social_proof", "reversal"],
        }

        recommended_styles = style_mapping.get(
            video_style, ["curiosity", "negativity", "question"]
        )

        results = []
        for style in recommended_styles:
            style_key = style if style in HOOK_STYLES else "curiosity"
            hooks = self.generate_hooks(style_key, product, pain_points, count=1)
            if hooks:
                results.append(
                    {
                        "style": style_key,
                        "style_name": HOOK_STYLES[style_key]["name"],
                        "hook": hooks[0],
                        "recommended_for": video_style,
                    }
                )

        return results
