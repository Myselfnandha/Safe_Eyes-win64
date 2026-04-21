"""System tray icon for SafeEyes Windows using pystray."""

import datetime
import logging
import threading
from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def _create_eye_icon(size: int = 64, enabled: bool = True) -> Image.Image:
    """Generate an eye icon programmatically."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r = size // 2 - 2

    if enabled:
        # Outer eye shape - blue gradient effect
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#3b82f6")
        # Inner circle
        inner_r = r * 6 // 10
        draw.ellipse(
            [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
            fill="#1e3a5f"
        )
        # Pupil
        pupil_r = r * 3 // 10
        draw.ellipse(
            [cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r],
            fill="#0f172a"
        )
        # Highlight
        hl_r = r * 1 // 10
        hl_x, hl_y = cx - pupil_r // 2, cy - pupil_r // 2
        draw.ellipse(
            [hl_x - hl_r, hl_y - hl_r, hl_x + hl_r, hl_y + hl_r],
            fill="#ffffff"
        )
    else:
        # Disabled - gray
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#4b5563")
        inner_r = r * 6 // 10
        draw.ellipse(
            [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
            fill="#374151"
        )
        pupil_r = r * 3 // 10
        draw.ellipse(
            [cx - pupil_r, cy - pupil_r, cx + pupil_r, cy + pupil_r],
            fill="#1f2937"
        )
        # Strike-through line
        draw.line(
            [cx - r, cy + r, cx + r, cy - r],
            fill="#ef4444", width=max(2, size // 16)
        )

    return img


class TrayIcon:
    """System tray icon manager using pystray."""

    def __init__(
        self,
        on_enable: Callable[[], None],
        on_disable: Callable[[], None],
        on_take_break: Callable[[], None],
        on_settings: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        self._on_enable = on_enable
        self._on_disable = on_disable
        self._on_take_break = on_take_break
        self._on_settings = on_settings
        self._on_quit = on_quit

        self._icon: Optional[pystray.Icon] = None
        self._enabled: bool = True
        self._status_text: str = "Starting..."
        self._next_break_text: str = ""

    def start(self) -> None:
        """Start the tray icon in a background thread."""
        self._icon = pystray.Icon(
            "SafeEyes",
            icon=_create_eye_icon(64, True),
            title="SafeEyes - Protecting your eyes",
            menu=self._build_menu(),
        )
        # Run in a thread so it doesn't block
        t = threading.Thread(target=self._icon.run, daemon=True)
        t.start()
        logger.info("Tray icon started")

    def stop(self) -> None:
        """Stop the tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def set_enabled(self, enabled: bool) -> None:
        """Update tray icon to show enabled/disabled state."""
        self._enabled = enabled
        if self._icon:
            self._icon.icon = _create_eye_icon(64, enabled)
            self._icon.menu = self._build_menu()
            state = "Enabled" if enabled else "Disabled"
            self._icon.title = f"SafeEyes - {state}"

    def update_status(self, text: str) -> None:
        """Update the status text shown in the menu."""
        self._status_text = text
        if self._icon:
            self._icon.title = f"SafeEyes - {text}"
            self._icon.menu = self._build_menu()

    def update_next_break(self, break_name: str, break_time: datetime.datetime) -> None:
        """Update next break info."""
        time_str = break_time.strftime("%H:%M")
        self._next_break_text = f"Next: {break_name} at {time_str}"
        self._status_text = self._next_break_text
        if self._icon:
            self._icon.title = f"SafeEyes - {self._next_break_text}"
            self._icon.menu = self._build_menu()

    def _build_menu(self) -> pystray.Menu:
        """Build the right-click context menu."""
        items = [
            pystray.MenuItem(
                self._status_text,
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
        ]

        if self._enabled:
            items.extend([
                pystray.MenuItem("⏸  Disable", lambda: self._on_disable()),
                pystray.MenuItem("⏯  Take a break now", lambda: self._on_take_break()),
            ])
        else:
            items.append(
                pystray.MenuItem("▶  Enable", lambda: self._on_enable()),
            )

        items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙  Settings", lambda: self._on_settings()),
            pystray.MenuItem("ℹ  About", lambda: self._show_about()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("✖  Quit", lambda: self._on_quit()),
        ])

        return pystray.Menu(*items)

    def _show_about(self) -> None:
        """Show a simple about dialog."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(
                "About SafeEyes",
                "SafeEyes for Windows\n"
                "Version 1.0.0\n\n"
                "Protect your eyes from eye strain\n"
                "using this continuous break reminder.\n\n"
                "Based on Safe Eyes by Gobinath Loganathan\n"
                "Windows port - 2026",
                parent=root,
            )
            root.destroy()
        except Exception as e:
            logger.warning("About dialog failed: %s", e)
