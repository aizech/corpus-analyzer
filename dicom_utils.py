"""DICOM anonymization and inspection utilities."""

import contextlib
from typing import List, Tuple

import pydicom

# DICOM tags that commonly contain patient-identifying information.
# Keep this list in one place so it can be extended or made configurable.
DEFAULT_ANONYMIZATION_TAGS: List[str] = [
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientSex",
    "PatientAge",
    "PatientAddress",
    "PatientTelephoneNumbers",
    "AccessionNumber",
    "InstitutionName",
    "InstitutionAddress",
    "ReferringPhysicianName",
    "PerformingPhysicianName",
    "OperatorsName",
    "StudyID",
    "StudyDate",
    "StudyTime",
    "SeriesDate",
    "SeriesTime",
    "AcquisitionDate",
    "AcquisitionTime",
]

DEFAULT_ANONYMIZATION_SEQUENCES: List[str] = [
    "OtherPatientIDsSequence",
    "ReferencedPatientSequence",
]


def anonymize_dicom_dataset(
    ds: pydicom.dataset.Dataset,
    tags: List[str] | None = None,
    sequences: List[str] | None = None,
) -> pydicom.dataset.Dataset:
    """Return an anonymized copy of a DICOM dataset.

    Args:
        ds: The dataset to anonymize.
        tags: Optional list of tag names to clear. Uses the default list if None.
        sequences: Optional list of sequence names to remove. Uses the default list if None.

    Returns:
        A new anonymized dataset.
    """
    tags = tags or DEFAULT_ANONYMIZATION_TAGS
    sequences = sequences or DEFAULT_ANONYMIZATION_SEQUENCES

    anon = ds.copy()
    with contextlib.suppress(Exception):
        anon.remove_private_tags()

    for tag_name in tags:
        if hasattr(anon, tag_name):
            with contextlib.suppress(Exception):
                setattr(anon, tag_name, "")
            with contextlib.suppress(Exception):
                delattr(anon, tag_name)

    for seq_name in sequences:
        if hasattr(anon, seq_name):
            with contextlib.suppress(Exception):
                delattr(anon, seq_name)

    return anon


def get_anonymization_report(
    ds: pydicom.dataset.Dataset,
    tags: List[str] | None = None,
    sequences: List[str] | None = None,
) -> Tuple[List[str], List[str]]:
    """Return which tags were cleared and which sequences were removed.

    Args:
        ds: The dataset before anonymization.
        tags: Optional list of tag names to check.
        sequences: Optional list of sequence names to check.

    Returns:
        Tuple of (cleared_tags, removed_sequences).
    """
    tags = tags or DEFAULT_ANONYMIZATION_TAGS
    sequences = sequences or DEFAULT_ANONYMIZATION_SEQUENCES

    cleared = [name for name in tags if hasattr(ds, name)]
    removed = [name for name in sequences if hasattr(ds, name)]
    return cleared, removed
