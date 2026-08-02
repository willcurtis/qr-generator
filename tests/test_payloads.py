from datetime import datetime, timezone

import pytest

from qr_generator.payloads import PayloadError, make_event, make_sms, make_text, make_url, make_vcard, make_wifi


def test_wifi_escapes_reserved_characters():
    assert make_wifi("Cafe;Guest", "WPA2", r"p,a:ss\word") == r"WIFI:T:WPA;S:Cafe\;Guest;P:p\,a\:ss\\word;;"


def test_wifi_requires_password_for_secured_network():
    with pytest.raises(PayloadError, match="Password"):
        make_wifi("Cafe", "WPA", "")


def test_vcard_uses_crlf_and_escapes_structured_text():
    payload = make_vcard("Will Curtis", "Tech;Shed", "+441234567890", "will@example.com", "Owner, Director")
    assert "ORG:Tech\\;Shed\r\n" in payload
    assert "TITLE:Owner\\, Director\r\n" in payload
    assert "\n" not in payload.replace("\r\n", "")


def test_event_is_interoperable_and_escaped():
    payload = make_event(
        "Review, planning",
        "2026-08-03T14:00",
        "2026-08-03T15:00",
        "HQ; London",
        "First line\nSecond line",
        uid="test@thetechshed.dev",
        timestamp=datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc),
    )
    assert "PRODID:-//The Tech Shed//QR Generator//EN\r\n" in payload
    assert "UID:test@thetechshed.dev\r\n" in payload
    assert "DTSTAMP:20260802T120000Z\r\n" in payload
    assert "SUMMARY:Review\\, planning\r\n" in payload
    assert "LOCATION:HQ\\; London\r\n" in payload
    assert "DESCRIPTION:First line\\nSecond line\r\n" in payload


def test_event_rejects_reversed_times():
    with pytest.raises(PayloadError, match="later"):
        make_event("Meeting", "2026-08-03T15:00", "2026-08-03T14:00", "", "")


def test_event_folds_long_content_lines_to_75_utf8_octets():
    payload = make_event(
        "A very long event title " * 8,
        "2026-08-03T14:00",
        "2026-08-03T15:00",
        "HQ",
        "",
        uid="test@thetechshed.dev",
    )
    lines = payload.split("\r\n")
    assert all(len(line.encode("utf-8")) <= 75 for line in lines)
    assert any(line.startswith(" ") for line in lines)


def test_empty_text_is_rejected():
    with pytest.raises(PayloadError, match="empty"):
        make_text("  ")


def test_url_requires_web_scheme_and_host():
    with pytest.raises(PayloadError, match="complete"):
        make_url("example.com")


def test_sms_preserves_a_multiword_message():
    assert make_sms("+441234567890", "Hello there friend") == "SMSTO:+441234567890:Hello there friend"
