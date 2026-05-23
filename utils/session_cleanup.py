from pathlib import Path

from generation.engine import cleanup_session_file, cleanup_stale_temp_dirs


def cleanup_zip_path(path_str: str | None) -> None:
    if not path_str:
        return
    cleanup_session_file(Path(path_str))


def cleanup_old_files() -> int:
    return cleanup_stale_temp_dirs(max_age_seconds=3600)
