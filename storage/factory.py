"""Factory for choosing a concrete storage backend."""

import os
from typing import Optional

from storage.base import AbstractStorage
from storage.memory import InMemoryStorage


def get_storage_backend(
    db_path: Optional[str] = None,
    encryption_key: Optional[str] = None,
) -> AbstractStorage:
    """Return the configured storage backend.

    If ``SNAPSHOT_STORAGE_PATH`` is set, an encrypted SQLite backend is used.
    Otherwise the in-memory backend is returned, which is suitable for tests
    and for deployments where progress tracking is disabled.

    Args:
        db_path: Optional path to the SQLite database. Defaults to the
            ``SNAPSHOT_STORAGE_PATH`` environment variable.
        encryption_key: Optional Fernet key. Defaults to
            ``STORAGE_ENCRYPTION_KEY`` from the environment.

    Returns:
        An ``AbstractStorage`` implementation.
    """
    from storage.sqlite_storage import EncryptedSQLiteStorage

    path = db_path or os.environ.get("SNAPSHOT_STORAGE_PATH")
    if path:
        return EncryptedSQLiteStorage(
            db_path=path,
            encryption_key=encryption_key or os.environ.get("STORAGE_ENCRYPTION_KEY", ""),
        )
    return InMemoryStorage()
