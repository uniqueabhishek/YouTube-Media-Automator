"""
FFmpeg utilities - Uses static-ffmpeg package for guaranteed FFmpeg availability.
"""
import static_ffmpeg


def get_ffmpeg_path() -> str:
    """
    Returns a guaranteed usable FFmpeg path using static-ffmpeg package.
    This automatically downloads FFmpeg binaries on first use.
    """
    # static_ffmpeg.add_paths() adds ffmpeg to PATH and returns the paths
    ffmpeg_path, ffprobe_path = static_ffmpeg.run.get_or_fetch_platform_executables_else_raise()
    return ffmpeg_path
