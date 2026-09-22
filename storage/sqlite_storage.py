"""Encrypted SQLite backend for photo/document snapshots.

This backend implements the abstract storage contract. It stores snapshots in a
local SQLite database and encrypts sensitive fields (image bytes, anamnesis,
analysis summary) at the application layer using Fernet (``cryptography``).

The encryption key must be provided by the operator; without it snapshots cannot
be recovered. The key is never persisted by this class.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from storage.base import AbstractStorage
from storage.models import ConsentRecord, PhotoSnapshot, SnapshotTag


def _get_fernet(key: str):
    """Return a Fernet instance for the given base64-encoded key."""
    from cryptography.fernet import Fernet

    return Fernet(key.encode("utf-8") if isinstance(key, str) else key)


class EncryptedSQLiteStorage(AbstractStorage):
    """Store snapshots in an encrypted SQLite database.

    Args:
        db_path: Path to the SQLite database file.
        encryption_key: URL-safe base64-encoded 32-byte Fernet key.
    """

    def __init__(self, db_path: str, encryption_key: str) -> None:
        self._db_path = db_path
        if not encryption_key:
            raise ValueError("An encryption key is required for EncryptedSQLiteStorage")
        self._fernet = _get_fernet(encryption_key)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_schema()

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def _ensure_schema(self) -> None:
        """Create the snapshots table if it does not exist."""
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    image_hash TEXT NOT NULL,
                    body_site TEXT,
                    encrypted_anamnesis BLOB,
                    encrypted_summary BLOB,
                    encrypted_image BLOB,
                    tags TEXT,
                    metadata TEXT
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_user ON snapshots (user_id)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_snapshots_body_site ON snapshots (body_site)"
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consent_records (
                    consent_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    granted INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    version TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_consent_user_scope ON consent_records (user_id, scope)"
            )

    def _encrypt_text(self, value: Optional[str]) -> Optional[bytes]:
        if value is None:
            return None
        return self._fernet.encrypt(value.encode("utf-8"))

    def _encrypt_bytes(self, value: Optional[bytes]) -> Optional[bytes]:
        if value is None:
            return None
        return self._fernet.encrypt(value)

    def _decrypt_text(self, value: Optional[bytes]) -> Optional[str]:
        if value is None:
            return None
        return self._fernet.decrypt(value).decode("utf-8")

    def _decrypt_bytes(self, value: Optional[bytes]) -> Optional[bytes]:
        if value is None:
            return None
        return self._fernet.decrypt(value)

    def _row_to_snapshot(self, row: sqlite3.Row) -> PhotoSnapshot:
        return PhotoSnapshot(
            snapshot_id=row["snapshot_id"],
            user_id=row["user_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            image_hash=row["image_hash"],
            image_path=None,
            body_site=row["body_site"],
            anamnesis=self._decrypt_text(row["encrypted_anamnesis"]),
            analysis_summary=self._decrypt_text(row["encrypted_summary"]),
            encrypted_image=self._decrypt_bytes(row["encrypted_image"]),
            tags=[SnapshotTag(t) for t in json.loads(row["tags"] or "[]")],
            metadata=json.loads(row["metadata"] or "{}"),
        )

    def save_snapshot(self, snapshot: PhotoSnapshot) -> str:
        """Persist a snapshot and return its snapshot_id."""
        snapshot_id = snapshot.snapshot_id or self._generate_id()
        created_at = (
            snapshot.created_at
            if isinstance(snapshot.created_at, str)
            else snapshot.created_at.isoformat()
        )
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO snapshots (
                    snapshot_id, user_id, created_at, image_hash, body_site,
                    encrypted_anamnesis, encrypted_summary, encrypted_image, tags, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    snapshot.user_id,
                    created_at,
                    snapshot.image_hash,
                    snapshot.body_site,
                    self._encrypt_text(snapshot.anamnesis),
                    self._encrypt_text(snapshot.analysis_summary),
                    self._encrypt_bytes(snapshot.encrypted_image),
                    json.dumps([t.value for t in snapshot.tags]),
                    json.dumps(snapshot.metadata),
                ),
            )
        return snapshot_id

    def get_snapshot(self, user_id: str, snapshot_id: str) -> PhotoSnapshot:
        """Retrieve a single snapshot by user and id."""
        self._conn.row_factory = sqlite3.Row
        row = self._conn.execute(
            "SELECT * FROM snapshots WHERE snapshot_id = ? AND user_id = ?",
            (snapshot_id, user_id),
        ).fetchone()
        if row is None:
            raise KeyError(f"Snapshot {snapshot_id} not found for user {user_id}")
        return self._row_to_snapshot(row)

    def list_snapshots(
        self,
        user_id: str,
        body_site: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[PhotoSnapshot]:
        """List snapshots for a user, optionally filtered by body site or tag."""
        query = "SELECT * FROM snapshots WHERE user_id = ?"
        params: List[object] = [user_id]
        if body_site is not None:
            query += " AND body_site = ?"
            params.append(body_site)
        if tag is not None:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")
        query += " ORDER BY created_at DESC"
        if limit is not None:
            query += f" LIMIT {int(limit)}"

        self._conn.row_factory = sqlite3.Row
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_snapshot(row) for row in rows]

    def delete_snapshot(self, user_id: str, snapshot_id: str) -> None:
        """Delete a snapshot permanently."""
        with self._conn:
            cursor = self._conn.execute(
                "DELETE FROM snapshots WHERE snapshot_id = ? AND user_id = ?",
                (snapshot_id, user_id),
            )
        if cursor.rowcount == 0:
            raise KeyError(f"Snapshot {snapshot_id} not found for user {user_id}")

    def record_consent(self, consent: ConsentRecord) -> str:
        """Persist a consent decision and return its consent_id."""
        consent_id = consent.consent_id or self._generate_id()
        created_at = (
            consent.created_at
            if isinstance(consent.created_at, str)
            else consent.created_at.isoformat()
        )
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO consent_records (
                    consent_id, user_id, scope, granted, created_at, version
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    consent_id,
                    consent.user_id,
                    consent.scope,
                    1 if consent.granted else 0,
                    created_at,
                    consent.version,
                ),
            )
        return consent_id

    def list_consent_records(
        self,
        user_id: str,
        scope: Optional[str] = None,
    ) -> List[ConsentRecord]:
        """Return consent records for a user, newest first."""
        query = "SELECT * FROM consent_records WHERE user_id = ?"
        params: List[object] = [user_id]
        if scope is not None:
            query += " AND scope = ?"
            params.append(scope)
        query += " ORDER BY created_at DESC"

        self._conn.row_factory = sqlite3.Row
        rows = self._conn.execute(query, params).fetchall()
        return [
            ConsentRecord(
                consent_id=row["consent_id"],
                user_id=row["user_id"],
                scope=row["scope"],
                granted=bool(row["granted"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                version=row["version"],
            )
            for row in rows
        ]

    @staticmethod
    def _generate_id() -> str:
        from uuid import uuid4

        return str(uuid4())


def create_encrypted_sqlite_storage(
    db_path: str,
    encryption_key: Optional[str] = None,
) -> EncryptedSQLiteStorage:
    """Factory helper that loads the encryption key from the environment if needed."""
    import os

    key = encryption_key or os.environ.get("STORAGE_ENCRYPTION_KEY")
    if not key:
        raise ValueError("STORAGE_ENCRYPTION_KEY must be set to use encrypted SQLite storage.")
    return EncryptedSQLiteStorage(db_path, key)
