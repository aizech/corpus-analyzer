"""Abstract storage interface for user snapshots.

A concrete backend must implement the methods below. This release ships only an
in-memory implementation to keep the codebase testable while the legal and
privacy implications of persistent storage are clarified.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from storage.models import PhotoSnapshot


class AbstractStorage(ABC):
    """Storage backend contract for photo/document snapshots."""

    @abstractmethod
    def save_snapshot(self, snapshot: PhotoSnapshot) -> str:
        """Persist a snapshot and return its generated snapshot_id."""

    @abstractmethod
    def get_snapshot(self, user_id: str, snapshot_id: str) -> PhotoSnapshot:
        """Retrieve a single snapshot by user and id."""

    @abstractmethod
    def list_snapshots(
        self,
        user_id: str,
        body_site: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[PhotoSnapshot]:
        """List snapshots for a user, optionally filtered by body site or tag."""

    @abstractmethod
    def delete_snapshot(self, user_id: str, snapshot_id: str) -> None:
        """Delete a snapshot permanently."""
