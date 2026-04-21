"""Settings dialog for SafeEyes Windows using tkinter."""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from safeeyes_windows.model import Config

logger = logging.getLogger(__name__)


class SettingsDialog:
    """Tkinter-based settings window."""

    def __init__(self, config: Config, on_save: Callable[[Config], None]):
        self._config = config.clone()
        self._save_callback = on_save
        self._window: Optional[tk.Toplevel] = None

    def show(self, parent: Optional[tk.Tk] = None) -> None:
        """Show the settings dialog."""
        if self._window is not None:
            try:
                self._window.lift()
                self._window.focus_force()
                return
            except tk.TclError:
                self._window = None

        root = parent or tk.Tk()
        if parent is None:
            root.withdraw()

        win = tk.Toplevel(root)
        self._window = win
        win.title("SafeEyes — Settings")
        win.geometry("520x620")
        win.resizable(False, False)
        win.configure(bg="#1a1b26")
        win.attributes("-topmost", True)

        # Title
        tk.Label(
            win, text="⚙️  Settings", font=("Segoe UI", 20, "bold"),
            fg="#c0caf5", bg="#1a1b26", pady=15
        ).pack(fill="x")

        # Scrollable content
        canvas = tk.Canvas(win, bg="#1a1b26", highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg="#1a1b26", padx=30)

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )
        canvas.create_window((0, 0), window=content, anchor="nw", width=490)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0))
        scrollbar.pack(side="right", fill="y")

        # Variables for settings
        vars_dict: dict[str, tk.IntVar | tk.BooleanVar] = {}

        def add_section(title: str) -> None:
            tk.Label(
                content, text=title, font=("Segoe UI", 13, "bold"),
                fg="#7aa2f7", bg="#1a1b26", anchor="w"
            ).pack(fill="x", pady=(15, 5))
            tk.Frame(content, bg="#3b4261", height=1).pack(fill="x", pady=(0, 10))

        def add_spinner(
            label: str, key: str, from_: int, to: int, unit: str = "",
        ) -> None:
            frame = tk.Frame(content, bg="#1a1b26")
            frame.pack(fill="x", pady=4)
            display = f"{label} ({unit})" if unit else label
            tk.Label(
                frame, text=display, font=("Segoe UI", 11),
                fg="#a9b1d6", bg="#1a1b26", anchor="w"
            ).pack(side="left")
            var = tk.IntVar(value=self._config.get(key, from_))
            vars_dict[key] = var
            spin = tk.Spinbox(
                frame, from_=from_, to=to, textvariable=var, width=6,
                font=("Segoe UI", 11), bg="#24283b", fg="#c0caf5",
                buttonbackground="#3b4261", insertbackground="#c0caf5",
                selectbackground="#7aa2f7", bd=0, highlightthickness=1,
                highlightcolor="#7aa2f7", highlightbackground="#3b4261"
            )
            spin.pack(side="right")

        def add_checkbox(label: str, key: str) -> None:
            var = tk.BooleanVar(value=self._config.get(key, False))
            vars_dict[key] = var
            cb = tk.Checkbutton(
                content, text=label, variable=var, font=("Segoe UI", 11),
                fg="#a9b1d6", bg="#1a1b26", selectcolor="#24283b",
                activebackground="#1a1b26", activeforeground="#c0caf5",
                anchor="w", pady=4
            )
            cb.pack(fill="x")

        # --- Break Intervals ---
        add_section("⏱  Break Intervals")
        add_spinner("Short break every", "short_break_interval", 1, 120, "minutes")
        add_spinner("Long break every", "long_break_interval", 1, 240, "minutes")

        # --- Break Duration ---
        add_section("⏳  Break Duration")
        add_spinner("Short break for", "short_break_duration", 5, 120, "seconds")
        add_spinner("Long break for", "long_break_duration", 10, 600, "seconds")

        # --- Behavior ---
        add_section("🎛  Behavior")
        add_spinner("Pre-break warning", "pre_break_warning_time", 0, 30, "seconds")
        add_spinner("Postpone duration", "postpone_duration", 1, 30, "minutes")
        add_spinner("Button lock time", "shortcut_disable_time", 0, 10, "seconds")
        add_checkbox("Allow postpone", "allow_postpone")
        add_checkbox("Strict break (no skip)", "strict_break")
        add_checkbox("Randomize break order", "random_order")
        add_checkbox("Audible alerts", "audible_alert")

        # --- Buttons ---
        btn_frame = tk.Frame(win, bg="#1a1b26", pady=15)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(
            btn_frame, text="Cancel", font=("Segoe UI", 12),
            fg="#a9b1d6", bg="#24283b", activebackground="#3b4261",
            activeforeground="#c0caf5", bd=0, padx=25, pady=8,
            cursor="hand2", command=self._on_cancel
        ).pack(side="right", padx=15)

        tk.Button(
            btn_frame, text="Save", font=("Segoe UI", 12, "bold"),
            fg="#ffffff", bg="#7aa2f7", activebackground="#89b4fa",
            activeforeground="#ffffff", bd=0, padx=30, pady=8,
            cursor="hand2",
            command=lambda: self._on_save(vars_dict)
        ).pack(side="right")

        # Center window
        win.update_idletasks()
        x = (win.winfo_screenwidth() - 520) // 2
        y = (win.winfo_screenheight() - 620) // 2
        win.geometry(f"+{x}+{y}")

        win.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_save(self, vars_dict: dict) -> None:
        """Save settings."""
        for key, var in vars_dict.items():
            self._config.set(key, var.get())
        self._config.save()
        if self._window:
            self._window.destroy()
            self._window = None
        self._save_callback(self._config)

    def _on_cancel(self) -> None:
        """Close without saving."""
        if self._window:
            self._window.destroy()
            self._window = None
