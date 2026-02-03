from __future__ import annotations

from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)


class DiscoveryEngineClient:
    """Discovery Engine search + ingestion client."""

    def __init__(
        self,
        project_id: str,
        location: str,
        data_store_id: str | None,
        serving_config: str = "default_search",
        collection_id: str = "default_collection",
        branch_id: str = "default_branch",
    ) -> None:
        self._project_id = project_id
        self._location = location
        self._data_store_id = data_store_id
        self._serving_config = serving_config
        self._collection_id = collection_id
        self._branch_id = branch_id
        self._client = None
        self._document_client = None

    def _get_client(self):
        if self._client is None:
            from google.cloud import discoveryengine_v1beta as discoveryengine

            self._client = discoveryengine.SearchServiceClient()
        return self._client

    def _get_document_client(self):
        if self._document_client is None:
            from google.cloud import discoveryengine_v1beta as discoveryengine

            self._document_client = discoveryengine.DocumentServiceClient()
        return self._document_client

    def is_configured(self) -> bool:
        return bool(self._project_id and self._location and self._data_store_id)

    def _build_serving_config(self, data_store_id: str | None = None) -> str:
        client = self._get_client()
        store_id = data_store_id or self._data_store_id
        return client.serving_config_path(
            self._project_id,
            self._location,
            store_id,
            self._serving_config,
        )

    def _build_branch_path(self, data_store_id: str | None = None) -> str:
        store_id = data_store_id or self._data_store_id
        if not store_id:
            raise ValueError("data_store_id is required")
        client = self._get_document_client()
        if hasattr(client, "branch_path"):
            try:
                return client.branch_path(
                    self._project_id, self._location, store_id, self._branch_id
                )
            except TypeError:
                return client.branch_path(
                    self._project_id,
                    self._location,
                    self._collection_id,
                    store_id,
                    self._branch_id,
                )
        return (
            f"projects/{self._project_id}/locations/{self._location}/collections/"
            f"{self._collection_id}/dataStores/{store_id}/branches/{self._branch_id}"
        )

    @staticmethod
    def _build_document_path(parent: str, document_id: str) -> str:
        return f"{parent}/documents/{document_id}"

    def search(
        self,
        query: str,
        max_results: int = 5,
        data_store_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.is_configured() and not data_store_id:
            logger.warning("Discovery Engine not configured.")
            return []

        if not query.strip():
            return []

        from google.cloud import discoveryengine_v1beta as discoveryengine

        request = discoveryengine.SearchRequest(
            serving_config=self._build_serving_config(data_store_id=data_store_id),
            query=query,
            page_size=max_results,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True
                )
            ),
        )

        try:
            response = self._get_client().search(request=request)
        except Exception as e:
            logger.error(f"Discovery Engine search failed: {e}")
            return []

        def _safe_struct(value: Any) -> dict[str, Any]:
            if isinstance(value, dict):
                return value
            try:
                from google.protobuf.json_format import MessageToDict

                return MessageToDict(value, preserving_proto_field_name=True)
            except Exception:
                return {}

        results: list[dict[str, Any]] = []
        for result in response.results:
            document = result.document
            derived = _safe_struct(document.derived_struct_data or {})
            struct = _safe_struct(document.struct_data or {})

            title = (
                derived.get("title")
                or struct.get("title")
                or derived.get("name")
                or struct.get("name")
                or document.id
            )
            url = (
                derived.get("link")
                or derived.get("uri")
                or struct.get("link")
                or struct.get("uri")
                or ""
            )

            snippet = ""
            snippets = derived.get("snippets") or struct.get("snippets") or []
            if isinstance(snippets, list) and snippets:
                first = snippets[0]
                if isinstance(first, dict):
                    snippet = first.get("snippet") or first.get("text") or ""
                elif isinstance(first, str):
                    snippet = first
            if not snippet:
                snippet = derived.get("snippet") or struct.get("snippet") or ""

            results.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "doc_type": struct.get("doc_type") or derived.get("doc_type") or "",
                    "source": struct.get("source") or derived.get("source") or "",
                    "campaign_name": struct.get("campaign_name") or "",
                    "channel": struct.get("channel") or "",
                    "region": struct.get("region") or "",
                    "period_start": struct.get("period_start") or "",
                    "period_end": struct.get("period_end") or "",
                    "metrics": struct.get("metrics") or {},
                    "tags": struct.get("tags") or [],
                    "created_at": struct.get("created_at") or "",
                }
            )

        logger.info(
            f"Discovery Engine search completed: '{query}' -> {len(results)} results"
        )
        return results

    def upsert_documents(
        self,
        documents: list[dict[str, Any]],
        data_store_id: str | None = None,
    ) -> int:
        if not documents:
            return 0
        store_id = data_store_id or self._data_store_id
        if not store_id:
            logger.warning("Discovery Engine ingest skipped: data_store_id missing.")
            return 0

        try:
            from google.cloud import discoveryengine_v1beta as discoveryengine
        except Exception as exc:
            logger.error(f"Discovery Engine client unavailable: {exc}")
            return 0

        parent = self._build_branch_path(store_id)
        client = self._get_document_client()
        ingested = 0

        for doc in documents:
            doc_id = str(doc.get("id") or "").strip()
            if not doc_id:
                continue
            struct_data = doc.get("struct_data") or {}
            try:
                document = discoveryengine.Document(id=doc_id, struct_data=struct_data)
                if hasattr(client, "upsert_document"):
                    client.upsert_document(parent=parent, document=document)
                else:
                    try:
                        client.create_document(
                            parent=parent, document=document, document_id=doc_id
                        )
                    except Exception:
                        document.name = self._build_document_path(parent, doc_id)
                        if hasattr(client, "update_document"):
                            client.update_document(document=document)
                        else:
                            raise
                ingested += 1
            except Exception as exc:
                logger.error(f"Discovery Engine ingest failed for {doc_id}: {exc}")

        return ingested
