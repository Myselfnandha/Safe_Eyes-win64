"""SafeEyes for Windows - Entry point.

Run with: python -m safeeyes_windows
"""

import ctypes
import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def ensure_single_instance() -> bool:
    """Ensure only one instance is running using a Windows mutex."""
    try:
        _mutex = ctypes.windll.kernel32.CreateMutexW(  # noqa: F841
            None, False, "SafeEyes_Windows_Mutex"
        )
        last_err = ctypes.windll.kernel32.GetLastError()
        if last_err == 183:  # ERROR_ALREADY_EXISTS
            logging.warning("SafeEyes is already running!")
            return False
        return True
    except Exception:
        return True  # Proceed if mutex fails


def main() -> None:
    """Main entry point."""
    debug = "--debug" in sys.argv
    setup_logging(debug)

    logger = logging.getLogger(__name__)
    logger.info("SafeEyes for Windows starting...")

    if not ensure_single_instance():
        print("SafeEyes is already running. Exiting.")
        sys.exit(1)

    # Set DPI awareness for crisp rendering
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    from safeeyes_windows.app import SafeEyesApp

    app = SafeEyesApp()
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        app.quit()
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        app.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
