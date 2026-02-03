from services.comment_analysis_service import CommentAnalysisService


def test_comment_analysis_empty():
    service = CommentAnalysisService(gemini_client=None)
    result = service.analyze_comments([])
    assert result["total_comments"] == 0
    assert result["summary"] == "분석할 댓글이 없습니다."


def test_comment_analysis_basic():
    service = CommentAnalysisService(gemini_client=None)
    comments = [
        {"text": "정말 좋아요 추천합니다!", "likes": 3},
        {"text": "가격이 너무 비싸요", "likes": 1},
    ]
    result = service.analyze_comments(comments)
    assert result["total_comments"] == 2
    assert "sentiment" in result
