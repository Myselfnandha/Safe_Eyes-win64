"""Fullscreen break screen overlay for SafeEyes Windows using tkinter.

Replaces the GTK-based break screen with a native Windows tkinter implementation.
Covers all monitors with a dark overlay showing the break message and countdown.
"""

import logging
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional

from safeeyes_windows.model import Break

logger = logging.getLogger(__name__)


class BreakScreen:
    """Manages fullscreen break overlay windows across all monitors."""

    def __init__(
        self,
        on_skipped: Callable[[], None],
        on_postponed: Callable[[], None],
    ):
        self.on_skipped = on_skipped
        self.on_postponed = on_postponed

        self._root: Optional[tk.Tk] = None
        self._windows: list = []
        self._countdown_labels: list[tk.Label] = []
        self._message_labels: list[tk.Label] = []
        self._skip_buttons: list[tk.Button] = []
        self._postpone_buttons: list[tk.Button] = []
        self._buttons_enabled: bool = False

        # Settings
        self.allow_postpone: bool = True
        self.strict_break: bool = False
        self.shortcut_disable_time: int = 2

    def show(self, break_obj: Break, allow_postpone: bool = True, strict_break: bool = False) -> None:
        """Show fullscreen break overlay on all monitors."""
        self.allow_postpone = allow_postpone
        self.strict_break = strict_break
        self._buttons_enabled = False

        try:
            if self._root is None:
                self._root = tk.Tk()
                self._root.withdraw()  # Hide the root window

            self._create_overlay(break_obj)
        except Exception as e:
            logger.error("Failed to show break screen: %s", e)

    def _create_overlay(self, break_obj: Break) -> None:
        """Create fullscreen overlay windows."""
        if self._root is None:
            return

        # Colors
        if break_obj.is_long_break():
            bg_color = "#0a0e27"
            accent_color = "#6c63ff"
            glow_color = "#8b83ff"
        else:
            bg_color = "#0d1117"
            accent_color = "#58a6ff"
            glow_color = "#79c0ff"

        # Get screen dimensions - single monitor overlay
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()

        win = tk.Toplevel(self._root)
        win.title("SafeEyes Break")
        win.configure(bg=bg_color)
        win.attributes("-fullscreen", True)
        win.attributes("-topmost", True)
        win.overrideredirect(True)
        win.geometry(f"{screen_w}x{screen_h}+0+0")

        # Prevent Alt+F4
        win.protocol("WM_DELETE_WINDOW", lambda: None)

        # Main container
        container = tk.Frame(win, bg=bg_color)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Break type indicator
        break_type_text = "LONG BREAK" if break_obj.is_long_break() else "SHORT BREAK"
        lbl_type = tk.Label(
            container,
            text=f"— {break_type_text} —",
            font=("Segoe UI", 12, "bold"),
            fg=accent_color,
            bg=bg_color,
            pady=5,
        )
        lbl_type.pack()

        # Eye icon
        lbl_icon = tk.Label(
            container,
            text="👁️",
            font=("Segoe UI Emoji", 48),
            bg=bg_color,
            pady=15,
        )
        lbl_icon.pack()

        # Break message
        lbl_message = tk.Label(
            container,
            text=break_obj.name,
            font=("Segoe UI", 28, "bold"),
            fg="#e6edf3",
            bg=bg_color,
            wraplength=800,
            pady=10,
        )
        lbl_message.pack()
        self._message_labels.append(lbl_message)

        # Countdown timer
        lbl_countdown = tk.Label(
            container,
            text="00:00",
            font=("Segoe UI", 72, "bold"),
            fg=glow_color,
            bg=bg_color,
            pady=20,
        )
        lbl_countdown.pack()
        self._countdown_labels.append(lbl_countdown)

        # Subtitle
        lbl_sub = tk.Label(
            container,
            text="Take care of your eyes",
            font=("Segoe UI", 14),
            fg="#8b949e",
            bg=bg_color,
            pady=5,
        )
        lbl_sub.pack()

        # Button frame
        btn_frame = tk.Frame(container, bg=bg_color, pady=30)
        btn_frame.pack()

        # Button styling
        btn_font = ("Segoe UI", 13, "bold")
        btn_padx = 30
        btn_pady = 10

        if not self.strict_break:
            # Skip button
            btn_skip = tk.Button(
                btn_frame,
                text="⏭  Skip",
                font=btn_font,
                fg="#c9d1d9",
                bg="#21262d",
                activebackground="#30363d",
                activeforeground="#e6edf3",
                bd=0,
                padx=btn_padx,
                pady=btn_pady,
                cursor="hand2",
                state="disabled",
                disabledforeground="#484f58",
                command=self._on_skip,
            )
            btn_skip.pack(side="left", padx=10)
            self._skip_buttons.append(btn_skip)

        if self.allow_postpone:
            # Postpone button
            btn_postpone = tk.Button(
                btn_frame,
                text="⏸  Postpone",
                font=btn_font,
                fg="#ffffff",
                bg=accent_color,
                activebackground=glow_color,
                activeforeground="#ffffff",
                bd=0,
                padx=btn_padx,
                pady=btn_pady,
                cursor="hand2",
                state="disabled",
                disabledforeground="#6e7681",
                command=self._on_postpone,
            )
            btn_postpone.pack(side="left", padx=10)
            self._postpone_buttons.append(btn_postpone)

        # Keyboard bindings
        win.bind("<Escape>", lambda e: self._on_skip() if self._buttons_enabled else None)
        win.bind("<space>", lambda e: self._on_postpone() if self._buttons_enabled else None)

        # Focus the window
        win.focus_force()
        win.lift()

        self._windows.append(win)

    def update_countdown(self, countdown: int, seconds_elapsed: int) -> None:
        """Update countdown display on all screens."""
        mins, secs = divmod(countdown, 60)
        time_str = f"{mins:02d}:{secs:02d}"

        # Enable buttons after shortcut_disable_time
        if seconds_elapsed >= self.shortcut_disable_time and not self._buttons_enabled:
            self._buttons_enabled = True
            for btn in self._skip_buttons:
                try:
                    btn.configure(state="normal")
                except tk.TclError:
                    pass
            for btn in self._postpone_buttons:
                try:
                    btn.configure(state="normal")
                except tk.TclError:
                    pass

        for lbl in self._countdown_labels:
            try:
                lbl.configure(text=time_str)
            except tk.TclError:
                pass

        # Process tkinter events
        if self._root:
            try:
                self._root.update()
            except tk.TclError:
                pass

    def close(self) -> None:
        """Close all break screen windows."""
        logger.info("Closing break screen(s)")
        for win in self._windows:
            try:
                win.destroy()
            except tk.TclError:
                pass
        self._windows.clear()
        self._countdown_labels.clear()
        self._message_labels.clear()
        self._skip_buttons.clear()
        self._postpone_buttons.clear()
        self._buttons_enabled = False

        # Keep root alive for reuse
        if self._root:
            try:
                self._root.update()
            except tk.TclError:
                pass

    def destroy(self) -> None:
        """Fully destroy the tkinter root."""
        self.close()
        if self._root:
            try:
                self._root.destroy()
            except tk.TclError:
                pass
            self._root = None

    def _on_skip(self) -> None:
        if self._buttons_enabled and not self.strict_break:
            self.on_skipped()

    def _on_postpone(self) -> None:
        if self._buttons_enabled and self.allow_postpone:
            self.on_postponed()

    def is_showing(self) -> bool:
        return len(self._windows) > 0
