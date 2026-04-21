"""Audio alerts for SafeEyes Windows using winsound."""

import logging
import os
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

RESOURCES_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "resources"


def _play_sound(filename: str) -> None:
    """Play a WAV file in a background thread."""
    filepath = RESOURCES_DIR / filename
    if not filepath.exists():
        logger.warning("Sound file not found: %s", filepath)
        return

    def _do_play():
        try:
            import winsound
            winsound.PlaySound(str(filepath), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            logger.warning("Failed to play sound: %s", e)

    t = threading.Thread(target=_do_play, daemon=True)
    t.start()


def play_pre_break_sound() -> None:
    """Play the pre-break alert sound."""
    _play_sound("on_pre_break.wav")


def play_stop_break_sound() -> None:
    """Play the break-ended sound."""
    _play_sound("on_stop_break.wav")
