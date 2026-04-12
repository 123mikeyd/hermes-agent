"""WSL / Windows Terminal compatibility hardening.

Provides a single ``apply_wsl_mitigations()`` entry-point that the CLI
calls once at startup.  All fixes are **no-ops on non-WSL platforms** so
there is zero risk to Mac/Linux users.

Addresses:
    1. Bracketed paste marker leak  (^[[200~ / ^[[201~ freeze)
    2. Terminal size polling         (missed SIGWINCH on ConPTY)
    3. Resize debounce              (ghost status bars, cleared text)
    4. Response text preservation    (buffer survives resize)
    5. Ctrl+L hard refresh          (escape hatch for corrupted display)
    6. Safe encoding defaults       (UTF-8 for all file I/O on Windows)
    7. WSL-aware tool descriptions  (don't tell the LLM it's a cloud sandbox)
"""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings

logger = logging.getLogger(__name__)

# ─── Detection ──────────────────────────────────────────────────────────────
# Re-use hermes_constants.is_wsl() if available (upstream has it);
# fall back to our own implementation for older codebases.

try:
    from hermes_constants import is_wsl as _upstream_is_wsl
except ImportError:
    _upstream_is_wsl = None

_is_wsl: bool | None = None


def is_wsl() -> bool:
    """Cached WSL detection via /proc/version Microsoft marker."""
    if _upstream_is_wsl is not None:
        return _upstream_is_wsl()
    global _is_wsl
    if _is_wsl is not None:
        return _is_wsl
    try:
        with open("/proc/version", "r") as f:
            _is_wsl = "microsoft" in f.read().lower()
    except Exception:
        _is_wsl = False
    return _is_wsl


def is_windows_native() -> bool:
    """True when running on native Windows (not WSL)."""
    return sys.platform == "win32"


def is_windows_env() -> bool:
    """True on either native Windows or WSL."""
    return is_windows_native() or is_wsl()


# ─── Fix 1: Bracketed Paste Sanitisation ────────────────────────────────────

_PASTE_MARKER_RE = re.compile(r"\x1b\[\d*~")


def sanitize_paste_input(text: str) -> str:
    """Strip leaked bracketed-paste escape sequences from user input.

    Windows Terminal's ConPTY bridge can fragment the paste terminator
    across multiple reads, leaving raw ``^[[200~`` / ``^[[201~`` markers
    in the input buffer.  This causes prompt_toolkit to freeze or to
    save corrupted text.

    Safe to call on all platforms — returns input unchanged if no markers
    are present.
    """
    if "\x1b" not in text:
        return text
    return _PASTE_MARKER_RE.sub("", text)


# ─── Fix 2: Terminal Size Polling ───────────────────────────────────────────

_size_poll_thread: threading.Thread | None = None
_size_poll_stop = threading.Event()


def start_terminal_size_polling(
    app: "Application",
    interval: float = 0.5,
) -> None:
    """Poll terminal dimensions as a fallback for missed SIGWINCH.

    WSL's ConPTY layer sometimes drops the SIGWINCH signal when the
    terminal window is resized.  This thread polls ``shutil.get_terminal_size()``
    at *interval* seconds and triggers the app's resize handler when a
    change is detected.

    Only activates on WSL.  No-op on other platforms.
    """
    if not is_wsl():
        return

    import shutil

    global _size_poll_thread, _size_poll_stop
    _size_poll_stop.clear()

    last_cols, last_rows = shutil.get_terminal_size()

    def _poll():
        nonlocal last_cols, last_rows
        while not _size_poll_stop.is_set():
            _size_poll_stop.wait(interval)
            if _size_poll_stop.is_set():
                break
            try:
                cols, rows = shutil.get_terminal_size()
                if cols != last_cols or rows != last_rows:
                    last_cols, last_rows = cols, rows
                    # Trigger the app's own resize path (not just invalidate)
                    # so prompt_toolkit recalculates layout dimensions.
                    if app.is_running:
                        try:
                            app._on_resize()
                        except Exception:
                            app.invalidate()
            except Exception:
                pass

    _size_poll_thread = threading.Thread(
        target=_poll,
        daemon=True,
        name="wsl-size-poll",
    )
    _size_poll_thread.start()
    logger.debug("WSL terminal size polling started (interval=%.1fs)", interval)


def stop_terminal_size_polling() -> None:
    """Signal the polling thread to stop (called on app exit)."""
    _size_poll_stop.set()


# ─── Fix 3: Resize Debounce ────────────────────────────────────────────────

_resize_timer: threading.Timer | None = None
_resize_lock = threading.Lock()


def make_debounced_resize_handler(app: "Application", delay: float = 0.15):
    """Wrap the app's ``_on_resize`` with a debounce timer.

    Instead of immediately redrawing on every resize signal (which causes
    duplicated status bars and cleared text on WSL), we cancel the previous
    pending redraw and wait *delay* seconds for the resize to settle.

    Returns the wrapper function that should replace ``app._on_resize``.
    Falls through to immediate call on non-WSL platforms.
    """
    original_on_resize = app._on_resize

    if not is_wsl():
        return original_on_resize  # no wrapping needed

    def _debounced():
        global _resize_timer
        with _resize_lock:
            if _resize_timer is not None:
                _resize_timer.cancel()

            def _do_resize():
                try:
                    original_on_resize()
                except Exception:
                    pass

            _resize_timer = threading.Timer(delay, _do_resize)
            _resize_timer.daemon = True
            _resize_timer.start()

    return _debounced


# ─── Fix 4: Response Text Preservation ──────────────────────────────────────

_response_buffer: list[str] = []
_buffer_lock = threading.Lock()


def buffer_response_text(text: str) -> None:
    """Store a completed response so it can be recovered after resize.

    The CLI should call this after every completed agent response.
    """
    with _buffer_lock:
        _response_buffer.append(text)
        # Keep only the last 5 responses to limit memory
        while len(_response_buffer) > 5:
            _response_buffer.pop(0)


def get_last_response() -> str | None:
    """Return the most recent buffered response, or None."""
    with _buffer_lock:
        return _response_buffer[-1] if _response_buffer else None


# ─── Fix 5: Ctrl+L Hard Refresh ────────────────────────────────────────────

def register_refresh_keybinding(kb: "KeyBindings") -> None:
    """Register Ctrl+L to force a full screen clear and redraw.

    This is the universal escape hatch when the display is corrupted.
    Works on all platforms but is most critical on WSL.
    """
    @kb.add("c-l")
    def _ctrl_l_refresh(event):
        """Force clear screen and full redraw."""
        output = event.app.renderer.output
        try:
            output.write_raw("\x1b[2J")   # Clear entire screen
            output.write_raw("\x1b[H")    # Cursor to home position
            output.flush()
        except Exception:
            pass
        try:
            event.app.renderer.reset()
        except Exception:
            pass
        event.app.invalidate()


# ─── Fix 6: Safe Encoding Defaults ─────────────────────────────────────────

def safe_open(path, mode="r", **kwargs):
    """Open a file with explicit UTF-8 encoding on Windows/WSL.

    On Windows, ``open()`` defaults to the system locale (cp1252, GBK, etc.)
    which causes ``UnicodeDecodeError`` for config files containing UTF-8
    characters (emoji, non-Latin text).

    This wrapper ensures UTF-8 for text mode opens.  Binary mode is
    unaffected.  If the caller already specifies an encoding, it is not
    overridden.
    """
    if "b" not in mode and "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    return open(path, mode, **kwargs)


def ensure_utf8_env() -> None:
    """Set PYTHONIOENCODING=utf-8 if not already set.

    Only meaningful on native Windows where the default encoding may be
    a legacy codepage.  On WSL the system is already UTF-8.
    """
    if is_windows_native() and not os.environ.get("PYTHONIOENCODING"):
        os.environ["PYTHONIOENCODING"] = "utf-8"


# ─── Fix 7: WSL-Aware Tool Description ─────────────────────────────────────

def adapt_terminal_description(description: str) -> str:
    """Adjust the terminal tool description for the current platform.

    The default description tells the LLM it's running on a "Linux
    environment" with "cloud sandboxes" — misleading when the user is
    on WSL or native Windows.
    """
    if is_wsl():
        description = description.replace(
            "Execute shell commands on a Linux environment.",
            "Execute shell commands in WSL (Windows Subsystem for Linux). "
            "You are running inside WSL on a Windows machine — /mnt/c/ "
            "accesses the Windows filesystem.",
        )
        description = description.replace(
            "cloud sandboxes may be cleaned up, idled out, or recreated between turns. "
            "Persistent filesystem means files can resume later; it does NOT guarantee "
            "a continuously running machine or surviving background processes. "
            "Use terminal sandboxes for task work, not durable hosting.",
            "This is a local WSL environment — files persist normally. "
            "The Windows filesystem is accessible at /mnt/c/, /mnt/d/, etc.",
        )
    elif is_windows_native():
        description = description.replace(
            "Execute shell commands on a Linux environment.",
            "Execute shell commands on Windows.",
        )
    return description


# ─── Unified Entry Point ───────────────────────────────────────────────────

def apply_wsl_mitigations(
    *,
    app: "Application | None" = None,
    kb: "KeyBindings | None" = None,
) -> None:
    """Apply all WSL/Windows Terminal mitigations.

    Call once at CLI startup after the prompt_toolkit Application is created.
    """
    platform = "WSL" if is_wsl() else "Windows" if is_windows_native() else "other"
    logger.debug("WSL mitigations: platform=%s", platform)

    # Fix 5: Ctrl+L refresh — all platforms, universally useful
    if kb is not None:
        register_refresh_keybinding(kb)

    if not is_windows_env():
        logger.debug("Non-Windows platform, skipping WSL-specific fixes")
        return

    # Fix 2: Terminal size polling (WSL only)
    if app is not None and is_wsl():
        start_terminal_size_polling(app, interval=0.5)

    # Fix 3: Debounced resize (WSL only) — wrap the app's resize handler
    if app is not None and is_wsl():
        app._on_resize = make_debounced_resize_handler(app, delay=0.15)

    # Fix 6: UTF-8 encoding for native Windows
    ensure_utf8_env()

    logger.info(
        "WSL/Windows Terminal mitigations active (%s): paste-sanitize, "
        "size-poll, resize-debounce, Ctrl+L, UTF-8, WSL-aware descriptions",
        platform,
    )
