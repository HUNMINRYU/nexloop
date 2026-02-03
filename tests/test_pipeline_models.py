from core.models.pipeline import PipelineResult


def test_pipeline_result_defaults():
    result = PipelineResult(
        success=True,
        product_name="sample",
    )

    assert result.approval_status == "draft"
    assert result.audit_trail == []


def test_pipeline_result_allows_audit_trail_append():
    result = PipelineResult(
        success=True,
        product_name="sample",
        audit_trail=[{"action": "created"}],
    )
    assert result.audit_trail[0]["action"] == "created"
