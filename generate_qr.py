#!/usr/bin/env python3

import argparse
import qrcode
from datetime import datetime

def generate_qr(data, output="qrcode.png"):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(output)
    print(f"[+] QR code saved as {output}")

def format_event(title, start, end, location, description):
    # Convert to iCalendar format
    def dtfmt(dt):
        return datetime.strptime(dt, "%Y-%m-%dT%H:%M").strftime("%Y%m%dT%H%M%S")
    
    return f"""BEGIN:VEVENT
SUMMARY:{title}
DTSTART:{dtfmt(start)}
DTEND:{dtfmt(end)}
LOCATION:{location}
DESCRIPTION:{description}
END:VEVENT
"""

def main():
    parser = argparse.ArgumentParser(description="Generate QR codes for various data types.")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--url", help="Generate QR for a URL")
    group.add_argument("--tel", help="Generate QR for a phone number (e.g., +1234567890)")
    group.add_argument("--wifi", nargs=3, metavar=("SSID", "SECURITY", "PASSWORD"),
                       help="Generate QR for WiFi access: SSID SECURITY PASSWORD")
    group.add_argument("--vcard", nargs=5, metavar=("FN", "ORG", "TEL", "EMAIL", "TITLE"),
                       help="Generate QR for a vCard contact")
    group.add_argument("--sms", nargs="+", metavar=("NUMBER", "MESSAGE"),
                       help="Generate QR for SMS (message is optional)")
    group.add_argument("--event", nargs=5, metavar=("TITLE", "START", "END", "LOCATION", "DESC"),
                       help="Generate QR for calendar event (start/end in YYYY-MM-DDTHH:MM format)")
    group.add_argument("--text", help="Generate QR for plain text")

    parser.add_argument("--output", default="qrcode.png", help="Output file name")
    args = parser.parse_args()

    if args.url:
        generate_qr(args.url, args.output)

    elif args.tel:
        generate_qr(f"tel:{args.tel}", args.output)

    elif args.wifi:
        ssid, security, password = args.wifi
        wifi_qr = f"WIFI:T:{security};S:{ssid};P:{password};;"
        generate_qr(wifi_qr, args.output)

    elif args.vcard:
        fn, org, tel, email, title = args.vcard
        parts = fn.strip().split()
        given = " ".join(parts[:-1]) if len(parts) > 1 else fn
        surname = parts[-1] if len(parts) > 1 else ""
        vcard = f"""BEGIN:VCARD
VERSION:3.0
N:{surname};{given};;;
FN:{fn}
ORG:{org}
TITLE:{title}
TEL;TYPE=WORK,VOICE:{tel}
EMAIL;TYPE=INTERNET:{email}
END:VCARD"""
        generate_qr(vcard, args.output)

    elif args.sms:
        number = args.sms[0]
        message = args.sms[1] if len(args.sms) > 1 else ""
        generate_qr(f"SMSTO:{number}:{message}", args.output)

    elif args.event:
        title, start, end, location, desc = args.event
        event_ical = f"""BEGIN:VCALENDAR
VERSION:2.0
{format_event(title, start, end, location, desc)}
END:VCALENDAR"""
        generate_qr(event_ical, args.output)

    elif args.text:
        generate_qr(args.text, args.output)

if __name__ == "__main__":
    main()
