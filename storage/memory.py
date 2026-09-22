"""In-memory implementation of the storage interface for tests and design validation."""

from typing import Dict, List, Optional

from storage.base import AbstractStorage
from storage.models import ConsentRecord, PhotoSnapshot


class InMemoryStorage(AbstractStorage):
    """Volatile in-memory storage backend.

    This backend is intentionally unsuitable for production because all data is
    lost when the process exits. It is useful for unit tests and for validating
    the storage interface before choosing a real backend.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, PhotoSnapshot]] = {}
        self._consents: Dict[str, List[ConsentRecord]] = {}

    def save_snapshot(self, snapshot: PhotoSnapshot) -> str:
        """Persist a snapshot and return its snapshot_id."""
        user_store = self._store.setdefault(snapshot.user_id, {})
        user_store[snapshot.snapshot_id] = snapshot
        return snapshot.snapshot_id

    def get_snapshot(self, user_id: str, snapshot_id: str) -> PhotoSnapshot:
        """Retrieve a single snapshot by user and id."""
        user_store = self._store.get(user_id)
        if not user_store or snapshot_id not in user_store:
            raise KeyError(f"Snapshot {snapshot_id} not found for user {user_id}")
        return user_store[snapshot_id]

    def list_snapshots(
        self,
        user_id: str,
        body_site: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[PhotoSnapshot]:
        """List snapshots for a user, optionally filtered by body site or tag."""
        user_store = self._store.get(user_id, {})
        snapshots = list(user_store.values())
        if body_site is not None:
            snapshots = [s for s in snapshots if s.body_site == body_site]
        if tag is not None:
            snapshots = [s for s in snapshots if tag in (t.value for t in s.tags)]
        snapshots = sorted(snapshots, key=lambda s: s.created_at, reverse=True)
        if limit is not None:
            snapshots = snapshots[:limit]
        return snapshots

    def delete_snapshot(self, user_id: str, snapshot_id: str) -> None:
        """Delete a snapshot permanently."""
        user_store = self._store.get(user_id)
        if user_store and snapshot_id in user_store:
            del user_store[snapshot_id]

    def record_consent(self, consent: ConsentRecord) -> str:
        """Persist a consent decision and return its consent_id."""
        user_consents = self._consents.setdefault(consent.user_id, [])
        user_consents.append(consent)
        return consent.consent_id

    def list_consent_records(
        self,
        user_id: str,
        scope: Optional[str] = None,
    ) -> List[ConsentRecord]:
        """Return consent records for a user, newest first."""
        records = self._consents.get(user_id, [])
        if scope is not None:
            records = [r for r in records if r.scope == scope]
        return sorted(records, key=lambda r: r.created_at, reverse=True)
