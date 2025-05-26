# QR Code Generator

A flexible command-line QR code generator written in Python. Supports encoding URLs, WiFi credentials, vCards, SMS, calendar events, telephone links, and plain text into QR codes.

---

## 🚀 Features

- ✅ URLs
- ✅ Phone numbers
- ✅ WiFi credentials
- ✅ vCard contact info
- ✅ SMS messages
- ✅ Calendar events
- ✅ Plain text

---

## 📦 Requirements

- Python 3.6+
- `qrcode` and `Pillow` packages

Install dependencies:

```bash
pip install qrcode pillow
```

---

## 🛠 Usage

```bash
python3 generate_qr.py [OPTIONS]
```

### 🔗 URL

```bash
python3 generate_qr.py --url "https://example.com"
```

### 📞 Phone

```bash
python3 generate_qr.py --tel "+441234567890"
```

### 📶 WiFi

```bash
python3 generate_qr.py --wifi "SSID" "WPA2" "mypassword"
```

### 👤 vCard

```bash
python3 generate_qr.py --vcard "Will Curtis" "NXTGen Tech" "+441234567890" "will@example.com" "CTO"
```

### 💬 SMS

```bash
python3 generate_qr.py --sms "+441234567890" "Hello there!"
```

### 📅 Calendar Event

```bash
python3 generate_qr.py --event "Meeting" "2025-06-01T14:00" "2025-06-01T15:00" "HQ" "Discuss roadmap"
```

### 📝 Plain Text

```bash
python3 generate_qr.py --text "Hello from QR world!"
```

---

## 💾 Output

By default, the QR code is saved as `qrcode.png`. Use `--output` to specify a custom filename:

```bash
python3 generate_qr.py --url "https://example.com" --output mysite.png
```

---

## 📁 License

MIT License. Free to use, modify, and distribute.

---

## ✨ Credits

Built by [Your Name] at [Your GitHub or Company Link]
