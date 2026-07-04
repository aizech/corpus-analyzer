"""Tests for DICOM anonymization utilities."""

import pydicom

from dicom_utils import (
    anonymize_dicom_dataset,
    get_anonymization_report,
)


def test_anonymize_dicom_clears_patient_name():
    ds = pydicom.Dataset()
    ds.PatientName = "Test Patient"
    ds.PatientID = "12345"
    ds.Rows = 10
    ds.Columns = 10
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelData = bytes(100)

    anon = anonymize_dicom_dataset(ds)
    assert not hasattr(anon, "PatientName") or anon.PatientName == ""
    assert not hasattr(anon, "PatientID") or anon.PatientID == ""


def test_get_anonymization_report_lists_tags():
    ds = pydicom.Dataset()
    ds.PatientName = "Test Patient"
    ds.StudyDate = "20240101"

    cleared, removed = get_anonymization_report(ds)
    assert "PatientName" in cleared
    assert "StudyDate" in cleared
    assert removed == []


def test_anonymize_leaves_non_identifying_data():
    ds = pydicom.Dataset()
    ds.PatientName = "Test"
    ds.Rows = 10

    anon = anonymize_dicom_dataset(ds)
    assert anon.Rows == 10
