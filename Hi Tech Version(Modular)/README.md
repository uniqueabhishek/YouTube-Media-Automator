# YouTube Downloader - Hi Tech Version

Professional YouTube video downloader with advanced features built using PyQt5.

## Features

✨ **Advanced Functionality:**
- Download queue management
- SQLite database for download history
- System tray integration
- Automatic retry mechanism (up to 3 attempts)
- Format size preview before download
- Smart URL validation with clipboard support
- Multiple quality/format options
- Professional PyQt5 interface

## Quick Start

### Method 1: Using app.py (Recommended)

```bash
# From project root
cd "Hi Tech Versions"
python app.py
```

### Method 2: Using batch file

Double-click `run_hitech.bat` from the project root folder.

### Method 3: Direct execution (Legacy)

```bash
cd "Hi Tech Versions"
python main_window.py
```

## Requirements

All dependencies are managed via the virtual environment in the parent directory.

Required packages:
- PyQt5 >= 5.15.0
- yt-dlp >= 2024.0.0
- loguru >= 0.7.0
- requests >= 2.31.0

FFmpeg is automatically downloaded if not found.

## File Structure

```
Hi Tech Versions/
├── app.py                          # Main launcher (USE THIS)
├── main_window.py                  # Main application code
├── download_thread.py              # Threaded download manager
├── database_handler.py             # SQLite database operations
├── vSmart_Paste_url.py            # Smart URL validation widget
├── app_dir_creator.py             # Environment setup
├── ffmpeg_utils.py                # FFmpeg path resolution
├── ffmpeg_updater.py              # FFmpeg update utility
└── README.md                      # This file
```

## Usage

1. **Launch the application** using one of the methods above
2. **Paste a YouTube URL** in the input field
3. **Select quality/format** from the dropdown
4. **Click Download** to start
5. **Monitor progress** in the queue list
6. **View history** of all downloads in the database

## Features in Detail

### Queue Management
- Add multiple videos to download queue
- Pause, resume, or cancel downloads
- View real-time progress for each item

### Database History
- All downloads are tracked in SQLite database
- Located at: `Hi Tech Versions/My YT Downloads/downloads.db`
- Track status, file paths, and timestamps

### Smart URL Validation
- Automatically validates YouTube URLs
- Supports clipboard paste with Ctrl+V
- Shows error for invalid URLs

### Format Preview
- See available formats and their sizes before downloading
- Choose optimal quality for your needs
- Supports video, audio-only, and custom formats

### Retry Mechanism
- Automatically retries failed downloads up to 3 times
- Handles network errors gracefully
- Logs all errors for debugging

### System Tray
- Minimize application to system tray
- Continue downloads in background
- Quick access from tray icon

## Troubleshooting

### Application won't start?
- Make sure virtual environment is activated
- Check that all dependencies are installed: `pip list`
- Verify Python version: `python --version` (3.10+ required)

### Downloads failing?
- Check internet connection
- Verify YouTube URL is valid
- Check logs in `downloader.log`
- FFmpeg will be auto-downloaded if missing

### Import errors?
- Ensure you're in the virtual environment
- Reinstall dependencies: `pip install -r ../requirements.txt`

## Development

### Module Overview

- **app.py**: Clean launcher entry point
- **main_window.py**: Main GUI and business logic
- **download_thread.py**: QThread-based async downloads
- **database_handler.py**: SQLite CRUD operations
- **vSmart_Paste_url.py**: Custom QLineEdit with validation
- **app_dir_creator.py**: Cross-platform path management
- **ffmpeg_utils.py**: FFmpeg binary detection/download
- **ffmpeg_updater.py**: FFmpeg version management

## License

This is an educational project for learning PyQt5 and yt-dlp integration.

## Credits

Built using:
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download engine
- [FFmpeg](https://ffmpeg.org/) - Media processing
- [loguru](https://github.com/Delgan/loguru) - Advanced logging
