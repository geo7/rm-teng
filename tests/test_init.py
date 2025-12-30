"""Tests for rm_teng package."""

import shutil
import subprocess
import sys
from unittest.mock import MagicMock

import pytest

from src.rm_teng import rm_teng


def test_rm_rf_happy_path(tmp_path, monkeypatch):
    """Test the happy path for rm -rf {{ dir }}.

    GIVEN: a directory to be deleted and a trash directory
    WHEN: rm-teng is called with -rf and the directory name
    THEN: the directory is moved to the trash directory with the correct structure
    """
    # Setup
    work_dir = tmp_path / "work"
    work_dir.mkdir()

    target_dir = work_dir / "todelete"
    target_dir.mkdir()
    (target_dir / "file.txt").write_text("content")

    trash_dir = tmp_path / "trash"

    # Set environment variable for the trash dir
    monkeypatch.setenv("RM_TENG_DELETION_DIR", str(trash_dir))

    monkeypatch.chdir(work_dir)
    monkeypatch.setattr(sys, "argv", ["rm-teng", "-rf", "todelete"])

    # Act
    exit_code = rm_teng()

    # Assert
    assert exit_code == 0
    assert not target_dir.exists()

    # Verify content in trash
    # Find the timestamp dir
    trash_items = list(trash_dir.glob("*"))
    assert len(trash_items) == 1
    timestamp_dir = trash_items[0]

    # Check if todelete is inside
    # Structure: timestamp_dir / (full path relative to anchor)
    relative_path = target_dir.relative_to(target_dir.anchor)
    moved_dir = timestamp_dir / relative_path

    assert moved_dir.exists()
    assert (moved_dir / "file.txt").read_text() == "content"


def test_double_check_disabled(monkeypatch):
    """Test that double check can be disabled via environment variable.

    GIVEN: double check is disabled via env var and no handlers exist for
           command.
    WHEN: rm-teng is called
    THEN: System rm is called, there's no user prompt for confirmation
    """
    monkeypatch.setenv("RM_TENG_DOUBLE_CHECK", "false")
    monkeypatch.setattr(sys, "argv", ["rm-teng", "somefile"])

    # Mock subprocess.run so we don't actually run rm
    mock_run = MagicMock()
    monkeypatch.setattr(subprocess, "run", mock_run)
    monkeypatch.setattr(shutil, "which", lambda x: "/bin/rm")

    rm_teng()

    assert mock_run.called
    assert len(mock_run.mock_calls) == 1
    call = mock_run.mock_calls[0].args[0]
    assert " ".join(call) == "/bin/rm somefile"


def test_invalid_trash_dir(monkeypatch):
    """Test that relative trash dir raises ValueError.

    GIVEN: an invalid (relative) trash directory path set via environment variable
    WHEN: rm-teng is called
    THEN: a ValueError is raised with a descriptive error message
    """
    monkeypatch.setenv("RM_TENG_DELETION_DIR", "relative/path")
    monkeypatch.setattr(sys, "argv", ["rm-teng", "-rf", "anything"])

    with pytest.raises(ValueError, match="should be an absolute path"):
        rm_teng()
