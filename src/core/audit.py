import json
from typing import Any
from infrastructure.database.models import AuditLog


async def record_audit_log(
    session,
    action: str,
    actor_email: str,
    actor_role: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    payload = None
    if metadata:
        payload = json.dumps(metadata, ensure_ascii=False)
    log_entry = AuditLog(
        action=action,
        actor_email=actor_email,
        actor_role=actor_role,
        entity_type=entity_type,
        entity_id=entity_id,
        meta_json=payload,
    )
    session.add(log_entry)
    await session.commit()
