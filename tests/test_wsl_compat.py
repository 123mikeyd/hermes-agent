"""Tests for hermes_cli.wsl_compat — WSL / Windows Terminal resilience."""

import os
import tempfile
import unittest
from unittest.mock import patch

from hermes_cli.wsl_compat import (
    adapt_terminal_description,
    sanitize_paste_input,
    safe_open,
)


class TestSanitizePasteInput(unittest.TestCase):
    """Fix 1: Bracketed paste marker sanitisation."""

    def test_clean_input_unchanged(self):
        assert sanitize_paste_input("hello world") == "hello world"

    def test_empty_string(self):
        assert sanitize_paste_input("") == ""

    def test_strips_start_marker(self):
        assert sanitize_paste_input("\x1b[200~hello") == "hello"

    def test_strips_end_marker(self):
        assert sanitize_paste_input("hello\x1b[201~") == "hello"

    def test_strips_both_markers(self):
        assert sanitize_paste_input("\x1b[200~pasted text\x1b[201~") == "pasted text"

    def test_strips_partial_markers(self):
        assert sanitize_paste_input("\x1b[0~text\x1b[1~") == "text"

    def test_multiline_paste(self):
        inp = "\x1b[200~line1\nline2\nline3\x1b[201~"
        assert sanitize_paste_input(inp) == "line1\nline2\nline3"

    def test_no_escape_fast_path(self):
        text = "a" * 10000
        assert sanitize_paste_input(text) == text


class TestAdaptTerminalDescription(unittest.TestCase):
    """Fix 7: WSL-aware tool descriptions."""

    def test_non_wsl_unchanged(self):
        desc = "Execute shell commands on a Linux environment."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=False), \
             patch("hermes_cli.wsl_compat.is_windows_native", return_value=False):
            assert adapt_terminal_description(desc) == desc

    def test_wsl_replaces_linux_environment(self):
        desc = "Execute shell commands on a Linux environment. More text."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=True):
            result = adapt_terminal_description(desc)
            assert "WSL" in result
            assert "/mnt/c/" in result

    def test_windows_native(self):
        desc = "Execute shell commands on a Linux environment."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=False), \
             patch("hermes_cli.wsl_compat.is_windows_native", return_value=True):
            result = adapt_terminal_description(desc)
            assert "Windows" in result


class TestSafeOpen(unittest.TestCase):
    """Fix 6: UTF-8 encoding defaults."""

    def test_text_mode_gets_utf8(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                          delete=False, encoding="utf-8") as f:
            f.write("héllo wörld")
            path = f.name
        try:
            with safe_open(path, "r") as fh:
                assert fh.read() == "héllo wörld"
        finally:
            os.unlink(path)

    def test_binary_mode_no_encoding(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"bytes")
            path = f.name
        try:
            with safe_open(path, "rb") as fh:
                assert fh.read() == b"bytes"
        finally:
            os.unlink(path)


class TestRefreshKeybinding(unittest.TestCase):
    """Fix 5: Ctrl+L hard refresh."""

    def test_ctrl_l_registered(self):
        from prompt_toolkit.key_binding import KeyBindings
        from hermes_cli.wsl_compat import register_refresh_keybinding
        kb = KeyBindings()
        register_refresh_keybinding(kb)
        ctrl_l_found = any(
            hasattr(b, "keys") and any("c-l" in str(k) for k in b.keys)
            for b in kb.bindings
        )
        assert ctrl_l_found, "Ctrl+L binding not found"


if __name__ == "__main__":
    unittest.main()
