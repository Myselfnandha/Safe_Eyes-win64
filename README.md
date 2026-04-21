<div align="center">

# SafeEyes for Windows

**Protect your eyes from digital eye strain with smart break reminders.**

A Windows-native system tray application that reminds you to take regular breaks — built as a full port of the popular Linux [Safe Eyes](https://github.com/slgobinath/SafeEyes) app.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](LICENSE)

</div>

---

## Why SafeEyes?

Staring at screens for long periods causes **digital eye strain** — dry eyes, headaches, blurred vision, and neck pain. The **20-20-20 rule** recommends looking at something 20 feet away for 20 seconds every 20 minutes.

SafeEyes automates this with configurable break intervals and a fullscreen overlay that gently reminds you to rest.

---

## Features

| Feature | Description |
|---------|-------------|
| **Smart Break Scheduling** | Short breaks every 15 min, long breaks every 75 min (fully configurable) |
| **Fullscreen Break Overlay** | Dark-themed overlay with countdown timer covers your screen during breaks |
| **System Tray Integration** | Lives quietly in your Windows taskbar notification area |
| **Skip & Postpone** | Skip a break entirely or postpone it for later |
| **Keyboard Shortcuts** | `Escape` to skip, `Space` to postpone during a break |
| **Audible Alerts** | Sound notification before and after each break |
| **Toast Notifications** | Windows 10/11 native notification before each break |
| **Settings Dialog** | Configure intervals, durations, and behavior from a dark-themed UI |
| **Randomized Breaks** | Eye exercises shown in random order to keep things fresh |
| **Single Instance** | Windows mutex ensures only one instance runs at a time |
| **Persistent Config** | Settings saved to `%APPDATA%\SafeEyes\safeeyes.json` |

---

## Quick Start

### Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **Windows 10 or 11**

### Option 1: Double-Click Launch

Two startup scripts are included in the repository. Simply double-click one:

| Script | Description |
|--------|-------------|
| `start_safeeyes.bat` | Batch script — installs deps and launches silently |
| `start_safeeyes.ps1` | PowerShell script — same behavior for PS users |

Both scripts auto-install dependencies and run the app in the background using `pythonw` (no console window).

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/Myselfnandha/Safe_Eyes-win64.git
cd Safe_Eyes-win64

# Install dependencies
pip install -r safeeyes_windows/requirements.txt

# Run SafeEyes
python -m safeeyes_windows
```

### Option 3: One-Liner

```bash
pip install pystray Pillow plyer && python -m safeeyes_windows
```

---

## Usage

### System Tray

Right-click the eye icon in your taskbar:

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

Enables verbose logging for scheduler timings, break events, and state transitions.

---

## Configuration

Settings are stored at `%APPDATA%\SafeEyes\safeeyes.json` and can be edited via the Settings dialog or manually:

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

---

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

---

## Architecture

```
safeeyes_windows/
├── __main__.py          # Entry point — mutex, DPI awareness, bootstrap
├── app.py               # Orchestrator — wires all components together
├── core.py              # Break scheduler (threading.Timer based)
├── model.py             # Break, BreakQueue, State, Config dataclasses
├── break_screen.py      # Fullscreen tkinter overlay with countdown
├── tray.py              # System tray icon + context menu (pystray)
├── notification.py      # Windows toast notifications (plyer)
├── audio.py             # WAV sound alerts (winsound)
├── settings_dialog.py   # Tkinter settings window (dark theme)
├── config.json          # Default configuration
├── requirements.txt     # Python dependencies
├── start_safeeyes.bat   # Batch launcher script
├── start_safeeyes.ps1   # PowerShell launcher script
└── resources/
    ├── on_pre_break.wav  # Pre-break alert sound
    └── on_stop_break.wav # Break-ended sound
```

### Tech Stack

| Component | Library | Rationale |
|-----------|---------|-----------|
| **GUI / Break Screen** | `tkinter` | Ships with Python — zero install |
| **System Tray** | `pystray` | Lightweight, native Win32 APIs |
| **Tray Icon** | `Pillow` | Programmatic eye icon generation |
| **Notifications** | `plyer` | Cross-platform Windows toast support |
| **Audio** | `winsound` | Built-in Python module for WAV |
| **Scheduling** | `threading.Timer` | Standard library, no deps |

### Component Flow

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
        │ Notify   │ │  Audio  │ │ Config │
        │ (plyer)  │ │(winsound)│ │ (JSON) │
        └──────────┘ └─────────┘ └────────┘
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pystray` | >= 0.19 | System tray icon and menu |
| `Pillow` | >= 10.0 | Icon image generation |
| `plyer` | >= 2.1 | Windows toast notifications |

All other modules (`tkinter`, `winsound`, `threading`, `json`) are part of the Python standard library.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| **1.0.2** | 2026-04-21 | Fix settings dialog crash, lint and type fixes |
| **1.0.1** | 2026-04-21 | Add startup scripts (`bat` / `ps1`) |
| **1.0.0** | 2026-04-21 | Initial release — full Windows port |

---

## Credits

This project is a Windows port of [**Safe Eyes**](https://github.com/slgobinath/SafeEyes) by [Gobinath Loganathan](https://github.com/slgobinath), originally built for Linux using GTK. The core scheduling logic, break messages, and audio resources are derived from the original project.

## License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Take care of your eyes. They're the only pair you've got.**

</div>
