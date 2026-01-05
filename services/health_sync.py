"""
Health sync shim for HealthKit / Health Connect integration.
Currently logs payloads; replace with platform-specific APIs later.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthSyncService:
    """Lightweight stub to enqueue nutrition entries for device health apps."""

    def __init__(self):
        self.buffer = []  # Simple in-memory buffer; replace with durable queue if needed

    def sync_nutrition_entry(
        self,
        user_id: str,
        product: str,
        nutrients: Dict[str, Any],
        source: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> bool:
        """Queue a nutrition entry for downstream sync."""
        if not nutrients:
            return False

        payload = {
            "user_id": user_id,
            "product": product,
            "source": source,
            "nutrients": nutrients,
            "timestamp": timestamp or datetime.utcnow().isoformat(),
        }
        self.buffer.append(payload)
        logger.info("Health sync queued", extra={"source": source, "product": product})
        return True


_health_sync_service: Optional[HealthSyncService] = None


def get_health_sync_service() -> HealthSyncService:
    global _health_sync_service
    if _health_sync_service is None:
        _health_sync_service = HealthSyncService()
    return _health_sync_service
