import pytest

from services.data_validator import validate_comments


def test_valid_comment_passes():
    comments = [{"author": "user1", "text": "정말 유용한 영상입니다!", "likes": 10}]
    valid, report = validate_comments(comments)
    assert len(valid) == 1
    assert report.quality_score == 1.0


def test_spam_comment_rejected():
    comments = [{"author": "spammer", "text": "http://spam.com 클릭하세요", "likes": 0}]
    valid, report = validate_comments(comments)
    assert len(valid) == 0
    assert report.rejected_count == 1


def test_empty_text_rejected():
    comments = [{"author": "user", "text": "", "likes": 5}]
    valid, report = validate_comments(comments)
    assert len(valid) == 0
