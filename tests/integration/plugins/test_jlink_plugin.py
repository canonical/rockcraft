# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import atexit
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from craft_application.models import DEVEL_BASE_INFOS
from rockcraft import plugins
from rockcraft.models.project import Project

from tests.testing.project import create_project
from tests.util import ubuntu_only

pytestmark = ubuntu_only


@pytest.fixture(autouse=True)
def setup_test(monkeypatch):
    # Keep craft-parts from trying to refresh apt's cache, so that we can run
    # this test as regular users.
    monkeypatch.setenv("CRAFT_PARTS_PACKAGE_REFRESH", "0")
    plugins.register()


def create_test_project(base, parts) -> Project:
    build_base = None
    if base in [info.current_devel_base for info in DEVEL_BASE_INFOS]:
        build_base = "devel"

    return create_project(base=base, parts=parts, build_base=build_base)


def get_tmp_path(tmp_path: str) -> Path:
    # chisel snap is confined to user home
    home = os.path.expanduser("~")
    basename = os.path.basename(tmp_path)
    ret = Path(f"{home}/{basename}")
    atexit.register(lambda: shutil.rmtree(ret))
    return ret


def test_jlink_plugin_with_jar(tmp_path, run_lifecycle):
    """Test that jlink produces tailored modules"""
    user_home_tmp = get_tmp_path(tmp_path)
    parts = {
        "my-part": {
            "plugin": "jlink",
            "source": "https://github.com/vpa1977/chisel-releases",
            "source-type": "git",
            "source-branch": "24.04-openjdk-21-jre-headless",
            "jlink-jars": ["test.jar"],
            "after": ["stage-jar"],
        },
        "stage-jar": {
            "plugin": "dump",
            "source": ".",
        },
    }
    # build test jar
    Path(f"Test.java").write_text(
        """
            import javax.swing.*;
            public class Test {
                public static void main(String[] args) {
                    new JFrame("foo").setVisible(true);
                }
            }
        """
    )
    subprocess.run(["javac", "Test.java"], check=True, capture_output=True)
    subprocess.run(
        ["jar", "cvf", "test.jar", "Test.class"], check=True, capture_output=True
    )
    atexit.register(lambda: os.remove("Test.class"))
    atexit.register(lambda: os.remove("Test.java"))
    atexit.register(lambda: os.remove("test.jar"))

    project = create_test_project("ubuntu@24.04", parts)
    run_lifecycle(project=project, work_dir=user_home_tmp)
    # java.desktop module should be included in the image
    assert len(list(Path(f"{user_home_tmp}/stage/usr/lib/jvm/").rglob("libawt.so"))) > 0


def test_jlink_plugin_base(tmp_path, run_lifecycle):
    """Test that jlink produces base image"""
    parts = {
        "my-part": {
            "plugin": "jlink",
            "source": "https://github.com/vpa1977/chisel-releases",
            "source-type": "git",
            "source-branch": "24.04-openjdk-21-jre-headless",
        }
    }
    user_home_tmp = get_tmp_path(tmp_path)
    project = create_test_project("ubuntu@24.04", parts)
    run_lifecycle(project=project, work_dir=user_home_tmp)
    java = user_home_tmp / "stage/usr/bin/java"
    assert java.is_file()
