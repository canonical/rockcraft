# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2026 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Tests for the Java plugin helpers."""

import subprocess
from pathlib import Path

from rockcraft.plugins.java_common import create_usr_bin_java


def test_create_usr_bin_java_commands():
    """The generated commands skip the link when no java binary is found
    and replace a stale link instead of failing on a re-run."""
    assert create_usr_bin_java() == [
        (
            '# Find the "java" executable and make a link to it in '
            "$CRAFT_PART_INSTALL/usr/bin/java"
        ),
        "java_bin=$(find ${CRAFT_PART_INSTALL} -name java -type f -executable)",
        (
            "if [ -d ${CRAFT_PART_INSTALL}/usr/bin ] && "
            '[ -n "$java_bin" ] && '
            "[ ! -f ${CRAFT_PART_INSTALL}/usr/bin/java ]; then "
            "ln -sfn --relative $java_bin ${CRAFT_PART_INSTALL}/usr/bin/java; fi"
        ),
    ]


def _run_generated_commands(
    work_dir: Path, install_dir: Path
) -> subprocess.CompletedProcess:
    """Run the generated commands the way craft-parts runs build commands:
    a script with ``set -euo pipefail`` executed from the part build
    directory, where the script exit status decides the build outcome."""
    script = work_dir / "build.sh"
    script.write_text(
        "#!/bin/bash\nset -euo pipefail\n"
        f"CRAFT_PART_INSTALL={install_dir}\n" + "\n".join(create_usr_bin_java()) + "\n"
    )
    script.chmod(0o755)
    return subprocess.run(
        [str(script)],
        cwd=work_dir,
        capture_output=True,
        text=True,
        check=False,
    )


def _install_java(install_dir: Path, jdk: str) -> Path:
    """Place a fake java executable in the part install directory."""
    java_bin = install_dir / "usr" / "lib" / "jvm" / jdk / "bin" / "java"
    java_bin.parent.mkdir(parents=True, exist_ok=True)
    java_bin.write_text("#!/bin/sh\nexit 0\n")
    java_bin.chmod(0o755)
    return java_bin


def test_create_usr_bin_java_without_binary_is_idempotent(tmp_path):
    """With no java binary in the install dir (a plain maven/ant project),
    the step is a no-op and never creates a stray ./java link.

    Regression test for https://github.com/canonical/rockcraft/issues/1388:
    the unguarded ln degraded to a one-operand call that created ./java in
    the part build directory, so the next pack failed with
    "ln: failed to create symbolic link './java': Already exists".
    """
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    install_dir = tmp_path / "install"
    (install_dir / "usr" / "bin").mkdir(parents=True)

    for _ in range(2):
        result = _run_generated_commands(work_dir, install_dir)
        assert result.returncode == 0, result.stderr

    assert not (work_dir / "java").exists()
    assert not (install_dir / "usr" / "bin" / "java").exists()


def test_create_usr_bin_java_links_binary_and_replaces_stale_link(tmp_path):
    """With a java binary present, the link is created and a re-run replaces
    a dangling link instead of failing."""
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    install_dir = tmp_path / "install"
    (install_dir / "usr" / "bin").mkdir(parents=True)

    java_bin = _install_java(install_dir, "fake-jdk")
    link = install_dir / "usr" / "bin" / "java"

    for _ in range(2):
        result = _run_generated_commands(work_dir, install_dir)
        assert result.returncode == 0, result.stderr

    assert link.is_symlink()
    assert link.resolve() == java_bin

    # The java binary is replaced on a rebuild: the old link dangles and
    # the next run must replace it, not fail with "File exists".
    java_bin.unlink()
    new_java_bin = _install_java(install_dir, "fake-jdk-2")

    result = _run_generated_commands(work_dir, install_dir)
    assert result.returncode == 0, result.stderr
    assert link.is_symlink()
    assert link.resolve() == new_java_bin
