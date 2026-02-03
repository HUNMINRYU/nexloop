from pathlib import Path
import shutil

from services.model_evaluator import ModelEvaluator


def test_log_and_report():
    output_dir = Path("outputs/_test_evaluations")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    evaluator = ModelEvaluator(output_dir=str(output_dir))
    evaluator.log_prediction("test_model", {"input": "test"}, {"score": 0.8})
    report = evaluator.generate_report()
    assert "test_model" in report
    shutil.rmtree(output_dir)
