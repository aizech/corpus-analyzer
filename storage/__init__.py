"""Storage abstraction for future progress-tracking features.

This package defines the interface and data model for storing user snapshots
(e.g., skin-lesion photos over time). No production storage backend is wired in
this release; only an in-memory implementation is provided for tests and design
validation.
"""

from storage.base import AbstractStorage
from storage.memory import InMemoryStorage
from storage.models import PhotoSnapshot, SnapshotTag

__all__ = ["AbstractStorage", "InMemoryStorage", "PhotoSnapshot", "SnapshotTag"]
