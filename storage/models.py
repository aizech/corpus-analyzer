"""Data models for progress-tracking snapshots."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


class SnapshotTag(str, Enum):
    """Tags that describe the type or purpose of a snapshot."""

    SKIN = "skin"
    NAIL = "nail"
    WOUND = "wound"
    RASH = "rash"
    DOCUMENT = "document"
    OTHER = "other"


@dataclass
class PhotoSnapshot:
    """A single stored photo/document snapshot with optional metadata.

    This model is intentionally decoupled from any concrete storage backend so
    that the backend can be chosen later (SQLite, S3, encrypted file system,
    etc.) without changing the rest of the application.
    """

    user_id: str
    created_at: datetime
    image_hash: str
    image_path: Optional[str]
    body_site: Optional[str]
    anamnesis: Optional[str]
    analysis_summary: Optional[str]
    encrypted_image: Optional[bytes] = None
    tags: List[SnapshotTag] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    snapshot_id: str = field(default_factory=lambda: str(uuid4()))

    @classmethod
    def create(
        cls,
        user_id: str,
        image_hash: str,
        image_path: Optional[str] = None,
        body_site: Optional[str] = None,
        anamnesis: Optional[str] = None,
        analysis_summary: Optional[str] = None,
        encrypted_image: Optional[bytes] = None,
        tags: Optional[List[SnapshotTag]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> "PhotoSnapshot":
        """Factory that stamps a new snapshot with the current UTC time."""
        return cls(
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            image_hash=image_hash,
            image_path=image_path,
            body_site=body_site,
            anamnesis=anamnesis,
            analysis_summary=analysis_summary,
            encrypted_image=encrypted_image,
            tags=tags or [],
            metadata=metadata or {},
        )


@dataclass
class ConsentRecord:
    """A recorded user consent decision.

    Consent records are immutable once created. Withdrawing consent creates a
    new record with ``granted=False`` so that the history of consent decisions is
    preserved.
    """

    user_id: str
    scope: str
    granted: bool
    created_at: datetime
    version: str
    consent_id: str = field(default_factory=lambda: str(uuid4()))

    @classmethod
    def create(
        cls,
        user_id: str,
        scope: str,
        granted: bool,
        version: str = "1.0",
    ) -> "ConsentRecord":
        """Factory that stamps a new consent record with the current UTC time."""
        return cls(
            user_id=user_id,
            scope=scope,
            granted=granted,
            created_at=datetime.now(timezone.utc),
            version=version,
        )
