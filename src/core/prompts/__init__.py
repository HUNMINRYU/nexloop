"""프롬프트 템플릿/레지스트리"""
from __future__ import annotations


class PromptTemplate:
    def __init__(self, name: str, template: str, version: str = "v1") -> None:
        self.name = name
        self.template = template
        self.version = version

    def render(self, **kwargs) -> str:
        return self.template.format_map(kwargs)


class PromptRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {}

    def register(self, template: PromptTemplate) -> None:
        self._templates[template.name] = template

    def get(self, name: str) -> PromptTemplate:
        if name not in self._templates:
            raise KeyError(f"등록되지 않은 프롬프트: {name}")
        return self._templates[name]


prompt_registry = PromptRegistry()

__all__ = ["PromptTemplate", "PromptRegistry", "prompt_registry"]
