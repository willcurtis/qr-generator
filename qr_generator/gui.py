"""CustomTkinter desktop interface for The Tech Shed QR Generator."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from .core import create_qr
from .payloads import PayloadError, make_event, make_sms, make_tel, make_text, make_url, make_vcard, make_wifi
from .theme import BACKGROUND, BORDER, CARD, CYAN, CYAN_HOVER, DANGER, MUTED, SURFACE, TEAL, TEXT

FORMATS: dict[str, tuple[tuple[str, str, bool], ...]] = {
    "URL": (("URL", "https://example.com", False),),
    "Phone": (("Phone number", "+441234567890", False),),
    "Wi-Fi": (
        ("Network name (SSID)", "The Tech Shed", False),
        ("Security", "WPA2", False),
        ("Password", "Password", True),
    ),
    "vCard": (
        ("Full name", "Will Curtis", False),
        ("Organisation", "The Tech Shed", False),
        ("Phone number", "+441234567890", False),
        ("Email", "will@example.com", False),
        ("Job title", "Director", False),
    ),
    "SMS": (("Phone number", "+441234567890", False), ("Message", "Hello there!", False)),
    "Calendar": (
        ("Event title", "Meeting", False),
        ("Start (YYYY-MM-DDTHH:MM)", "2026-08-03T14:00", False),
        ("End (YYYY-MM-DDTHH:MM)", "2026-08-03T15:00", False),
        ("Location", "HQ", False),
        ("Description", "Discuss roadmap", False),
    ),
    "Text": (("Text", "Hello from The Tech Shed!", False),),
}


class QRGeneratorApp(ctk.CTk):
    """Single-window QR generator with live preview and save controls."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("The Tech Shed | QR Generator")
        self.geometry("1060x780")
        self.minsize(920, 700)
        self.configure(fg_color=BACKGROUND)
        self.entries: list[ctk.CTkEntry] = []
        self.preview_image: ctk.CTkImage | None = None
        self.qr_image = None
        self._build()
        self._build_form("URL")

    def _build(self) -> None:
        ctk.CTkFrame(self, height=3, corner_radius=0, fg_color=TEAL).pack(fill="x")
        header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER)
        header.pack(fill="x", padx=24, pady=(20, 14))
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=22, pady=15)
        ctk.CTkLabel(title_box, text="THE TECH SHED", text_color=TEAL, font=("Arial", 11, "bold")).pack(anchor="w")
        ctk.CTkLabel(title_box, text="QR Generator", text_color=TEXT, font=("Arial", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Create polished QR codes for links, contacts, Wi-Fi and more.",
            text_color=MUTED,
            font=("Arial", 13),
        ).pack(side="right", padx=22)

        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=24)
        workspace.grid_columnconfigure(0, weight=3)
        workspace.grid_columnconfigure(1, weight=2)
        workspace.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(workspace, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="CONTENT TYPE", text_color=MUTED, font=("Arial", 11, "bold")).pack(
            anchor="w", padx=22, pady=(20, 8)
        )
        self.format_choice = ctk.CTkOptionMenu(
            left,
            values=list(FORMATS),
            command=self._build_form,
            fg_color=CARD,
            button_color=CYAN,
            button_hover_color=CYAN_HOVER,
            dropdown_fg_color=CARD,
        )
        self.format_choice.pack(fill="x", padx=22)
        self.form = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.form.pack(fill="both", expand=True, padx=10, pady=8)

        options = ctk.CTkFrame(left, fg_color="transparent")
        options.pack(fill="x", padx=22, pady=(0, 12))
        self.error_level = self._option(options, "Error correction", ("L", "M", "Q", "H"), "Q", 0)
        self.box_size = self._option(options, "Pixel scale", tuple(str(i) for i in (5, 8, 10, 12, 16)), "10", 1)
        self.foreground = self._entry_option(options, "Foreground", "black", 2)
        self.background = self._entry_option(options, "Background", "white", 3)

        right = ctk.CTkFrame(workspace, fg_color=SURFACE, corner_radius=18, border_width=1, border_color=BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(right, text="PREVIEW", text_color=MUTED, font=("Arial", 11, "bold")).pack(
            anchor="w", padx=22, pady=(20, 10)
        )
        preview_card = ctk.CTkFrame(right, width=330, height=330, fg_color=CARD, corner_radius=14)
        preview_card.pack(padx=22, pady=4, fill="both", expand=True)
        preview_card.pack_propagate(False)
        self.preview = ctk.CTkLabel(preview_card, text="Your QR preview\nwill appear here", text_color=MUTED)
        self.preview.pack(expand=True)
        self.status = ctk.CTkLabel(right, text="Enter your details, then generate a preview.", text_color=MUTED)
        self.status.pack(padx=22, pady=(12, 6))
        ctk.CTkButton(
            right,
            text="Generate preview",
            command=self.generate_preview,
            height=42,
            fg_color=CYAN,
            hover_color=CYAN_HOVER,
            text_color=BACKGROUND,
            font=("Arial", 13, "bold"),
        ).pack(fill="x", padx=22, pady=6)
        self.save_button = ctk.CTkButton(
            right,
            text="Save QR code",
            command=self.save,
            state="disabled",
            height=42,
            fg_color=TEAL,
            hover_color="#00B58A",
            text_color=BACKGROUND,
            font=("Arial", 13, "bold"),
        )
        self.save_button.pack(fill="x", padx=22, pady=(6, 20))

        footer = ctk.CTkFrame(self, fg_color="transparent", height=44)
        footer.pack(fill="x", padx=24, pady=(10, 8))
        ctk.CTkLabel(footer, text="QR Generator v1.0.0", text_color=MUTED).pack(side="left")
        link = ctk.CTkLabel(footer, text="© 2026 The Tech Shed", text_color=CYAN, cursor="hand2")
        link.pack(side="right")
        link.bind("<Button-1>", lambda _event: webbrowser.open("https://thetechshed.dev"))

    def _option(self, parent, label: str, values: tuple[str, ...], default: str, column: int):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=column, sticky="ew", padx=4)
        parent.grid_columnconfigure(column, weight=1)
        ctk.CTkLabel(box, text=label, text_color=MUTED, font=("Arial", 10)).pack(anchor="w")
        widget = ctk.CTkOptionMenu(box, values=list(values), fg_color=CARD, button_color=BORDER)
        widget.set(default)
        widget.pack(fill="x")
        return widget

    def _entry_option(self, parent, label: str, default: str, column: int):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=column, sticky="ew", padx=4)
        parent.grid_columnconfigure(column, weight=1)
        ctk.CTkLabel(box, text=label, text_color=MUTED, font=("Arial", 10)).pack(anchor="w")
        widget = ctk.CTkEntry(box, fg_color=CARD, border_color=BORDER)
        widget.insert(0, default)
        widget.pack(fill="x")
        return widget

    def _build_form(self, selected: str) -> None:
        for child in self.form.winfo_children():
            child.destroy()
        self.entries.clear()
        for label, placeholder, secret in FORMATS[selected]:
            ctk.CTkLabel(self.form, text=label, text_color=MUTED, font=("Arial", 11, "bold")).pack(
                anchor="w", padx=10, pady=(9, 3)
            )
            entry = ctk.CTkEntry(
                self.form,
                placeholder_text=placeholder,
                show="•" if secret else "",
                height=38,
                fg_color=CARD,
                border_color=BORDER,
                text_color=TEXT,
            )
            entry.pack(fill="x", padx=10)
            self.entries.append(entry)

    def _payload(self) -> str:
        values = [entry.get() for entry in self.entries]
        selected = self.format_choice.get()
        builders = {
            "URL": make_url,
            "Phone": make_tel,
            "Wi-Fi": make_wifi,
            "vCard": make_vcard,
            "SMS": make_sms,
            "Calendar": make_event,
            "Text": make_text,
        }
        return builders[selected](*values)

    def generate_preview(self) -> None:
        try:
            self.qr_image = create_qr(
                self._payload(),
                error_correction=self.error_level.get(),
                box_size=int(self.box_size.get()),
                foreground=self.foreground.get(),
                background=self.background.get(),
            )
            preview = self.qr_image.get_image().copy()
            self.preview_image = ctk.CTkImage(light_image=preview, dark_image=preview, size=(300, 300))
            self.preview.configure(image=self.preview_image, text="")
            self.status.configure(text="Preview ready", text_color=TEAL)
            self.save_button.configure(state="normal")
        except (PayloadError, ValueError) as exc:
            self.status.configure(text=str(exc), text_color=DANGER)
            self.save_button.configure(state="disabled")

    def save(self) -> None:
        if self.qr_image is None:
            return
        filename = filedialog.asksaveasfilename(
            title="Save QR code",
            defaultextension=".png",
            filetypes=(("PNG image", "*.png"), ("JPEG image", "*.jpg *.jpeg")),
        )
        if not filename:
            return
        try:
            self.qr_image.save(Path(filename))
            self.status.configure(text=f"Saved {Path(filename).name}", text_color=TEAL)
        except OSError as exc:
            self.status.configure(text=f"Could not save: {exc}", text_color=DANGER)


def run() -> None:
    QRGeneratorApp().mainloop()


if __name__ == "__main__":
    run()
