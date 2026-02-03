"""
제품 도메인 모델
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductCategory(str, Enum):
    """제품 카테고리"""

    PEST_CONTROL = "해충방제"
    COCKROACH = "바퀴벌레"
    TRAP = "트랩"
    REPELLENT = "기피제"
    RODENTICIDE = "쥐약"
    DEVICE = "퇴치기"
    DEODORIZER = "탈취/방향"
    GENERAL = "종합"


class Product(BaseModel):
    """제품 도메인 모델"""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, description="제품명")
    category: ProductCategory = Field(..., description="제품 카테고리")
    description: str = Field(..., description="제품 설명")
    target: str = Field(..., description="대상 해충/문제")
    visual_description: Optional[str] = Field(
        default=None,
        description="썸네일용 제품 시각 묘사 (예: white spray bottle with green label). 없으면 generic product packaging 사용",
    )

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        d = {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "target": self.target,
        }
        if self.visual_description is not None:
            d["visual_description"] = self.visual_description
        return d


class ProductCatalog(BaseModel):
    """제품 카탈로그"""

    products: list[Product] = Field(default_factory=list)

    def get_by_name(self, name: str) -> Optional[Product]:
        """이름으로 제품 검색"""
        return next((p for p in self.products if p.name == name), None)

    def get_by_category(self, category: ProductCategory) -> list[Product]:
        """카테고리별 제품 검색"""
        return [p for p in self.products if p.category == category]

    def get_names(self) -> list[str]:
        """모든 제품명 반환"""
        return [p.name for p in self.products]

    def __len__(self) -> int:
        return len(self.products)
