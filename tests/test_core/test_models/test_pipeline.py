import pytest
from pydantic import ValidationError

from core.models.pipeline import PipelineConfig, PipelineProgress, PipelineStep


def test_pipeline_config_defaults():
    config = PipelineConfig()
    assert config.youtube_count == 3
    assert config.naver_count == 10
    assert config.include_comments is True
    assert config.generate_thumbnail is True


def test_pipeline_config_validation():
    with pytest.raises(ValidationError):
        PipelineConfig(youtube_count=0)
    with pytest.raises(ValidationError):
        PipelineConfig(naver_count=1)


def test_pipeline_progress_configure_steps():
    config = PipelineConfig(
        generate_social=False,
        generate_thumbnail=False,
        generate_video=False,
        upload_to_gcs=False,
    )
    progress = PipelineProgress()
    progress.configure_steps(config)
    assert progress.total_steps == 6
    progress.update(PipelineStep.STRATEGY_GENERATION, "done")
    assert progress.percentage > 0
    progress.update(PipelineStep.COMPLETED, "done")
    assert progress.percentage == 100
