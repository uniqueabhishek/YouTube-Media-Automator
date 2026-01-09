# YouTube Downloader - Setup Guide

## Virtual Environment Setup (Updated for uv ✓)

The project now uses **uv** for ultra-fast Python dependency management.

### What's Been Done:

1.  **Virtual Environment Created**: `venv/` folder (managed by `uv`)
2.  **Dependencies Installed**: All required packages are installed via `uv pip`
3.  **Requirements File**: `requirements.txt` created with all dependencies

### Installed Dependencies:

-   **yt-dlp** - Core YouTube download library
-   **PyQt5** - Professional GUI framework
-   **customtkinter** - Modern tkinter variant
-   **loguru** - Advanced logging
-   **pyperclip** - Clipboard management
-   **requests** - HTTP library

---

## How to Activate the Virtual Environment:

### Windows:
```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# Command Prompt
.\venv\Scripts\activate.bat

# Git Bash / MinGW
source venv/Scripts/activate
```

### Linux/Mac:
```bash
source venv/bin/activate
```

You'll know it's activated when you see `(venv)` at the start of your command prompt.

---

## Running the Application:

### Option 1: Hi Tech Version (Recommended - Modular, Production-Ready)
```bash
# Activate venv first
.\venv\Scripts\Activate.ps1

# Navigate to Hi Tech Versions folder
cd "Hi Tech Versions"

# Run the application (Note: File name may be updated in future commands)
python app.py
```

### Option 2: Best Standalone Versions
```bash
# Activate venv first
.\venv\Scripts\Activate.ps1

# Run Best CustomTkinter version
python Best-1.py

# OR run alternative version with pause/resume
python v9.py
```

---

## VS Code Setup:

If you're using VS Code, the Python interpreter has been configured in `.vscode/settings.json`:

1.  Open Command Palette (`Ctrl+Shift+P`)
2.  Type "Python: Select Interpreter"
3.  Choose the one that shows: `.\venv\Scripts\python.exe` (Recommended)

---

## Managing Dependencies with uv:

To install new packages, use `uv` instead of `pip` for speed:

```bash
uv pip install <package_name>
```

To update requirements file:

```bash
uv pip freeze > requirements.txt
```

---

## Troubleshooting:

### Virtual environment not activating?
-   Windows: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell
-   Make sure you're in the project root directory

### Import errors?
-   Ensure virtual environment is activated
-   Reinstall dependencies: `uv pip install -r requirements.txt`

### Application won't start?
-   Check Python version: `python --version` (should be 3.10+)
-   Verify all dependencies: `uv pip list`

---

## Project Structure:

```
ytd-all/
├── venv/                      # uv virtual environment (DO NOT commit to git)
├── venv_backup/               # Backup of old environment
├── requirements.txt           # Python dependencies
├── Hi Tech Versions/          # Production-ready modular application
│   └── app.py                 # Main application launcher
├── Best-1.py                  # Best CustomTkinter standalone version
├── v9.py                      # Alternative standalone version
└── ffmpeg-7.1.1-essentials_build/   # FFmpeg binaries
```
