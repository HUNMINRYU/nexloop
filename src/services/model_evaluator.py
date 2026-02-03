"""
모델 평가 및 로깅
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ModelEvaluator:
    """모델 성능 평가 및 추적"""

    def __init__(self, output_dir: str = "outputs/evaluations") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log_prediction(
        self,
        model_name: str,
        input_data: dict,
        output: dict,
        ground_truth: Optional[dict] = None,
    ) -> None:
        record = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "input": input_data,
            "output": output,
            "ground_truth": ground_truth,
        }
        log_file = self.output_dir / f"{model_name}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def compare_models(self, model_a: str, model_b: str) -> Dict:
        return {
            "model_a": model_a,
            "model_b": model_b,
            "comparison": "구현 예정",
        }

    def generate_report(self) -> str:
        report_lines = [
            "# 모델 평가 보고서",
            f"생성 시각: {datetime.now().isoformat()}",
            "",
        ]
        for log_file in self.output_dir.glob("*.jsonl"):
            count = sum(1 for _ in log_file.open(encoding="utf-8"))
            report_lines.append(f"- {log_file.stem}: {count}건")
        return "\n".join(report_lines)
