# The Tech Shed QR Generator

A validated QR code generator with both a command-line interface and a Tech Shed themed desktop app. It supports URLs, Wi-Fi credentials, vCards, SMS messages, calendar events, telephone links, and plain text.

## Features

- Desktop app with QR preview and PNG/JPEG export
- URL, telephone, email, date, and output validation
- Escaped Wi-Fi, vCard, and iCalendar payloads
- Configurable colours, scale, border, and error correction
- Cross-platform Python packaging and console commands
- Automated payload and CLI tests

## Requirements

- Python 3.10 or newer
- A working Tk installation for the desktop app

On macOS, the Python installer from [python.org](https://www.python.org/downloads/) includes Tk. Homebrew users may need a matching `python-tk` package.

## Installation

Clone the repository, then create an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For development tools and tests, use:

```bash
python -m pip install -e '.[dev]'
```

## Desktop app

Launch the app with either command:

```bash
qr-generator-gui
qr-generator --gui
```

Choose a content type, enter the required values, generate a preview, and select **Save QR code**.

## Command line

```bash
qr-generator [CONTENT OPTION] [IMAGE OPTIONS]
```

The original script entry point remains available:

```bash
python3 generate_qr.py --url 'https://example.com'
```

### Examples

```bash
qr-generator --url 'https://example.com'
qr-generator --tel '+441234567890'
qr-generator --wifi 'SSID' 'WPA2' 'mypassword'
qr-generator --vcard 'Will Curtis' 'The Tech Shed' '+441234567890' 'will@example.com' 'Director'
qr-generator --sms '+441234567890' 'Hello there!'
qr-generator --event 'Meeting' '2026-08-03T14:00' '2026-08-03T15:00' 'HQ' 'Discuss roadmap'
qr-generator --text 'Hello from QR world!'
```

SMS messages may be quoted or supplied as separate words; all words after the number are preserved.

### Image options

```bash
qr-generator --url 'https://example.com' \
  --output mysite.png \
  --error-correction H \
  --box-size 12 \
  --border 4 \
  --foreground '#06141E' \
  --background '#F3FAFC'
```

Supported error-correction levels are `L`, `M`, `Q`, and `H`. QR specifications require a quiet-zone border of at least four modules, so smaller values are rejected.

Calendar times use the local floating format `YYYY-MM-DDTHH:MM`. They intentionally do not attach a timezone; the importing calendar application interprets them in its local timezone.

## Tests and linting

```bash
python -m pytest -q
python -m ruff check .
```

## License

MIT License. Free to use, modify, and distribute.

Built by [The Tech Shed](https://thetechshed.dev).
