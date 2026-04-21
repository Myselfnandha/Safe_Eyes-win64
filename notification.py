"""Windows toast notifications for SafeEyes."""

import logging
import threading

logger = logging.getLogger(__name__)


def notify(title: str, message: str) -> None:
    """Show a Windows toast notification."""
    def _do_notify():
        try:
            from plyer import notification as plyer_notify
            plyer_notify.notify(
                title=title,
                message=message,
                app_name="SafeEyes",
                timeout=8,
            )
        except Exception as e:
            logger.warning("Notification failed: %s", e)

    t = threading.Thread(target=_do_notify, daemon=True)
    t.start()


def notify_pre_break(break_name: str, seconds: int) -> None:
    """Notify user about upcoming break."""
    notify(
        "👁️ Break coming up!",
        f'"{break_name}" in {seconds} seconds',
    )
