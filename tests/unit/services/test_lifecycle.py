# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2023 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import shutil
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from craft_application import services, util
from craft_application.util import repositories
from craft_parts import (
    LifecycleManager,
    Part,
    PartInfo,
    ProjectDirs,
    ProjectInfo,
    ProjectVar,
    ProjectVarInfo,
    Step,
    StepInfo,
    callbacks,
)
from craft_parts.state_manager.prime_state import PrimeState
from rockcraft.plugins.python_common import get_python_plugins
from rockcraft.services import lifecycle as lifecycle_module


@pytest.fixture
def extra_project_params():
    return {"package_repositories": [{"type": "apt", "ppa": "ppa/ppa"}]}


@pytest.mark.usefixtures("configured_project")
def test_lifecycle_args(
    default_image_info, mocker, monkeypatch, fake_services, project_path
):
    monkeypatch.setenv("CRAFT_PARALLEL_BUILD_COUNT", "4")

    mock_obtain_image = mocker.patch.object(
        fake_services.get("image"), "obtain_image", return_value=default_image_info
    )
    mock_lifecycle = mocker.patch.object(
        LifecycleManager, "__init__", return_value=None
    )

    # Initialize the lifecycle service
    fake_services.get("lifecycle")

    mock_obtain_image.assert_called_once_with()
    mock_lifecycle.assert_called_once_with(
        mock.ANY,
        application_name="rockcraft",
        arch="riscv64",
        base="ubuntu@24.04",
        build_base="ubuntu@24.04",
        base_layer_dir=Path(),
        base_layer_hash=b"deadbeef",
        cache_dir=project_path / "cache",
        ignore_local_sources=[".craft", "*.rock"],
        parallel_build_count=4,
        partitions=None,
        project_name="test-rock",
        project_vars=ProjectVarInfo(
            root={
                "version": ProjectVar(value="0.1", updated=False, part_name=None),
                "summary": ProjectVar(value="Rock on!", updated=False, part_name=None),
                "description": ProjectVar(
                    value="Ramble off!", updated=False, part_name=None
                ),
            }
        ),
        work_dir=project_path,
        rootfs_dir=Path(),
        track_stage_packages=True,
        usrmerged_by_default=False,
    )


@pytest.mark.usefixtures("configured_project", "project_keys")
@pytest.mark.parametrize(
    "project_keys",
    [
        {
            "base": "ubuntu@24.04",
            "package-repositories": [{"type": "apt", "ppa": "ppa/ppa"}],
        }
    ],
)
def test_lifecycle_package_repositories(extra_project_params, fake_services, mocker):
    base = cast(services.ProjectService, fake_services.get("project")).get().base
    mocker.patch.object(util, "get_host_base", return_value=base)
    fake_repositories = extra_project_params["package_repositories"]
    lifecycle_service = fake_services.get("lifecycle")
    lifecycle_service._lcm = mock.MagicMock(spec=LifecycleManager)

    # Installation of repositories in the build instance
    mock_install = mocker.patch.object(repositories, "install_package_repositories")
    # Installation of repositories in overlays
    mock_callback = mocker.patch.object(callbacks, "register_configure_overlay")

    lifecycle_service.run("prime")

    mock_install.assert_called_once_with(
        fake_repositories, lifecycle_service._lcm, local_keys_path=None
    )
    mock_callback.assert_called_once_with(repositories.install_overlay_repositories)


def _create_step_info(tmp_path, plugin_name, base, build_base) -> tuple[StepInfo, Path]:
    # The test setup is rather involved because we need to recreate/mock an
    # exact set of circumstances here:

    # 1) Create a project with the given base;
    dirs = ProjectDirs(work_dir=tmp_path)
    project_info = ProjectInfo(
        project_dirs=dirs,
        application_name="test",
        cache_dir=tmp_path,
        strict_mode=False,
        base=base,
        build_base=build_base,
    )

    # 2) Create a part using the Python plugin;
    part = Part("p1", {"source": ".", "plugin": plugin_name})
    part_info = PartInfo(project_info=project_info, part=part)

    prime_dir = dirs.prime_dir
    prime_dir.mkdir()

    # 4) Create a StepInfo that contains all of this.
    step_info = StepInfo(part_info=part_info, step=Step.PRIME)
    step_info.state = PrimeState(part_properties=part.spec.marshal(), files=set())

    return step_info, prime_dir


@pytest.mark.parametrize("plugin_name", get_python_plugins("ubuntu@24.04"))
@pytest.mark.parametrize("base", ["bare", "ubuntu@24.04"])
@pytest.mark.parametrize("build_base", ["ubuntu@24.04"])
def test_python_usrmerge_fix(tmp_path, plugin_name, base, build_base):
    step_info, prime_dir = _create_step_info(tmp_path, plugin_name, base, build_base)

    # Setup a 'prime' directory where "lib64" is a symlink to "lib";
    (prime_dir / "lib").mkdir()
    (prime_dir / "lib64").symlink_to("lib")
    assert sorted(os.listdir(prime_dir)) == ["lib", "lib64"]  # noqa: PTH208 (use Path.iterdir())

    assert step_info.state is not None
    step_info.state.files.update({Path("lib64")})

    lifecycle_module._python_usrmerge_fix(step_info)

    # After running the fix the "lib64" symlink must be gone
    assert sorted(os.listdir(prime_dir)) == ["lib"]  # noqa: PTH208 (use Path.iterdir())


@pytest.mark.parametrize("source_file", ["from-install", "from-stage"])
def test_python_v2_shebang_fix(tmp_path, monkeypatch, source_file):
    monkeypatch.chdir(tmp_path)
    step_info, prime_dir = _create_step_info(
        tmp_path, "python", "ubuntu@25.10", "devel"
    )

    # Setup a 'prime' directory with some files
    bin_dir = prime_dir / "usr/bin"
    bin_dir.mkdir(parents=True)
    files: set[Path] = set()

    # 'script' is a file with a shebang pointing to either the part's install dir
    # ('from-install'), or from the stage dir ('from-stage').
    script = bin_dir / "script"
    data_file = Path(__file__).parent / f"test_lifecycle/{source_file}"
    shutil.copy(data_file, script)
    script.write_text(script.read_text().replace("/root", str(tmp_path)))
    files.add(Path("usr/bin/script"))

    # Also add some "bad" entries to ensure the function is resilient

    # Add an entry without a corresponding 'concrete' file, which might've been pruned
    # by another post-prime function
    files.add(Path("i-dont-exist"))

    # Add a binary file
    bin_file = bin_dir / "binary"
    bin_file.write_bytes(b"\x81")
    files.add(Path("usr/bin/binary"))

    assert step_info.state is not None
    step_info.state.files.update(files)

    lifecycle_module._python_v2_shebang_fix(step_info)

    contents = script.read_text()
    assert contents.startswith("#!/usr/bin/python3\n")


@pytest.mark.usefixtures("configured_project", "project_keys")
@pytest.mark.parametrize(
    ("project_keys", "expected_default"),
    [
        # Focal cases (no usrmerge)
        pytest.param({"base": "ubuntu@20.04"}, False, id="focal"),
        pytest.param(
            {"base": "bare", "build-base": "ubuntu@20.04"}, False, id="focal-bare"
        ),
        # Jammy cases (no usrmerge)
        pytest.param({"base": "ubuntu@22.04"}, False, id="jammy"),
        pytest.param(
            {"base": "bare", "build-base": "ubuntu@22.04"}, False, id="jammy-bare"
        ),
        # Noble cases (no usrmerge)
        pytest.param({"base": "ubuntu@24.04"}, False, id="noble"),
        pytest.param(
            {"base": "bare", "build-base": "ubuntu@24.04"}, False, id="noble-bare"
        ),
        # Questing cases (currently devel) (yes usrmerge)
        pytest.param({"base": "ubuntu@25.10", "build-base": "devel"}, True, id="devel"),
        pytest.param({"base": "bare", "build-base": "devel"}, True, id="devel-bare"),
    ],
)
def test_usrmerged_by_default(
    default_image_info,
    mocker,
    fake_services,
    expected_default,
):
    _mock_obtain_image = mocker.patch.object(
        fake_services.get("image"), "obtain_image", return_value=default_image_info
    )
    mock_lifecycle = mocker.patch.object(
        LifecycleManager, "__init__", return_value=None
    )

    # Initialize the lifecycle service
    fake_services.get("lifecycle")

    assert mock_lifecycle.called
    call = mock_lifecycle.mock_calls[0]
    assert call.kwargs["usrmerged_by_default"] == expected_default
