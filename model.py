"""Data models for SafeEyes Windows."""

import json
import logging
import os
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BreakType(Enum):
    """Type of break."""

    SHORT_BREAK = 1
    LONG_BREAK = 2


class State(Enum):
    """Application states."""

    WAITING = 1
    PRE_BREAK = 2
    BREAK = 3
    STOPPED = 4
    QUIT = 5


@dataclass
class Break:
    """Represents a single break."""

    type: BreakType
    name: str
    time: int  # interval in minutes
    duration: int  # duration in seconds

    def is_long_break(self) -> bool:
        return self.type == BreakType.LONG_BREAK

    def is_short_break(self) -> bool:
        return self.type == BreakType.SHORT_BREAK


class BreakQueue:
    """Manages the queue of breaks, alternating short and long."""

    def __init__(self, config: "Config"):
        self._short_queue: List[Break] = []
        self._long_queue: List[Break] = []
        self._current_short: int = 0
        self._current_long: int = 0
        self._is_random: bool = config.get("random_order", True)

        short_time = config.get("short_break_interval", 15)
        long_time = config.get("long_break_interval", 75)
        short_dur = config.get("short_break_duration", 15)
        long_dur = config.get("long_break_duration", 60)

        for bc in config.get("short_breaks", []):
            dur = bc.get("duration", short_dur)
            interval = bc.get("interval", short_time)
            self._short_queue.append(
                Break(BreakType.SHORT_BREAK, bc["name"], interval, dur)
            )

        for bc in config.get("long_breaks", []):
            dur = bc.get("duration", long_dur)
            interval = bc.get("interval", long_time)
            self._long_queue.append(
                Break(BreakType.LONG_BREAK, bc["name"], interval, dur)
            )

        if self._is_random:
            random.shuffle(self._short_queue)
            random.shuffle(self._long_queue)

        # Track accumulated time to know when long break is due
        self._accumulated_time: int = 0
        self._long_break_interval: int = long_time

    def has_breaks(self) -> bool:
        return len(self._short_queue) > 0 or len(self._long_queue) > 0

    def get_break(self) -> Optional[Break]:
        """Get the next break to take based on accumulated time."""
        if not self.has_breaks():
            return None

        # Check if it's time for a long break
        if (
            self._long_queue
            and self._accumulated_time >= self._long_break_interval
        ):
            brk = self._long_queue[self._current_long]
            return brk

        if self._short_queue:
            brk = self._short_queue[self._current_short]
            return brk

        if self._long_queue:
            return self._long_queue[self._current_long]

        return None

    def get_wait_time(self) -> int:
        """Get wait time in seconds until next break."""
        brk = self.get_break()
        if brk is None:
            return 900  # fallback 15 min
        return brk.time * 60

    def advance(self) -> None:
        """Move to the next break in the queue."""
        brk = self.get_break()
        if brk is None:
            return

        if brk.is_long_break():
            self._current_long = (self._current_long + 1) % len(self._long_queue)
            self._accumulated_time = 0
            if self._current_long == 0 and self._is_random:
                random.shuffle(self._long_queue)
        else:
            self._accumulated_time += brk.time
            self._current_short = (self._current_short + 1) % len(self._short_queue)
            if self._current_short == 0 and self._is_random:
                random.shuffle(self._short_queue)


# Paths
APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_DIR = APP_DIR / "resources"
CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / "SafeEyes"
USER_CONFIG_PATH = CONFIG_DIR / "safeeyes.json"
SESSION_PATH = CONFIG_DIR / "session.json"
DEFAULT_CONFIG_PATH = APP_DIR / "config.json"


class Config:
    """Configuration manager."""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load config from user file, falling back to defaults."""
        # Load defaults first
        if DEFAULT_CONFIG_PATH.exists():
            with open(DEFAULT_CONFIG_PATH, "r") as f:
                self._data = json.load(f)

        # Override with user config
        if USER_CONFIG_PATH.exists():
            try:
                with open(USER_CONFIG_PATH, "r") as f:
                    user_data = json.load(f)
                self._data.update(user_data)
            except Exception as e:
                logging.warning("Failed to load user config: %s", e)

    def save(self) -> None:
        """Save current config to user config file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(USER_CONFIG_PATH, "w") as f:
            json.dump(self._data, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def clone(self) -> "Config":
        c = Config.__new__(Config)
        c._data = json.loads(json.dumps(self._data))
        return c
