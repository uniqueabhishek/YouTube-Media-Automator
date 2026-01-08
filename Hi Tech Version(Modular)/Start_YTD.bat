@echo off
title YouTube Downloader - Hi Tech Version
cd /d "%~dp0"
set UV_LINK_MODE=copy
echo Starting YouTube Downloader...
uv run python app.py
pause
