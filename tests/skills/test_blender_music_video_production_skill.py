"""Invariant tests for the Blender music-video production skill."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = (
    REPO
    / "optional-skills"
    / "creative"
    / "blender-music-video-production"
)
SKILL_MD = SKILL_DIR / "SKILL.md"


@pytest.fixture(scope="module")
def skill_text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def test_frontmatter_and_description_contract(skill_text: str):
    assert skill_text.startswith("---\n")
    description = re.search(r"^description: (.+)$", skill_text, re.MULTILINE)
    assert description
    value = description.group(1).strip().strip('"')
    assert len(value) <= 60
    assert value.endswith(".")
    assert "author: Mike (123mikeyd), Hermes Agent" in skill_text
    assert "license: MIT" in skill_text
    assert "platforms: [linux, macos, windows]" in skill_text


def test_modern_sections_are_present_and_ordered(skill_text: str):
    headings = [
        "## When to Use",
        "## Prerequisites",
        "## How to Run",
        "## Quick Reference",
        "## Procedure",
        "## Pitfalls",
        "## Verification",
    ]
    positions = [skill_text.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_source_protection_and_recoverable_rendering_are_hard_gates(skill_text: str):
    assert "Save Copy" in skill_text
    assert "matching Blender autosave" in skill_text
    assert "numbered PNG sequence" in skill_text
    assert "Direct-to-MP4 rendering" in skill_text
    assert "FFprobe" in skill_text
    assert "black-frame and long-freeze detection" in skill_text


def test_timeline_wide_extension_and_ensemble_rules_are_explicit(skill_text: str):
    assert "update every time-dependent layer" in skill_text
    assert "camera object, camera data/lens" in skill_text
    assert "123 intervals" in skill_text
    assert "exactly one render-visible instance" in skill_text
    assert "evaluated render-mesh bounds" in skill_text


def test_attribution_is_present_without_bundling_assets(skill_text: str):
    assert "created with Meshy" in skill_text
    assert "animation clips obtained from Mixamo" in skill_text
    assert "No third-party assets are" in skill_text
    assert "not bundled with this skill" in skill_text


def test_all_linked_support_files_exist(skill_text: str):
    linked = set(
        re.findall(r"`((?:references|scripts)/[^`]+)`", skill_text)
    )
    assert linked
    missing = [path for path in linked if not (SKILL_DIR / path).is_file()]
    assert not missing


def test_references_do_not_leak_machine_or_project_specific_names():
    forbidden = re.compile(
        r"C:\\Users|OneDrive|NRCU|Basilisk|I Sneeze|Dogeman|Gumy|"
        r"Nous Girl|Teknium",
        re.IGNORECASE,
    )
    for path in (SKILL_DIR / "references").glob("*.md"):
        assert not forbidden.search(path.read_text(encoding="utf-8")), path


def test_python_helpers_compile_without_importing_blender():
    scripts = list((SKILL_DIR / "scripts").glob("*.py"))
    assert scripts
    for path in scripts:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
