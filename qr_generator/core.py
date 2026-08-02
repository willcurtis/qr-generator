"""QR image generation shared by the CLI and desktop app."""

from __future__ import annotations

from pathlib import Path

import qrcode
from qrcode.image.pil import PilImage

ERROR_CORRECTION = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def create_qr(
    data: str,
    *,
    error_correction: str = "Q",
    box_size: int = 10,
    border: int = 4,
    foreground: str = "black",
    background: str = "white",
) -> PilImage:
    """Create a QR image from an already validated payload."""
    if error_correction not in ERROR_CORRECTION:
        raise ValueError("Error correction must be L, M, Q, or H")
    if box_size < 1:
        raise ValueError("Box size must be at least 1")
    if border < 4:
        raise ValueError("Border must be at least 4 modules")
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECTION[error_correction],
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color=foreground, back_color=background)


def save_qr(data: str, output: str | Path, **options: object) -> Path:
    """Create and save a QR image, returning the resolved output path."""
    path = Path(output).expanduser()
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("Output must use a .png, .jpg, or .jpeg extension")
    if not path.parent.exists():
        raise ValueError(f"Output directory does not exist: {path.parent}")
    create_qr(data, **options).save(path)
    return path.resolve()
