"""Validation and serialization for QR code payload formats."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parseaddr
from urllib.parse import urlparse
from uuid import uuid4


class PayloadError(ValueError):
    """Raised when user input cannot form a valid QR payload."""


def require_text(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise PayloadError(f"{label} cannot be empty")
    return value


def make_url(value: str) -> str:
    value = require_text(value, "URL")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PayloadError("URL must be a complete http:// or https:// address")
    return value


def make_tel(number: str) -> str:
    number = require_text(number, "Phone number")
    if not re.fullmatch(r"\+?[0-9 ()-]{3,30}", number):
        raise PayloadError("Phone number contains unsupported characters")
    return f"tel:{number}"


def _wifi_escape(value: str) -> str:
    return re.sub(r'([\\;,:"])', r"\\\1", value)


def make_wifi(ssid: str, security: str, password: str) -> str:
    ssid = require_text(ssid, "SSID")
    security_map = {
        "WPA": "WPA",
        "WPA2": "WPA",
        "WPA3": "WPA",
        "WEP": "WEP",
        "NOPASS": "nopass",
        "NONE": "nopass",
    }
    normalized = security_map.get(security.strip().upper())
    if normalized is None:
        raise PayloadError("Security must be WPA, WPA2, WPA3, WEP, or nopass")
    if normalized != "nopass" and not password:
        raise PayloadError("Password cannot be empty for a secured network")
    return f"WIFI:T:{normalized};S:{_wifi_escape(ssid)};P:{_wifi_escape(password)};;"


def _structured_escape(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def _fold_lines(lines: list[str]) -> str:
    """Fold content lines to the 75 UTF-8 octet interoperability limit."""
    folded: list[str] = []
    for line in lines:
        current = ""
        for character in line:
            if len((current + character).encode("utf-8")) > 75:
                folded.append(current)
                current = " " + character
            else:
                current += character
        folded.append(current)
    return "\r\n".join(folded)


def make_vcard(full_name: str, organization: str, telephone: str, email: str, title: str) -> str:
    full_name = require_text(full_name, "Full name")
    telephone = require_text(telephone, "Phone number")
    make_tel(telephone)
    email = require_text(email, "Email")
    if parseaddr(email)[1] != email or "@" not in email:
        raise PayloadError("Email address is not valid")

    parts = full_name.split()
    given = " ".join(parts[:-1]) if len(parts) > 1 else full_name
    surname = parts[-1] if len(parts) > 1 else ""
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{_structured_escape(surname)};{_structured_escape(given)};;;",
        f"FN:{_structured_escape(full_name)}",
        f"ORG:{_structured_escape(organization)}",
        f"TITLE:{_structured_escape(title)}",
        f"TEL;TYPE=WORK,VOICE:{telephone}",
        f"EMAIL;TYPE=INTERNET:{email}",
        "END:VCARD",
    ]
    return _fold_lines(lines)


def make_sms(number: str, message: str = "") -> str:
    number = require_text(number, "Phone number")
    make_tel(number)
    if any(character in message for character in "\r\n"):
        raise PayloadError("SMS message must be on one line")
    return f"SMSTO:{number}:{message}"


def _parse_event_time(value: str, label: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError as exc:
        raise PayloadError(f"{label} must use YYYY-MM-DDTHH:MM") from exc


def make_event(
    title: str,
    start: str,
    end: str,
    location: str,
    description: str,
    *,
    uid: str | None = None,
    timestamp: datetime | None = None,
) -> str:
    title = require_text(title, "Event title")
    start_dt = _parse_event_time(start, "Start")
    end_dt = _parse_event_time(end, "End")
    if end_dt <= start_dt:
        raise PayloadError("Event end must be later than its start")

    timestamp = timestamp or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    stamp = timestamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    event_uid = uid or f"{uuid4()}@thetechshed.dev"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//The Tech Shed//QR Generator//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{event_uid}",
        f"DTSTAMP:{stamp}",
        f"SUMMARY:{_structured_escape(title)}",
        f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
        f"LOCATION:{_structured_escape(location)}",
        f"DESCRIPTION:{_structured_escape(description)}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return _fold_lines(lines)


def make_text(value: str) -> str:
    return require_text(value, "Text")
