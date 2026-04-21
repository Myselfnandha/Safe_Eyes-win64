<div align="center">

# 👁️ SafeEyes for Windows

**Protect your eyes from eye strain with smart break reminders.**

A Windows-native system tray application that reminds you to take regular breaks — built as a full port of the popular Linux [Safe Eyes](https://github.com/slgobinath/SafeEyes) app.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)

<img src="safeeyes_windows/resources/screenshot_break.png" alt="SafeEyes Break Screen" width="720" />

</div>

---

## Why SafeEyes?

Staring at screens for long periods causes **digital eye strain** — dry eyes, headaches, blurred vision, and neck pain. The **20-20-20 rule** recommends looking at something 20 feet away for 20 seconds every 20 minutes. SafeEyes automates this with configurable break intervals and a fullscreen overlay that gently reminds you to rest.

## Features

| Feature | Description |
|---------|-------------|
| 🔔 **Smart Break Scheduling** | Short breaks every 15 min, long breaks every 75 min (fully configurable) |
| 🖥️ **Fullscreen Break Overlay** | Dark-themed overlay with countdown timer covers your screen during breaks |
| 📌 **System Tray Integration** | Lives quietly in your Windows taskbar notification area |
| ⏭️ **Skip & Postpone** | Skip a break entirely or postpone it for later |
| ⌨️ **Keyboard Shortcuts** | `Escape` to skip, `Space` to postpone during a break |
| 🔊 **Audible Alerts** | Sound notification before and after each break |
| 💬 **Toast Notifications** | Windows 10/11 native notification 10 seconds before a break |
| ⚙️ **Settings Dialog** | Configure intervals, durations, and behavior from a sleek dark UI |
| 🔁 **Randomized Breaks** | Eye exercises are shown in random order to keep things fresh |
| 🔒 **Single Instance** | Windows mutex ensures only one instance runs at a time |
| 💾 **Persistent Config** | Settings saved to `%APPDATA%\SafeEyes\safeeyes.json` |

## Quick Start

### Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **Windows 10 or 11**

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/safeeyes-windows.git
cd safeeyes-windows

# Install dependencies
pip install -r safeeyes_windows/requirements.txt

# Run SafeEyes
python -m safeeyes_windows
```

### One-Liner

```bash
pip install pystray Pillow plyer && python -m safeeyes_windows
```

### Using Startup Scripts

For convenience, two startup scripts are provided in the repository:
- `start_safeeyes.bat` (Batch script)
- `start_safeeyes.ps1` (PowerShell script)

These scripts automatically install any missing dependencies and run the application silently in the background (using `pythonw`). Simply double-click the `.bat` file to start SafeEyes without keeping a console window open.

## Usage

### System Tray Menu

Right-click the eye icon in your taskbar to access:

| Menu Item | Action |
|-----------|--------|
| **Status** | Shows next break time |
| **Disable / Enable** | Toggle break reminders on/off |
| **Take a break now** | Trigger an immediate break |
| **Settings** | Open the settings dialog |
| **About** | Version and credits |
| **Quit** | Exit SafeEyes completely |

### During a Break

| Control | Action |
|---------|--------|
| `Escape` key | Skip this break |
| `Space` key | Postpone for 5 minutes |
| **Skip** button | Skip this break |
| **Postpone** button | Postpone for 5 minutes |

> Buttons and shortcuts are locked for the first 2 seconds to prevent accidental dismissal.

### Debug Mode

```bash
python -m safeeyes_windows --debug
```

Enables verbose logging to see scheduler timings, break events, and state transitions.

## Configuration

Settings are stored at `%APPDATA%\SafeEyes\safeeyes.json`. You can edit via the Settings dialog or manually:

```json
{
    "short_break_interval": 15,
    "long_break_interval": 75,
    "short_break_duration": 15,
    "long_break_duration": 60,
    "pre_break_warning_time": 10,
    "allow_postpone": true,
    "postpone_duration": 5,
    "strict_break": false,
    "random_order": true,
    "audible_alert": true
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `short_break_interval` | `15` | Minutes between short breaks |
| `long_break_interval` | `75` | Minutes between long breaks |
| `short_break_duration` | `15` | Seconds a short break lasts |
| `long_break_duration` | `60` | Seconds a long break lasts |
| `pre_break_warning_time` | `10` | Seconds of warning before a break |
| `allow_postpone` | `true` | Show the Postpone button |
| `postpone_duration` | `5` | Minutes to postpone |
| `strict_break` | `false` | Hide Skip button (enforced breaks) |
| `random_order` | `true` | Randomize break exercise messages |
| `audible_alert` | `true` | Play sounds on break start/end |

## Break Messages

### Short Breaks (15 seconds)
- Gently close your eyes
- Roll your eyes a few times to each side
- Rotate your eyes in clockwise direction
- Rotate your eyes in counterclockwise direction
- Blink your eyes
- Focus on a point in the far distance
- Have some water

### Long Breaks (60 seconds)
- Walk for a while
- Lean back at your seat and relax
- Stand up and stretch your body

## Architecture

```
safeeyes_windows/
├── __main__.py          # Entry point, single-instance mutex, DPI awareness
├── app.py               # Main orchestrator — wires all components together
├── core.py              # Break scheduler engine (threading.Timer based)
├── model.py             # Break, BreakQueue, State, Config data classes
├── break_screen.py      # Fullscreen tkinter overlay with countdown
├── tray.py              # System tray icon + menu (pystray)
├── notification.py      # Windows toast notifications (plyer)
├── audio.py             # WAV sound alerts (winsound)
├── settings_dialog.py   # Tkinter settings window
├── config.json          # Default configuration
├── requirements.txt     # Python dependencies
└── resources/
    ├── on_pre_break.wav # Pre-break alert sound
    └── on_stop_break.wav# Break-ended sound
```

### Tech Stack

| Component | Library | Why |
|-----------|---------|-----|
| **GUI / Break Screen** | `tkinter` | Ships with Python, no install needed |
| **System Tray** | `pystray` | Lightweight, uses native Win32 APIs |
| **Tray Icon** | `Pillow` | Programmatically generated eye icon |
| **Notifications** | `plyer` | Cross-platform Windows toast support |
| **Audio** | `winsound` | Built-in Python module for WAV playback |
| **Scheduling** | `threading.Timer` | Standard library, no external deps |

### How It Works

```
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│  System Tray │◄──►│   App.py    │◄──►│  Break Screen   │
│  (pystray)   │    │ Orchestrator│    │  (tkinter)      │
└─────────────┘    └──────┬──────┘    └─────────────────┘
                          │
                   ┌──────┴──────┐
                   │   Core.py   │
                   │  Scheduler  │
                   │  (Timer)    │
                   └──────┬──────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌─────────┐ ┌────────┐
        │Notify    │ │ Audio   │ │ Config │
        │(plyer)   │ │(winsound│ │ (JSON) │
        └──────────┘ └─────────┘ └────────┘
```

## Credits

This project is a Windows port of [**Safe Eyes**](https://github.com/slgobinath/SafeEyes) by [Gobinath Loganathan](https://github.com/slgobinath), originally built for Linux using GTK. The core scheduling logic, break messages, and audio resources are derived from the original project.

## License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Take care of your eyes. They're the only pair you've got.** 👁️

</div>
