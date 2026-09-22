"""Tests for image loading and normalization helpers."""

import io

import pydicom
from PIL import Image as PILImage

from image_loader import (
    LoadedImage,
    _dicom_to_pil,
    _is_dicom_file,
    load_camera_shot,
    load_image_file,
    load_images,
    resize_for_display,
)


class _UploadedFile(io.BytesIO):
    """Minimal file-like wrapper with the attributes Streamlit's UploadedFile provides."""

    def __init__(self, initial_bytes: bytes, name: str, mime_type: str) -> None:
        super().__init__(initial_bytes)
        self.name = name
        self.type = mime_type


def _make_dicom_dataset(pixel_value: int = 128) -> pydicom.Dataset:
    """Create a minimal valid DICOM dataset."""
    ds = pydicom.Dataset()
    ds.Rows = 10
    ds.Columns = 10
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelData = bytes([pixel_value]) * 100
    ds.PatientName = "Test Patient"
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    ds.SOPInstanceUID = pydicom.uid.generate_uid()

    ds.file_meta = pydicom.dataset.FileMetaDataset()
    ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

    return ds


def _make_dicom_bytes() -> bytes:
    """Create a minimal DICOM file in memory."""
    ds = _make_dicom_dataset()
    buf = io.BytesIO()
    pydicom.dcmwrite(buf, ds, enforce_file_format=True)
    buf.seek(0)
    return buf.getvalue()


def test_is_dicom_file_by_extension():
    assert _is_dicom_file("scan.dcm") is True
    assert _is_dicom_file("scan.DICOM") is True
    assert _is_dicom_file("scan.jpg") is False


def test_is_dicom_file_by_mime_type():
    assert _is_dicom_file("scan", "application/dicom") is True
    assert _is_dicom_file("scan", "image/jpeg") is False


def test_dicom_to_pil_converts_grayscale():
    ds = _make_dicom_dataset(pixel_value=255)
    pil_image = _dicom_to_pil(ds)
    assert pil_image.size == (10, 10)
    assert pil_image.mode == "RGB"


def test_load_image_file_with_dicom_anonymizes():
    dicom_bytes = _make_dicom_bytes()
    uploaded = _UploadedFile(dicom_bytes, "test.dcm", "application/dicom")

    loaded = load_image_file(uploaded, anonymize=True)
    assert loaded.is_dicom is True
    assert loaded.original_name == "test.dcm"
    assert "PatientName" in loaded.cleared_tags
    assert loaded.pil_image.size == (10, 10)


def test_load_image_file_with_standard_image():
    buf = io.BytesIO()
    PILImage.new("RGB", (50, 50), color="red").save(buf, format="PNG")

    uploaded = _UploadedFile(buf.getvalue(), "test.png", "image/png")
    loaded = load_image_file(uploaded)
    assert loaded.is_dicom is False
    assert loaded.pil_image.size == (50, 50)


def test_load_images_preserves_order():
    uploads = []
    for color in ["red", "blue"]:
        buf = io.BytesIO()
        PILImage.new("RGB", (10, 10), color=color).save(buf, format="PNG")
        uploads.append(_UploadedFile(buf.getvalue(), f"{color}.png", "image/png"))

    loaded = load_images(uploads)
    assert len(loaded) == 2
    assert loaded[0].original_name == "red.png"
    assert loaded[1].original_name == "blue.png"


def test_load_camera_shot():
    buf = io.BytesIO()
    PILImage.new("RGB", (20, 20), color="green").save(buf, format="PNG")
    loaded = load_camera_shot(buf.getvalue(), original_name="camera.png")
    assert loaded.source_type == "camera"
    assert loaded.original_name == "camera.png"
    assert loaded.pil_image.size == (20, 20)


def test_resize_for_display_only_downscales():
    big = PILImage.new("RGB", (1000, 500), color="blue")
    resized = resize_for_display(big, max_width=600)
    assert resized.size[0] == 600
    assert resized.size[1] == 300

    small = PILImage.new("RGB", (400, 200), color="blue")
    not_resized = resize_for_display(small, max_width=600)
    assert not_resized.size == (400, 200)


def test_loaded_image_dataclass():
    img = PILImage.new("RGB", (10, 10))
    record = LoadedImage(
        pil_image=img,
        source_type="upload",
        original_name="x.png",
        is_dicom=False,
        cleared_tags=[],
        removed_sequences=[],
    )
    assert record.is_dicom is False
    assert record.original_name == "x.png"
