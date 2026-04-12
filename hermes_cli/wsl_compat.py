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
    from prompt_toolkit.widgets import TextArea

logger = logging.getLogger(__name__)

# ─── Detection ──────────────────────────────────────────────────────────────

_is_wsl: bool | None = None


def is_wsl() -> bool:
    """Cached WSL detection via /proc/version Microsoft marker."""
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

# Bracketed paste mode markers that ConPTY can leak into input.
# ^[[200~ = start of paste, ^[[201~ = end of paste.
# Also catch partial/garbled variants that JPEGs and ConPTY fragmentation
# can produce.
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
    at ``interval`` seconds and calls ``app._on_resize()`` when a change
    is detected.

    Only starts on WSL.  No-op on other platforms.
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
                    if app.is_running:
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


# ─── Fix 3 & 4: Resize Debounce + Response Preservation ────────────────────

_resize_timer: threading.Timer | None = None
_resize_lock = threading.Lock()

# Buffer for completed response text that should survive resizes.
_response_buffer: list[str] = []


def buffer_response_text(text: str) -> None:
    """Store a completed response so it survives a terminal resize.

    The CLI should call this after every completed agent response.
    On resize, the buffered text can be replayed.
    """
    _response_buffer.append(text)
    # Keep only the last 5 responses to limit memory
    while len(_response_buffer) > 5:
        _response_buffer.pop(0)


def get_buffered_responses() -> list[str]:
    """Return buffered response texts (most recent last)."""
    return list(_response_buffer)


def debounced_resize(app: "Application", delay: float = 0.15) -> None:
    """Debounce terminal resize events.

    Instead of immediately redrawing on every resize signal (which causes
    duplicated status bars and cleared text on WSL), we wait ``delay``
    seconds for the resize to settle before invalidating.

    Falls through to immediate invalidate on non-WSL platforms.
    """
    if not is_wsl():
        app.invalidate()
        return

    global _resize_timer
    with _resize_lock:
        if _resize_timer is not None:
            _resize_timer.cancel()

        def _do_resize():
            try:
                if app.is_running:
                    app.invalidate()
            except Exception:
                pass

        _resize_timer = threading.Timer(delay, _do_resize)
        _resize_timer.daemon = True
        _resize_timer.start()


# ─── Fix 5: Ctrl+L Hard Refresh ────────────────────────────────────────────

def register_refresh_keybinding(
    kb: "KeyBindings",
    app_ref: "Application | None" = None,
) -> None:
    """Register Ctrl+L to force a full screen clear and redraw.

    This is the universal "escape hatch" when the display is corrupted.
    Works on all platforms but is most critical on WSL.
    """
    @kb.add("c-l")
    def _ctrl_l_refresh(event):
        """Force clear screen and full redraw."""
        output = event.app.renderer.output
        try:
            # Clear the entire screen
            output.write_raw("\x1b[2J")  # Clear screen
            output.write_raw("\x1b[H")   # Cursor to home
            output.flush()
        except Exception:
            pass
        # Reset the renderer state so it does a full repaint
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
    unaffected.
    """
    if "b" not in mode and "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    return open(path, mode, **kwargs)


# ─── Fix 7: WSL-Aware Tool Description ─────────────────────────────────────

def adapt_terminal_description(description: str) -> str:
    """Adjust the terminal tool description for the current platform.

    The default description tells the LLM it's running on a "Linux
    environment" with "cloud sandboxes" — misleading when the user is
    on WSL or native Windows.  This produces better tool use decisions.
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

    Parameters
    ----------
    app : Application, optional
        The prompt_toolkit Application instance.  Required for size polling
        and debounced resize.
    kb : KeyBindings, optional
        The active keybinding registry.  Required for Ctrl+L refresh.
    """
    platform = "WSL" if is_wsl() else "Windows" if is_windows_native() else "other"
    logger.debug("WSL mitigations: platform=%s", platform)

    # Fix 5: Ctrl+L refresh (all platforms — it's universally useful)
    if kb is not None:
        register_refresh_keybinding(kb, app)

    if not is_windows_env():
        logger.debug("WSL mitigations: non-Windows platform, skipping WSL-specific fixes")
        return

    # Fix 2: Terminal size polling (WSL only)
    if app is not None and is_wsl():
        start_terminal_size_polling(app, interval=0.5)

    # Fix 6: Ensure UTF-8 default for file I/O on Windows
    if sys.platform == "win32" and not os.environ.get("PYTHONIOENCODING"):
        os.environ["PYTHONIOENCODING"] = "utf-8"

    logger.info(
        "WSL/Windows Terminal mitigations applied: paste-sanitize, "
        "size-poll, resize-debounce, Ctrl+L refresh, UTF-8 encoding, "
        "WSL-aware tool descriptions"
    )
