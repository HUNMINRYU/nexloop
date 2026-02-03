"""
애플리케이션 상수 정의
보안 정보 없음 - 순수 상수만 포함
"""
from typing import Final

# 썸네일 스타일
THUMBNAIL_STYLES: Final[list[str]] = [
    "드라마틱",
    "미니멀",
    "모던",
    "레트로",
    "네온",
    "자연",
]

# 색상 스킴
COLOR_SCHEMES: Final[list[str]] = [
    "블루 그라디언트",
    "레드 그라디언트",
    "그린 네이처",
    "골드 프리미엄",
    "모노크롬",
    "파스텔",
]

# 레이아웃
LAYOUTS: Final[list[str]] = [
    "중앙 집중형",
    "좌측 정렬",
    "우측 정렬",
    "대각선",
    "분할 레이아웃",
]

# 훅 심리학 타입
HOOK_TYPES: Final[list[str]] = [
    "loss_aversion",   # 손실 회피
    "social_proof",    # 사회적 증거
    "scarcity",        # 희소성
    "curiosity",       # 호기심
    "authority",       # 권위
    "benefit",         # 혜택 강조
]

# 훅 템플릿 (마케팅 심리학 기반)
HOOK_TEMPLATES: Final[dict[str, list[str]]] = {
    "loss_aversion": [
        "지금 안 사면 후회할 {product}",
        "이 기회를 놓치면 {product}",
        "{product} 품절 전 마지막 기회",
        "오늘만 이 가격! {product}",
    ],
    "social_proof": [
        "{count}명이 선택한 {product}",
        "후기 {count}개! {product}",
        "베스트셀러 {product}",
        "인기 TOP {product}",
    ],
    "scarcity": [
        "한정수량 {product}",
        "오늘만 {discount}% 할인!",
        "단 {count}개 남음!",
        "마감 임박 {product}",
    ],
    "curiosity": [
        "이게 바로 {product}의 비밀",
        "아직도 {product} 안 써봤어?",
        "{product}, 직접 써보니...",
        "충격! {product}의 진실",
    ],
    "authority": [
        "전문가가 추천하는 {product}",
        "셀럽이 선택한 {product}",
        "공식 인증 {product}",
        "1위 {product}",
    ],
    "benefit": [
        "{product}로 {benefit} 시작",
        "이제 {benefit}은 {product}로",
        "{product} 하나로 {benefit}",
        "{benefit}의 끝판왕 {product}",
    ],
}

# 비디오 설정
VIDEO_DURATIONS: Final[list[int]] = [8, 15, 30]
DEFAULT_VIDEO_DURATION: Final[int] = 8
DEFAULT_VIDEO_RESOLUTION: Final[str] = "720p"

# 데이터 수집 기본값
DEFAULT_YOUTUBE_COUNT: Final[int] = 3
DEFAULT_NAVER_COUNT: Final[int] = 10
MAX_YOUTUBE_COUNT: Final[int] = 10
MAX_NAVER_COUNT: Final[int] = 30

# 카메라 모션 (비디오 생성용)
CAMERA_MOTIONS: Final[list[str]] = [
    "static",
    "pan_left",
    "pan_right",
    "zoom_in",
    "zoom_out",
    "dolly_in",
    "dolly_out",
    "orbit",
    "tilt_up",
    "tilt_down",
]

# YouTube 언어 설정
YOUTUBE_LANGUAGES: Final[list[str]] = ["ko", "en"]

# 이미지 설정
DEFAULT_ASPECT_RATIO: Final[str] = "16:9"
SUPPORTED_ASPECT_RATIOS: Final[list[str]] = ["16:9", "9:16", "1:1", "4:3"]
