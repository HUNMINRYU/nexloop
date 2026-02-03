"""
네이버 쇼핑 관련 도메인 모델
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NaverProduct(BaseModel):
    """네이버 쇼핑 상품 모델"""

    product_id: str = Field(..., description="상품 ID")
    title: str = Field(..., description="상품명")
    link: str = Field(..., description="상품 링크")
    image: Optional[str] = Field(default=None, description="이미지 URL")
    price: int = Field(default=0, ge=0, description="최저가")
    mall_name: str = Field(default="", description="판매처")
    brand: str = Field(default="", description="브랜드")
    category1: str = Field(default="", description="카테고리1")
    category2: str = Field(default="", description="카테고리2")
    category3: str = Field(default="", description="카테고리3")
    category4: str = Field(default="", description="카테고리4")

    @property
    def full_category(self) -> str:
        """전체 카테고리 경로"""
        categories = [c for c in [self.category1, self.category2, self.category3, self.category4] if c]
        return " > ".join(categories)


class CompetitorStats(BaseModel):
    """경쟁사 통계"""

    total_products: int = Field(default=0, ge=0, description="총 상품 수")
    min_price: int = Field(default=0, ge=0, description="최저가")
    max_price: int = Field(default=0, ge=0, description="최고가")
    avg_price: float = Field(default=0.0, ge=0, description="평균가")
    top_brands: list[str] = Field(default_factory=list, description="상위 브랜드")
    top_malls: list[str] = Field(default_factory=list, description="상위 판매처")
    price_distribution: dict[str, int] = Field(default_factory=dict, description="가격대별 분포")


class NaverSearchResult(BaseModel):
    """네이버 쇼핑 검색 결과"""

    query: str = Field(..., description="검색 쿼리")
    products: list[NaverProduct] = Field(default_factory=list, description="검색된 상품 목록")
    competitor_stats: Optional[CompetitorStats] = Field(default=None, description="경쟁사 통계")
    collected_at: datetime = Field(default_factory=datetime.now, description="수집 시간")

    @property
    def product_count(self) -> int:
        """상품 수"""
        return len(self.products)
