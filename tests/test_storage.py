"""Tests for the abstract storage interface and in-memory implementation."""

import pytest

from storage import AbstractStorage, ConsentRecord, InMemoryStorage, PhotoSnapshot, SnapshotTag


def test_in_memory_storage_implements_abstract_storage():
    storage = InMemoryStorage()
    assert isinstance(storage, AbstractStorage)


def test_save_and_get_snapshot():
    storage = InMemoryStorage()
    snapshot = PhotoSnapshot.create(
        user_id="user-1",
        image_hash="abc123",
        image_path="/tmp/abc123.enc",
        body_site="arm:forearm:left",
        anamnesis="Itchy rash for 2 days.",
        analysis_summary="Possible contact dermatitis.",
        tags=[SnapshotTag.SKIN],
    )
    snapshot_id = storage.save_snapshot(snapshot)
    retrieved = storage.get_snapshot("user-1", snapshot_id)
    assert retrieved.snapshot_id == snapshot_id
    assert retrieved.image_hash == "abc123"


def test_get_missing_snapshot_raises():
    storage = InMemoryStorage()
    with pytest.raises(KeyError):
        storage.get_snapshot("user-1", "missing-id")


def test_list_snapshots_by_user():
    storage = InMemoryStorage()
    for idx in range(3):
        storage.save_snapshot(
            PhotoSnapshot.create(
                user_id="user-1",
                image_hash=f"hash-{idx}",
                tags=[SnapshotTag.SKIN],
            )
        )
    storage.save_snapshot(
        PhotoSnapshot.create(user_id="user-2", image_hash="other-hash", tags=[SnapshotTag.NAIL])
    )

    user1_snapshots = storage.list_snapshots("user-1")
    assert len(user1_snapshots) == 3

    user2_snapshots = storage.list_snapshots("user-2")
    assert len(user2_snapshots) == 1


def test_list_snapshots_filtered_by_body_site():
    storage = InMemoryStorage()
    storage.save_snapshot(
        PhotoSnapshot.create(
            user_id="user-1",
            image_hash="a",
            body_site="arm:forearm:left",
            tags=[SnapshotTag.SKIN],
        )
    )
    storage.save_snapshot(
        PhotoSnapshot.create(
            user_id="user-1",
            image_hash="b",
            body_site="leg:thigh:right",
            tags=[SnapshotTag.SKIN],
        )
    )

    filtered = storage.list_snapshots("user-1", body_site="arm:forearm:left")
    assert len(filtered) == 1
    assert filtered[0].image_hash == "a"


def test_list_snapshots_filtered_by_tag():
    storage = InMemoryStorage()
    storage.save_snapshot(
        PhotoSnapshot.create(user_id="user-1", image_hash="a", tags=[SnapshotTag.SKIN])
    )
    storage.save_snapshot(
        PhotoSnapshot.create(user_id="user-1", image_hash="b", tags=[SnapshotTag.NAIL])
    )

    filtered = storage.list_snapshots("user-1", tag="nail")
    assert len(filtered) == 1
    assert filtered[0].image_hash == "b"


def test_delete_snapshot():
    storage = InMemoryStorage()
    snapshot = PhotoSnapshot.create(
        user_id="user-1", image_hash="delete-me", tags=[SnapshotTag.SKIN]
    )
    snapshot_id = storage.save_snapshot(snapshot)
    assert len(storage.list_snapshots("user-1")) == 1

    storage.delete_snapshot("user-1", snapshot_id)
    assert len(storage.list_snapshots("user-1")) == 0


def test_photo_snapshot_create_sets_timestamps():
    snapshot = PhotoSnapshot.create(
        user_id="user-1",
        image_hash="abc",
        body_site="arm",
    )
    assert snapshot.user_id == "user-1"
    assert snapshot.image_hash == "abc"
    assert snapshot.body_site == "arm"
    assert snapshot.created_at is not None
    assert snapshot.snapshot_id


def test_record_and_list_consent():
    storage = InMemoryStorage()
    record = ConsentRecord.create(
        user_id="user-1",
        scope="progress_tracking",
        granted=True,
        version="1.0",
    )
    storage.record_consent(record)
    records = storage.list_consent_records("user-1", scope="progress_tracking")
    assert len(records) == 1
    assert records[0].granted is True


def test_consent_withdrawal_returns_false():
    storage = InMemoryStorage()
    storage.record_consent(
        ConsentRecord.create(
            user_id="user-1", scope="progress_tracking", granted=True, version="1.0"
        )
    )
    storage.record_consent(
        ConsentRecord.create(
            user_id="user-1", scope="progress_tracking", granted=False, version="1.0"
        )
    )
    assert storage.is_consent_granted("user-1", "progress_tracking") is False


def test_missing_consent_returns_false():
    storage = InMemoryStorage()
    assert storage.is_consent_granted("user-1", "progress_tracking") is False
