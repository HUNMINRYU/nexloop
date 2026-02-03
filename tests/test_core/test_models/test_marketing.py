import pytest
from pydantic import ValidationError

from core.models.marketing import HookingPoint, MarketingStrategy, TargetPersona


def test_target_persona_requires_primary():
    with pytest.raises(ValidationError):
        TargetPersona()
    persona = TargetPersona(primary="고객", pain_points=["문제"])
    assert persona.primary == "고객"


def test_hooking_point_score_bounds():
    HookingPoint(hook="훅", hook_type="loss_aversion", viral_score=0)
    with pytest.raises(ValidationError):
        HookingPoint(hook="훅", hook_type="loss_aversion", viral_score=101)


def test_marketing_strategy_serialization():
    strategy = MarketingStrategy(product_name="테스트", summary="요약")
    dumped = strategy.model_dump()
    assert "generated_at" in dumped
