from services.market_trend_service import MarketTrendService


class DummyRagClient:
    def search(
        self,
        query: str,
        max_results: int = 5,
        data_store_id: str | None = None,
    ) -> list[dict]:
        return [
            {"title": "title1", "snippet": "snippet1", "url": "http://example.com/1"},
            {"title": "title2", "snippet": "snippet2", "url": "http://example.com/2"},
            {"title": "title3", "snippet": "snippet3", "url": "http://example.com/3"},
        ]

    def upsert_documents(
        self,
        documents: list[dict],
        data_store_id: str | None = None,
    ) -> int:
        return len(documents)

    def is_configured(self) -> bool:
        return True


def test_market_trend_service_extracts_issues(sample_product):
    service = MarketTrendService(rag_client=DummyRagClient())
    result = service.get_market_trends(sample_product)
    assert result["issues"]
    assert result["issues"][0]["title"] == "title1"
