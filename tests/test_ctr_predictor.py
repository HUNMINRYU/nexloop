import services.ctr_predictor as ctr_predictor
from services.ctr_predictor import CTRPredictor


def test_predict_ctr_returns_expected_keys():
    predictor = CTRPredictor()
    result = predictor.predict_ctr(
        title="충격! 3가지 방법으로 개선하는 비결",
        thumbnail_description="밝은 배경, 큰 텍스트, 얼굴 강조",
        competitor_titles=["제품 소개", "비교 리뷰"],
    )

    assert "predicted_ctr" in result
    assert "total_score" in result
    assert "breakdown" in result
    assert "recommendations" in result
    assert "grade" in result


def test_predict_ctr_breakdown_fields():
    predictor = CTRPredictor()
    result = predictor.predict_ctr(title="간단한 테스트 제목")
    breakdown = result["breakdown"]

    assert set(breakdown.keys()) == {
        "title_length",
        "emoji_usage",
        "hook_strength",
        "thumbnail",
        "differentiation",
    }


def test_predict_ctr_grade_bounds():
    predictor = CTRPredictor()
    result = predictor.predict_ctr(title="긴급 경고! 반드시 확인하세요")
    assert result["grade"] in {"S", "A", "B", "C", "D"}


def test_predict_ctr_logs(monkeypatch):
    class DummyEvaluator:
        def __init__(self) -> None:
            self.logged = []

        def log_prediction(self, model_name, input_data, output, ground_truth=None):
            self.logged.append((model_name, input_data, output, ground_truth))

    evaluator = DummyEvaluator()
    monkeypatch.setattr(ctr_predictor, "ModelEvaluator", lambda: evaluator)

    predictor = CTRPredictor()
    predictor.predict_ctr(title="로그 테스트")
    assert evaluator.logged
