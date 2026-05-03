"""MongoDB ObjectId and datetime helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId


def parse_object_id(value: str) -> Optional[ObjectId]:
    try:
        return ObjectId(value)
    except InvalidId:
        return None


def utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
