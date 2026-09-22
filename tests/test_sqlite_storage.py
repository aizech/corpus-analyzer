"""Tests for the encrypted SQLite storage backend."""

import os
import tempfile

import pytest
from cryptography.fernet import Fernet

from storage.models import PhotoSnapshot, SnapshotTag
from storage.sqlite_storage import EncryptedSQLiteStorage


def _fresh_key() -> str:
    return Fernet.generate_key().decode("utf-8")


def _make_snapshot(
    user_id: str = "user-1", body_site: str = "front:shoulder:left"
) -> PhotoSnapshot:
    return PhotoSnapshot.create(
        user_id=user_id,
        image_hash="sha256-abc",
        body_site=body_site,
        anamnesis="Itching for 3 days",
        analysis_summary="Possible contact dermatitis; no definitive diagnosis.",
        encrypted_image=b"encrypted-image-bytes",
        tags=[SnapshotTag.SKIN],
        metadata={"source": "test"},
    )


def test_storage_requires_encryption_key():
    with pytest.raises(ValueError, match="encryption key is required"):
        EncryptedSQLiteStorage(":memory:", "")


def test_save_and_get_snapshot():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    snapshot = _make_snapshot()

    snapshot_id = storage.save_snapshot(snapshot)
    retrieved = storage.get_snapshot(snapshot.user_id, snapshot_id)

    assert retrieved.snapshot_id == snapshot_id
    assert retrieved.user_id == snapshot.user_id
    assert retrieved.image_hash == snapshot.image_hash
    assert retrieved.body_site == snapshot.body_site
    assert retrieved.anamnesis == snapshot.anamnesis
    assert retrieved.analysis_summary == snapshot.analysis_summary
    assert retrieved.encrypted_image == snapshot.encrypted_image
    assert retrieved.tags == snapshot.tags
    assert retrieved.metadata == snapshot.metadata


def test_list_snapshots_filters_by_body_site():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    s1 = _make_snapshot(body_site="front:shoulder:left")
    s2 = _make_snapshot(body_site="back:lower_back:center")
    storage.save_snapshot(s1)
    storage.save_snapshot(s2)

    results = storage.list_snapshots("user-1", body_site="front:shoulder:left")
    assert len(results) == 1
    assert results[0].body_site == "front:shoulder:left"


def test_list_snapshots_filters_by_tag():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    s1 = _make_snapshot()
    s2 = _make_snapshot()
    s2.tags = [SnapshotTag.NAIL]
    storage.save_snapshot(s1)
    storage.save_snapshot(s2)

    results = storage.list_snapshots("user-1", tag="nail")
    assert len(results) == 1


def test_list_snapshots_respects_limit():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    for _ in range(5):
        storage.save_snapshot(_make_snapshot())

    results = storage.list_snapshots("user-1", limit=2)
    assert len(results) == 2


def test_delete_snapshot():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    snapshot = _make_snapshot()
    snapshot_id = storage.save_snapshot(snapshot)

    storage.delete_snapshot(snapshot.user_id, snapshot_id)
    with pytest.raises(KeyError):
        storage.get_snapshot(snapshot.user_id, snapshot_id)


def test_delete_wrong_user_raises():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    snapshot = _make_snapshot()
    snapshot_id = storage.save_snapshot(snapshot)

    with pytest.raises(KeyError):
        storage.delete_snapshot("other-user", snapshot_id)


def test_encrypted_data_not_readable_without_key():
    key = _fresh_key()
    storage = EncryptedSQLiteStorage(":memory:", key)
    snapshot = _make_snapshot()
    storage.save_snapshot(snapshot)

    # We cannot read from the same in-memory DB with a different connection, so
    # we instead test that the raw database file contains encrypted bytes.
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        path = tmp.name
    persistent = None
    try:
        persistent = EncryptedSQLiteStorage(path, key)
        persistent.save_snapshot(snapshot)
        persistent.close()
        persistent = None
        with open(path, "rb") as f:
            raw = f.read()
        assert b"Itching for 3 days" not in raw
        assert b"Possible contact dermatitis" not in raw
    finally:
        if persistent is not None:
            persistent.close()
        os.unlink(path)


def test_factory_returns_in_memory_by_default():
    from storage.factory import get_storage_backend

    backend = get_storage_backend()
    assert backend.__class__.__name__ == "InMemoryStorage"


def test_factory_returns_sqlite_when_path_set(monkeypatch):
    from storage.factory import get_storage_backend

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        path = tmp.name
    key = _fresh_key()
    monkeypatch.setenv("SNAPSHOT_STORAGE_PATH", path)
    monkeypatch.setenv("STORAGE_ENCRYPTION_KEY", key)
    backend = None
    try:
        backend = get_storage_backend()
        assert isinstance(backend, EncryptedSQLiteStorage)
    finally:
        if backend is not None:
            backend.close()
        os.unlink(path)
        monkeypatch.delenv("SNAPSHOT_STORAGE_PATH", raising=False)
        monkeypatch.delenv("STORAGE_ENCRYPTION_KEY", raising=False)
