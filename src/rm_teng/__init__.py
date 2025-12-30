"""rm-teng."""

from __future__ import annotations

import datetime as dt
import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar


def check_and_create_deletion_dir(*, deletion_dir: str | Path) -> Path:
    """Ensure that deletion dir is valid, and exists."""
    # If deletion dir is set different to the default it needs to be a full
    # If the path. The deletion dir also needs to exist.
    if not Path(deletion_dir).is_absolute():
        msg = f"""Deletion dir set as {deletion_dir}, should be an absolute path to a directory."""
        raise ValueError(msg)
    Path(deletion_dir).mkdir(exist_ok=True, parents=True)
    return Path(deletion_dir)


class HandlerBase(ABC):
    """Base class for handlers."""

    registry: ClassVar[list[type[HandlerBase]]] = []

    def __init_subclass__(cls, **kwargs) -> None:
        """Register subclass so we can iterate over them."""
        super().__init_subclass__(**kwargs)
        HandlerBase.registry.append(cls)

    def __init__(self) -> None:
        """Create dirs and vars."""
        default_trash_dir = os.getenv("RM_TENG_DELETION_DIR", Path.home() / ".rm_rf_files")
        self.trash_dir = check_and_create_deletion_dir(deletion_dir=default_trash_dir)
        self.run_time = dt.datetime.now().strftime("%Y%m%d%H%M%S")

    @abstractmethod
    def use(self, arg_values: list[str]) -> bool:
        """Whether to use this handler."""

    @abstractmethod
    def handle(self, arg_values: list[str]) -> bool:
        """Method to handle these args."""


class HandleRmRf(HandlerBase):
    """Handle rm -rf {{ dir }}.

    This is the _main_ way that I've messed up when using rm, a "classic" is
    the following:

    * on the wrong git branch
    * rm -rf .git for {{ reasons }}
    * realise all work has been lost

    I think it's only happened once or twice, but each time it has been
    annoying enough to bother writing this.

    Will allow trash to be deleted.
    """

    def use(self, arg_values: list[str]) -> bool:
        """Check whehter to use handler."""
        expected_number_of_args = 3

        if len(arg_values) != expected_number_of_args:
            # Only handling a single dir.
            return False

        if arg_values[1] != "-rf":
            return False

        if not (Path.cwd() / arg_values[-1]).is_dir():
            # Only interested in dirs for this.
            return False

        if self.trash_dir.name in Path.cwd().parts:  # noqa: SIM103
            # Enable deletion from trash.
            return False

        return True

    def handle(self, arg_values: list[str]) -> bool:
        """Handle case."""
        dir_path_from = Path.cwd() / arg_values[-1]
        dir_path_to_base = self.trash_dir / self.run_time
        dir_path_to_base.mkdir(exist_ok=False, parents=True)
        dir_path_to = dir_path_to_base / dir_path_from.relative_to(dir_path_from.anchor)
        shutil.move(dir_path_from, dir_path_to)
        return True


def double_check() -> bool:
    """Run when nothing was 'handled'.

    Just to determine whether we definitely want to go ahead with the operation.

    """
    return os.getenv("RM_TENG_DOUBLE_CHECK", "true").lower() in {"true", "1", "yes", "y"}


def user_confirmation() -> bool:
    """Prompt user for confirmation."""
    return input("OK? [y/N]: ").strip().lower() in {"y", "yes"}


def rm_teng() -> int:
    """Entry point."""
    handled = False
    for _cls in HandlerBase.registry:
        instance = _cls()
        if instance.use(sys.argv):
            handled = instance.handle(sys.argv)
            break

    if handled:
        return 0

    run_process = False

    if double_check():
        arg_string = " ".join(sys.argv[1:])[:100]
        print(f"Running: rm {arg_string}")
        run_process = user_confirmation()

    else:
        run_process = True

    if run_process:
        rm_bin = shutil.which("rm")
        if rm_bin is None:
            return 1

        result = subprocess.run([rm_bin, *sys.argv[1:]], check=False)  # noqa: S603
        return result.returncode

    return 0


def main() -> None:
    """Run rm-teng."""
    raise SystemExit(rm_teng())
