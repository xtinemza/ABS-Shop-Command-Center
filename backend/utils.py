"""
Shared utilities for all Shop Command Center API routers.
"""
import io
import os
import sys
from contextlib import redirect_stdout
from typing import Callable, List, Tuple, Optional

# Project root — one level above this file (backend/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_ROOT = os.path.join(PROJECT_ROOT, "tools")
OUTPUT_ROOT = os.path.join(PROJECT_ROOT, "output")


def capture_output(func: Callable, *args, **kwargs) -> Tuple[str, Optional[str]]:
    """
    Call func(*args, **kwargs) and return (stdout_text, error_string).
    Returns captured stdout even when an exception occurs.
    SystemExit is swallowed (argparse calls sys.exit on success too).
    """
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            func(*args, **kwargs)
        return buf.getvalue(), None
    except SystemExit:
        return buf.getvalue(), None
    except Exception as exc:
        return buf.getvalue(), str(exc)


def read_output_files(module_folder: str) -> Tuple[List[str], dict]:
    """
    Scan output/<module_folder>/ and return:
      - list of absolute file paths
      - dict of { filename: content }
    """
    folder = os.path.join(OUTPUT_ROOT, module_folder)
    if not os.path.isdir(folder):
        return [], {}

    paths = []
    content_map = {}
    for fname in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            paths.append(fpath)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                    content_map[fname] = fh.read()
            except Exception:
                content_map[fname] = ""
    return paths, content_map


def ensure_tools_path(subfolder: str = "") -> None:
    """Add tools (and optionally a subfolder) to sys.path if not already there."""
    paths_to_add = [TOOLS_ROOT]
    if subfolder:
        paths_to_add.append(os.path.join(TOOLS_ROOT, subfolder))
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)
