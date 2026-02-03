from core.exceptions import ErrorCode, NexloopError, classify_error


def test_classify_error_network():
    err = classify_error(Exception("network timeout"))
    assert err.code == ErrorCode.NETWORK_ERROR


def test_classify_error_auth():
    err = classify_error(Exception("403 forbidden"))
    assert err.code == ErrorCode.AUTH_FAILED


def test_classify_error_rate_limit():
    err = classify_error(Exception("rate limit exceeded"))
    assert err.code == ErrorCode.API_RATE_LIMIT


def test_classify_error_data_not_found():
    err = classify_error(Exception("not found"))
    assert err.code == ErrorCode.DATA_NOT_FOUND


def test_classify_error_json():
    err = classify_error(Exception("json parse error"))
    assert err.code == ErrorCode.DATA_PARSE_ERROR


def test_nexloop_error_full_message():
    err = NexloopError(code=ErrorCode.CONFIG_MISSING)
    assert "설정 파일" in err.get_full_message()
