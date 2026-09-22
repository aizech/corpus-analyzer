"""Helpers for loading and normalizing images from uploads or camera capture."""

import io
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pydicom
from PIL import Image as PILImage
from streamlit.runtime.uploaded_file_manager import UploadedFile

from dicom_utils import anonymize_dicom_dataset, get_anonymization_report


@dataclass
class LoadedImage:
    """A normalized image together with its provenance and anonymization report."""

    pil_image: PILImage.Image
    source_type: str  # "dicom", "upload", "camera"
    original_name: Optional[str]
    is_dicom: bool
    cleared_tags: List[str]
    removed_sequences: List[str]


def _is_dicom_file(file_name: str, mime_type: Optional[str] = None) -> bool:
    """Return True if the uploaded file looks like a DICOM file."""
    lowered = file_name.lower()
    return lowered.endswith((".dicom", ".dcm")) or bool(mime_type and "dicom" in mime_type.lower())


def _dicom_to_pil(dicom_data: pydicom.dataset.Dataset) -> PILImage.Image:
    """Convert a DICOM dataset to a displayable RGB PIL image."""
    img_array = dicom_data.pixel_array
    img_array = img_array / img_array.max() * 255
    img_array = img_array.astype(np.uint8)
    pil_image = PILImage.fromarray(img_array)
    if len(img_array.shape) == 2:
        pil_image = pil_image.convert("RGB")
    return pil_image


def load_image_file(
    uploaded_file: UploadedFile,
    *,
    anonymize: bool = True,
    source_type: str = "upload",
) -> LoadedImage:
    """Convert a single uploaded file into a LoadedImage.

    Args:
        uploaded_file: A Streamlit UploadedFile instance.
        anonymize: Whether to anonymize DICOM metadata locally.
        source_type: How the file was produced ("upload" or "camera").

    Returns:
        A LoadedImage containing the normalized PIL image and metadata.
    """
    mime_type = uploaded_file.type
    is_dicom = _is_dicom_file(uploaded_file.name, mime_type)

    if is_dicom:
        uploaded_file.seek(0)
        dicom_data = pydicom.dcmread(uploaded_file, force=True)
        cleared, removed = get_anonymization_report(dicom_data)
        dicom_for_use = anonymize_dicom_dataset(dicom_data) if anonymize else dicom_data
        pil_image = _dicom_to_pil(dicom_for_use)
        return LoadedImage(
            pil_image=pil_image,
            source_type="dicom",
            original_name=uploaded_file.name,
            is_dicom=True,
            cleared_tags=cleared,
            removed_sequences=removed,
        )

    pil_image = PILImage.open(uploaded_file)
    return LoadedImage(
        pil_image=pil_image,
        source_type=source_type,
        original_name=uploaded_file.name,
        is_dicom=False,
        cleared_tags=[],
        removed_sequences=[],
    )


def load_images(
    uploaded_files: List[UploadedFile],
    *,
    anonymize: bool = True,
) -> List[LoadedImage]:
    """Load multiple uploaded files into LoadedImage instances.

    Args:
        uploaded_files: A list of Streamlit UploadedFile instances.
        anonymize: Whether to anonymize DICOM metadata locally.

    Returns:
        A list of LoadedImage objects, preserving input order.
    """
    return [load_image_file(file, anonymize=anonymize) for file in uploaded_files]


def load_camera_shot(
    image_bytes: bytes,
    *,
    original_name: Optional[str] = None,
) -> LoadedImage:
    """Load a camera capture from raw bytes.

    Args:
        image_bytes: Raw image bytes from st.camera_input.
        original_name: Optional file name to associate with the shot.

    Returns:
        A LoadedImage representing the camera capture.
    """
    pil_image = PILImage.open(io.BytesIO(image_bytes))
    return LoadedImage(
        pil_image=pil_image,
        source_type="camera",
        original_name=original_name or "camera_capture.png",
        is_dicom=False,
        cleared_tags=[],
        removed_sequences=[],
    )


def resize_for_display(
    pil_image: PILImage.Image,
    max_width: int = 600,
) -> PILImage.Image:
    """Resize an image while preserving aspect ratio for display.

    Args:
        pil_image: The image to resize.
        max_width: Maximum display width in pixels.

    Returns:
        A resized copy if the original exceeded max_width, otherwise the original.
    """
    width, height = pil_image.size
    if width <= max_width:
        return pil_image
    aspect_ratio = width / height
    new_height = int(max_width / aspect_ratio)
    return pil_image.resize((max_width, new_height))


def get_image_metadata(loaded: LoadedImage) -> Tuple[str, str]:
    """Return human-readable format and dimension strings for a loaded image."""
    dimensions = f"{loaded.pil_image.size[0]} x {loaded.pil_image.size[1]} pixels"
    if loaded.is_dicom:
        return "DICOM", dimensions
    extension = (loaded.original_name or "").split(".")[-1].upper()
    return extension or "Image", dimensions
