"""Main SafeEyes Windows application orchestrator.

Wires together the core scheduler, break screen, tray icon,
notifications, and audio alerts.
"""

import datetime
import logging
import threading
import tkinter as tk
from typing import Optional

from safeeyes_windows.model import Break, Config, State
from safeeyes_windows.core import SafeEyesCore
from safeeyes_windows.break_screen import BreakScreen
from safeeyes_windows.tray import TrayIcon
from safeeyes_windows import notification, audio

logger = logging.getLogger(__name__)


class SafeEyesApp:
    """Main application class that orchestrates all components."""

    def __init__(self):
        self.config = Config()
        self.core = SafeEyesCore()
        self.active = False

        # Tkinter root for the break screen - must run on main thread
        self._root: Optional[tk.Tk] = None
        self._break_screen: Optional[BreakScreen] = None

        # System tray
        self.tray = TrayIcon(
            on_enable=self.enable,
            on_disable=self.disable,
            on_take_break=self.take_break,
            on_settings=self.show_settings,
            on_quit=self.quit,
        )

        # Wire up core callbacks
        self.core.on_pre_break = self._on_pre_break
        self.core.on_start_break = self._on_start_break
        self.core.on_countdown = self._on_countdown
        self.core.on_stop_break = self._on_stop_break
        self.core.on_update_next_break = self._on_update_next_break

        self._running = True

    def run(self) -> None:
        """Start the application. This is the main entry point."""
        logger.info("Starting SafeEyes for Windows")

        # Initialize tkinter on main thread
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.title("SafeEyes")

        # Create break screen
        self._break_screen = BreakScreen(
            on_skipped=self._user_skipped,
            on_postponed=self._user_postponed,
        )

        # Initialize and start core
        self.core.initialize(self.config)

        # Start tray icon (runs in background thread)
        self.tray.start()

        # Start the scheduler
        self.enable()

        # Start polling loop and run tkinter mainloop
        self._root.after(100, self._poll_loop)
        self._root.mainloop()

    def _poll_loop(self) -> None:
        """Keep tkinter responsive while app is running."""
        if self._root is None:
            return
        if self._running:
            self._root.after(100, self._poll_loop)
        else:
            self._root.quit()

    def enable(self) -> None:
        """Enable Safe Eyes."""
        if not self.active:
            logger.info("Enable SafeEyes")
            self.active = True
            self.core.start()
            self.tray.set_enabled(True)
            self.tray.update_status("Enabled - waiting for first break")

    def disable(self) -> None:
        """Disable Safe Eyes."""
        if self.active:
            logger.info("Disable SafeEyes")
            self.active = False
            self.core.stop()
            self.tray.set_enabled(False)
            self.tray.update_status("Disabled")
            # Close any active break screen
            if self._break_screen:
                self._safe_tk_call(self._break_screen.close)

    def take_break(self) -> None:
        """Force a break now."""
        if self.active:
            self.core.take_break_now()

    def show_settings(self) -> None:
        """Open the settings dialog."""
        from safeeyes_windows.settings_dialog import SettingsDialog

        def _show():
            dialog = SettingsDialog(self.config, self._on_settings_saved)
            dialog.show(self._root)

        self._safe_tk_call(_show)

    def quit(self) -> None:
        """Quit the application."""
        logger.info("Quitting SafeEyes")
        self._running = False
        self.core.stop()
        self.tray.stop()

        if self._break_screen:
            try:
                self._break_screen.destroy()
            except Exception:
                pass

        if self._root:
            try:
                self._root.after(0, self._root.quit)
            except Exception:
                pass

    # --- Core callbacks (called from timer threads) ---

    def _on_pre_break(self, brk: Break) -> None:
        """Called before a break starts (pre-break warning)."""
        logger.info("Pre-break: %s", brk.name)
        warning_time = self.config.get("pre_break_warning_time", 10)

        if self.config.get("audible_alert", True):
            audio.play_pre_break_sound()

        notification.notify_pre_break(brk.name, warning_time)

    def _on_start_break(self, brk: Break) -> None:
        """Called when a break starts."""
        logger.info("Start break: %s (%ds)", brk.name, brk.duration)

        def _show_break():
            if self._break_screen:
                self._break_screen.allow_postpone = self.config.get("allow_postpone", True)
                self._break_screen.strict_break = self.config.get("strict_break", False)
                self._break_screen.shortcut_disable_time = self.config.get("shortcut_disable_time", 2)
                self._break_screen.show(
                    brk,
                    allow_postpone=self.config.get("allow_postpone", True),
                    strict_break=self.config.get("strict_break", False),
                )

        self._safe_tk_call(_show_break)

    def _on_countdown(self, countdown: int, seconds_elapsed: int) -> None:
        """Called every second during a break."""
        def _update():
            if self._break_screen:
                self._break_screen.update_countdown(countdown, seconds_elapsed)

        self._safe_tk_call(_update)

    def _on_stop_break(self) -> None:
        """Called when a break ends."""
        logger.info("Break ended")

        if self.config.get("audible_alert", True):
            audio.play_stop_break_sound()

        def _close():
            if self._break_screen:
                self._break_screen.close()

        self._safe_tk_call(_close)

    def _on_update_next_break(self, brk: Break, break_time: datetime.datetime) -> None:
        """Called when the next break time is updated."""
        self.tray.update_next_break(brk.name, break_time)

    # --- User actions from break screen ---

    def _user_skipped(self) -> None:
        """User clicked Skip."""
        self.core.skip()

    def _user_postponed(self) -> None:
        """User clicked Postpone."""
        self.core.postpone()

    # --- Settings ---

    def _on_settings_saved(self, new_config: Config) -> None:
        """Called when settings are saved."""
        logger.info("Settings saved, restarting core")
        was_active = self.active
        if self.active:
            self.disable()

        self.config = new_config
        self.core.initialize(self.config)

        if was_active:
            self.enable()

    # --- Helpers ---

    def _safe_tk_call(self, func) -> None:
        """Schedule a function to run on the tkinter main thread."""
        if self._root:
            try:
                self._root.after(0, func)
            except tk.TclError:
                pass
