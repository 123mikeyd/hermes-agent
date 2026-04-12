"""Tests for hermes_cli.wsl_compat — WSL / Windows Terminal resilience."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from hermes_cli.wsl_compat import (
    adapt_terminal_description,
    buffer_response_text,
    ensure_utf8_env,
    get_last_response,
    is_windows_env,
    make_debounced_resize_handler,
    sanitize_paste_input,
    safe_open,
    _response_buffer,
)


class TestSanitizePasteInput(unittest.TestCase):
    """Fix 1: Bracketed paste marker sanitisation."""

    def test_clean_input_unchanged(self):
        self.assertEqual(sanitize_paste_input("hello world"), "hello world")

    def test_empty_string(self):
        self.assertEqual(sanitize_paste_input(""), "")

    def test_strips_start_marker(self):
        self.assertEqual(sanitize_paste_input("\x1b[200~hello"), "hello")

    def test_strips_end_marker(self):
        self.assertEqual(sanitize_paste_input("hello\x1b[201~"), "hello")

    def test_strips_both_markers(self):
        self.assertEqual(
            sanitize_paste_input("\x1b[200~pasted text\x1b[201~"),
            "pasted text",
        )

    def test_strips_partial_markers(self):
        self.assertEqual(sanitize_paste_input("\x1b[0~text\x1b[1~"), "text")

    def test_multiline_paste(self):
        inp = "\x1b[200~line1\nline2\nline3\x1b[201~"
        self.assertEqual(sanitize_paste_input(inp), "line1\nline2\nline3")

    def test_no_escape_fast_path(self):
        text = "a" * 10000
        self.assertIs(sanitize_paste_input(text), text)  # same object — fast path


class TestAdaptTerminalDescription(unittest.TestCase):
    """Fix 7: WSL-aware tool descriptions."""

    def test_non_wsl_unchanged(self):
        desc = "Execute shell commands on a Linux environment."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=False), \
             patch("hermes_cli.wsl_compat.is_windows_native", return_value=False):
            self.assertEqual(adapt_terminal_description(desc), desc)

    def test_wsl_replaces_linux_environment(self):
        desc = "Execute shell commands on a Linux environment. More text."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=True):
            result = adapt_terminal_description(desc)
            self.assertIn("WSL", result)
            self.assertIn("/mnt/c/", result)
            self.assertNotIn("Linux environment", result)

    def test_windows_native(self):
        desc = "Execute shell commands on a Linux environment."
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=False), \
             patch("hermes_cli.wsl_compat.is_windows_native", return_value=True):
            result = adapt_terminal_description(desc)
            self.assertIn("Windows", result)


class TestResponseBuffer(unittest.TestCase):
    """Fix 4: Response text preservation."""

    def setUp(self):
        _response_buffer.clear()

    def test_buffer_and_retrieve(self):
        buffer_response_text("hello")
        self.assertEqual(get_last_response(), "hello")

    def test_buffer_ordering(self):
        buffer_response_text("first")
        buffer_response_text("second")
        self.assertEqual(get_last_response(), "second")

    def test_buffer_limit(self):
        for i in range(10):
            buffer_response_text(f"msg{i}")
        self.assertEqual(len(_response_buffer), 5)
        self.assertEqual(get_last_response(), "msg9")

    def test_empty_buffer(self):
        self.assertIsNone(get_last_response())


class TestSafeOpen(unittest.TestCase):
    """Fix 6: UTF-8 encoding defaults."""

    def test_text_mode_gets_utf8(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("héllo wörld 🩺")
            path = f.name
        try:
            with safe_open(path, "r") as fh:
                self.assertEqual(fh.read(), "héllo wörld 🩺")
        finally:
            os.unlink(path)

    def test_binary_mode_no_encoding(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"bytes")
            path = f.name
        try:
            with safe_open(path, "rb") as fh:
                self.assertEqual(fh.read(), b"bytes")
        finally:
            os.unlink(path)

    def test_explicit_encoding_not_overridden(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("test")
            path = f.name
        try:
            with safe_open(path, "r", encoding="ascii") as fh:
                self.assertEqual(fh.read(), "test")
        finally:
            os.unlink(path)


class TestDebouncedResize(unittest.TestCase):
    """Fix 3: Resize debounce."""

    def test_non_wsl_returns_original(self):
        app = MagicMock()
        original = app._on_resize
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=False):
            result = make_debounced_resize_handler(app)
        self.assertIs(result, original)

    def test_wsl_returns_wrapper(self):
        app = MagicMock()
        original = app._on_resize
        with patch("hermes_cli.wsl_compat.is_wsl", return_value=True):
            result = make_debounced_resize_handler(app)
        self.assertIsNot(result, original)
        self.assertTrue(callable(result))


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
        self.assertTrue(ctrl_l_found, "Ctrl+L binding not found")


if __name__ == "__main__":
    unittest.main()
