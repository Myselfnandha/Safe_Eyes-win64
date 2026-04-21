"""Core break scheduler for SafeEyes Windows.

Replaces GLib.timeout_add_seconds with threading.Timer for Windows compatibility.
"""

import datetime
import logging
import threading
from typing import Callable, Optional

from safeeyes_windows.model import Break, BreakQueue, Config, State

logger = logging.getLogger(__name__)


class SafeEyesCore:
    """Core scheduler that manages break timing and state transitions."""

    def __init__(self):
        self.state: State = State.STOPPED
        self.running: bool = False
        self._timer: Optional[threading.Timer] = None
        self._break_queue: Optional[BreakQueue] = None
        self._lock = threading.Lock()

        # Config values
        self.pre_break_warning_time: int = 10
        self.postpone_duration: int = 300  # seconds
        self.shortcut_disable_time: int = 2

        # Current break state
        self._countdown: int = 0
        self._current_break: Optional[Break] = None
        self.scheduled_next_break_time: Optional[datetime.datetime] = None

        # Callbacks
        self.on_pre_break: Optional[Callable[[Break], None]] = None
        self.on_start_break: Optional[Callable[[Break], None]] = None
        self.on_countdown: Optional[Callable[[int, int], None]] = None
        self.on_stop_break: Optional[Callable[[], None]] = None
        self.on_update_next_break: Optional[
            Callable[[Break, datetime.datetime], None]
        ] = None

    def initialize(self, config: Config) -> None:
        """Initialize from config."""
        logger.info("Initialize the core")
        self.pre_break_warning_time = config.get("pre_break_warning_time", 10)
        postpone_min = config.get("postpone_duration", 5)
        self.postpone_duration = postpone_min * 60
        self.shortcut_disable_time = config.get("shortcut_disable_time", 2)
        self._break_queue = BreakQueue(config)

    def start(self) -> None:
        """Start the break scheduler."""
        if self._break_queue is None or not self._break_queue.has_breaks():
            logger.info("No breaks defined, not starting")
            return

        if not self.running:
            logger.info("Start SafeEyes core")
            self.running = True
            self.state = State.WAITING
            self._schedule_next_break()

    def stop(self) -> None:
        """Stop the break scheduler."""
        if not self.running:
            return
        logger.info("Stop SafeEyes core")
        self.running = False
        self.state = State.STOPPED
        self._cancel_timer()

    def skip(self) -> None:
        """User skipped the current break."""
        logger.info("Break skipped")
        self._cancel_timer()
        self._current_break = None
        if self.on_stop_break:
            self.on_stop_break()
        self._advance_and_schedule()

    def postpone(self) -> None:
        """User postponed the current break."""
        logger.info("Break postponed for %d seconds", self.postpone_duration)
        self._cancel_timer()
        self._current_break = None
        if self.on_stop_break:
            self.on_stop_break()
        # Schedule with postpone duration instead of normal interval
        self._schedule_with_delay(self.postpone_duration)

    def take_break_now(self) -> None:
        """Force a break immediately."""
        if self.state != State.WAITING:
            return
        self._cancel_timer()
        self._do_start_break()

    def has_breaks(self) -> bool:
        return self._break_queue is not None and self._break_queue.has_breaks()

    def _cancel_timer(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def _set_timer(self, delay: float, callback: Callable) -> None:
        self._cancel_timer()
        with self._lock:
            self._timer = threading.Timer(delay, callback)
            self._timer.daemon = True
            self._timer.start()

    def _schedule_next_break(self) -> None:
        """Schedule the next break based on queue timing."""
        if not self.running or self._break_queue is None:
            return

        wait_seconds = self._break_queue.get_wait_time()
        self._schedule_with_delay(wait_seconds)

    def _schedule_with_delay(self, delay_seconds: int) -> None:
        """Schedule next break with a specific delay."""
        if not self.running or self._break_queue is None:
            return

        self.state = State.WAITING
        now = datetime.datetime.now()
        self.scheduled_next_break_time = now + datetime.timedelta(seconds=delay_seconds)

        brk = self._break_queue.get_break()
        if brk and self.on_update_next_break:
            self.on_update_next_break(brk, self.scheduled_next_break_time)

        logger.info(
            "Next break in %d minutes (%s)",
            delay_seconds // 60,
            self.scheduled_next_break_time.strftime("%H:%M:%S"),
        )

        # Wait, then fire pre-break
        pre_break_delay = max(0, delay_seconds - self.pre_break_warning_time)
        self._set_timer(pre_break_delay, self._do_pre_break)

    def _do_pre_break(self) -> None:
        """Fire pre-break notification, then wait for warning period."""
        if not self.running or self._break_queue is None:
            return

        self.state = State.PRE_BREAK
        brk = self._break_queue.get_break()
        if brk and self.on_pre_break:
            self.on_pre_break(brk)

        # Wait the warning period, then start the break
        self._set_timer(self.pre_break_warning_time, self._do_start_break)

    def _do_start_break(self) -> None:
        """Start the actual break."""
        if not self.running or self._break_queue is None:
            return

        brk = self._break_queue.get_break()
        if brk is None:
            return

        self.state = State.BREAK
        self._current_break = brk
        self._countdown = brk.duration

        if self.on_start_break:
            self.on_start_break(brk)

        # Start countdown
        self._tick_countdown()

    def _tick_countdown(self) -> None:
        """Tick the countdown by 1 second."""
        if not self.running or self._current_break is None:
            return

        if self._countdown > 0:
            total = self._current_break.duration
            seconds_elapsed = total - self._countdown
            if self.on_countdown:
                self.on_countdown(self._countdown, seconds_elapsed)
            self._countdown -= 1
            self._set_timer(1, self._tick_countdown)
        else:
            # Break finished naturally
            logger.info("Break finished")
            self._current_break = None
            if self.on_stop_break:
                self.on_stop_break()
            self._advance_and_schedule()

    def _advance_and_schedule(self) -> None:
        """Advance queue and schedule next break."""
        if self._break_queue is not None:
            self._break_queue.advance()
        self._schedule_next_break()
