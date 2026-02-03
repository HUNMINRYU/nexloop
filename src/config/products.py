"""
블루가드 제품 카탈로그
"""
from typing import Final

from core.models.product import Product, ProductCategory

# 블루가드 제품 목록 (15개)
BLUEGUARD_PRODUCTS: Final[list[dict]] = [
    {
        "name": "벅스델타",
        "category": ProductCategory.PEST_CONTROL,
        "description": "델타메트린 기반 희석형 광역살충제",
        "target": "모든 해충",
        "visual_description": "a white plastic spray bottle with a green label held by a hand",
    },
    {
        "name": "벅스델타S",
        "category": ProductCategory.PEST_CONTROL,
        "description": "델타메트린 기반 스프레이형 즉석 살충제",
        "target": "모든 해충",
    },
    {
        "name": "벅스라인 산제",
        "category": ProductCategory.PEST_CONTROL,
        "description": "라인 도포형 가루 살충제",
        "target": "보행해충",
    },
    {
        "name": "블루가드 바퀴벌레겔",
        "category": ProductCategory.COCKROACH,
        "description": "연쇄 살충효과 먹이겔",
        "target": "바퀴벌레",
    },
    {
        "name": "블루가드 좀벌레트랩",
        "category": ProductCategory.TRAP,
        "description": "좀벌레 전문 끈끈이 트랩",
        "target": "좀벌레",
    },
    {
        "name": "블루가드 화랑곡나방트랩",
        "category": ProductCategory.TRAP,
        "description": "페로몬 유인 끈끈이 트랩",
        "target": "나방",
    },
    {
        "name": "뱀이싹",
        "category": ProductCategory.REPELLENT,
        "description": "천연유래물질 성분 뱀 기피제",
        "target": "뱀",
    },
    {
        "name": "쥐싹킬",
        "category": ProductCategory.RODENTICIDE,
        "description": "나가서 말라죽는 알약형 쥐약",
        "target": "쥐",
    },
    {
        "name": "싹보내 퇴치기",
        "category": ProductCategory.DEVICE,
        "description": "지진파 원리 두더지/뱀 퇴치기",
        "target": "두더지/뱀",
    },
    {
        "name": "싹보내G 퇴치기",
        "category": ProductCategory.DEVICE,
        "description": "3중 퇴치 야생동물용",
        "target": "야생동물",
    },
    {
        "name": "모기싹",
        "category": ProductCategory.PEST_CONTROL,
        "description": "모기 퇴치 전문 제품",
        "target": "모기",
    },
    {
        "name": "개미싹",
        "category": ProductCategory.PEST_CONTROL,
        "description": "개미 퇴치 전문 제품",
        "target": "개미",
    },
    {
        "name": "파리싹",
        "category": ProductCategory.PEST_CONTROL,
        "description": "파리 퇴치 전문 제품",
        "target": "파리",
    },
    {
        "name": "냄새싹",
        "category": ProductCategory.DEODORIZER,
        "description": "강력 탈취 제품",
        "target": "악취",
    },
    {
        "name": "블루가드올인원",
        "category": ProductCategory.GENERAL,
        "description": "다기능 통합 솔루션",
        "target": "다용도",
    },
]


def get_product_catalog() -> list[Product]:
    """Product 객체 리스트 반환"""
    return [Product(**p) for p in BLUEGUARD_PRODUCTS]


def get_product_names() -> list[str]:
    """제품명 리스트 반환"""
    return [p["name"] for p in BLUEGUARD_PRODUCTS]


def get_product_by_name(name: str) -> Product | None:
    """이름으로 제품 검색"""
    for p in BLUEGUARD_PRODUCTS:
        if p["name"] == name:
            return Product(**p)
    return None
