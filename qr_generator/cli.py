"""Command-line interface for The Tech Shed QR Generator."""

from __future__ import annotations

import argparse

from .core import save_qr
from .payloads import PayloadError, make_event, make_sms, make_tel, make_text, make_url, make_vcard, make_wifi


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate QR codes for common data formats.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL beginning with http:// or https://")
    group.add_argument("--tel", help="Telephone number")
    group.add_argument("--wifi", nargs=3, metavar=("SSID", "SECURITY", "PASSWORD"))
    group.add_argument("--vcard", nargs=5, metavar=("FN", "ORG", "TEL", "EMAIL", "TITLE"))
    group.add_argument("--sms", nargs="+", metavar=("NUMBER", "MESSAGE"))
    group.add_argument("--event", nargs=5, metavar=("TITLE", "START", "END", "LOCATION", "DESC"))
    group.add_argument("--text", help="Plain text")
    group.add_argument("--gui", action="store_true", help="Open the desktop app")
    parser.add_argument("--output", default="qrcode.png", help="Output image (.png, .jpg, or .jpeg)")
    parser.add_argument("--error-correction", choices=("L", "M", "Q", "H"), default="Q")
    parser.add_argument("--box-size", type=int, default=10)
    parser.add_argument("--border", type=int, default=4)
    parser.add_argument("--foreground", default="black")
    parser.add_argument("--background", default="white")
    return parser


def payload_from_args(args: argparse.Namespace) -> str:
    if args.url is not None:
        return make_url(args.url)
    if args.tel is not None:
        return make_tel(args.tel)
    if args.wifi is not None:
        return make_wifi(*args.wifi)
    if args.vcard is not None:
        return make_vcard(*args.vcard)
    if args.sms is not None:
        return make_sms(args.sms[0], " ".join(args.sms[1:]))
    if args.event is not None:
        return make_event(*args.event)
    if args.text is not None:
        return make_text(args.text)
    raise PayloadError("No QR data was supplied")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.gui:
        from .gui import run

        run()
        return 0
    try:
        payload = payload_from_args(args)
        output = save_qr(
            payload,
            args.output,
            error_correction=args.error_correction,
            box_size=args.box_size,
            border=args.border,
            foreground=args.foreground,
            background=args.background,
        )
    except (PayloadError, OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"[+] QR code saved as {output}")
    return 0
