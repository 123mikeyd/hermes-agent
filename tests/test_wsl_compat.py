"""Tests for hermes_cli.wsl_compat — WSL / Windows Terminal resilience."""

import re
import unittest
from unittest.mock import MagicMock, patch

from hermes_cli.wsl_compat import (
    adapt_terminal_description,
    sanitize_paste_input,
    safe_open,
    is_wsl,
    is_windows_native,
    is_windows_env,
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
        # ConPTY can fragment these — catch any digit-tilde pattern
        assert sanitize_paste_input("\x1b[0~text\x1b[1~") == "text"

    def test_multiline_paste(self):
        inp = "\x1b[200~line1\nline2\nline3\x1b[201~"
        assert sanitize_paste_input(inp) == "line1\nline2\nline3"

    def test_no_escape_chars_fast_path(self):
        """Input without ESC should take the fast path and return unchanged."""
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
        desc = "Execute shell commands on a Linux environment. Some other text."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=True):
            result = adapt_terminal_description(desc)
            assert "WSL" in result
            assert "/mnt/c/" in result
            assert "Linux environment" not in result

    def test_wsl_replaces_cloud_sandbox(self):
        desc = ("cloud sandboxes may be cleaned up, idled out, or recreated "
                "between turns. Persistent filesystem means files can resume "
                "later; it does NOT guarantee a continuously running machine "
                "or surviving background processes. Use terminal sandboxes "
                "for task work, not durable hosting.")
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=True):
            result = adapt_terminal_description(desc)
            assert "local WSL environment" in result
            assert "cloud sandbox" not in result

    def test_windows_native(self):
        desc = "Execute shell commands on a Linux environment."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=False), \
             patch("hermes_cli.wsl_compat.is_windows_native", return_value=True):
            result = adapt_terminal_description(desc)
            assert "Windows" in result


class TestSafeOpen(unittest.TestCase):
    """Fix 6: UTF-8 encoding defaults."""

    def test_text_mode_gets_utf8(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                          delete=False, encoding="utf-8") as f:
            f.write("héllo wörld 🩺")
            path = f.name
        try:
            with safe_open(path, "r") as f:
                content = f.read()
            assert content == "héllo wörld 🩺"
        finally:
            os.unlink(path)

    def test_binary_mode_no_encoding(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"bytes")
            path = f.name
        try:
            with safe_open(path, "rb") as f:
                assert f.read() == b"bytes"
        finally:
            os.unlink(path)

    def test_explicit_encoding_not_overridden(self):
        """If caller passes encoding explicitly, we don't override it."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                          delete=False, encoding="utf-8") as f:
            f.write("test")
            path = f.name
        try:
            with safe_open(path, "r", encoding="ascii") as f:
                content = f.read()
            assert content == "test"
        finally:
            os.unlink(path)


class TestRefreshKeybinding(unittest.TestCase):
    """Fix 5: Ctrl+L hard refresh."""

    def test_ctrl_l_registered(self):
        from prompt_toolkit.key_binding import KeyBindings
        kb = KeyBindings()
        from hermes_cli.wsl_compat import register_refresh_keybinding
        register_refresh_keybinding(kb)
        # Check that a binding for Ctrl+L exists
        bindings = kb.bindings
        ctrl_l_found = any(
            hasattr(b, "keys") and any("c-l" in str(k) for k in b.keys)
            for b in bindings
        )
        assert ctrl_l_found, "Ctrl+L binding not found"


if __name__ == "__main__":
    unittest.main()
