# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2024 Canonical Ltd.
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

import pytest
from rockcraft import extensions
from rockcraft.errors import ExtensionError


@pytest.fixture(name="go_input_yaml")
def go_input_yaml_fixture():
    return {
        "name": "goprojectname",
        "base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
        "extensions": ["go-framework"],
    }


@pytest.fixture
def go_extension(mock_extensions, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("go-framework", extensions.GoFramework)


@pytest.mark.usefixtures("go_extension")
def test_go_extension_default(tmp_path, go_input_yaml):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)

    assert applied == {
        "base": "ubuntu@24.04",
        "name": "goprojectname",
        "platforms": {"amd64": {}},
        "run_user": "_daemon_",
        "parts": {
            "go-framework/base-layout": {
                "override-build": "mkdir -p ${CRAFT_PART_INSTALL}/app",
                "plugin": "nil",
                "permissions": [{"owner": 584792, "group": 584792}],
            },
            "go-framework/install-app": {
                "plugin": "go",
                "source": ".",
                "build-snaps": ["go"],
                "organize": {"bin/goprojectname": "usr/local/bin/goprojectname"},
                "stage": ["usr/local/bin/goprojectname"],
            },
            "go-framework/runtime": {
                "plugin": "nil",
                "stage-packages": [
                    "ca-certificates_data",
                ],
            },
            "go-framework/logging": {
                "plugin": "nil",
                "override-build": (
                    "craftctl default\n"
                    "mkdir -p $CRAFT_PART_INSTALL/opt/promtail\n"
                    "mkdir -p $CRAFT_PART_INSTALL/etc/promtail"
                ),
                "permissions": [
                    {"path": "opt/promtail", "owner": 584792, "group": 584792},
                    {"path": "etc/promtail", "owner": 584792, "group": 584792},
                ],
            },
        },
        "services": {
            "go": {
                "command": "goprojectname",
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
                "working-dir": "/app",
            },
        },
    }


@pytest.mark.usefixtures("go_extension")
def test_go_extension_bare(tmp_path):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    go_input_yaml = {
        "name": "foo-bar",
        "extensions": ["go-framework"],
        "base": "bare",
        "build-base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
    }
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)

    assert applied["parts"]["go-framework/runtime"] == {
        "plugin": "nil",
        "override-build": "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh",
        "stage-packages": ["ca-certificates_data", "bash_bins", "coreutils_bins"],
    }


@pytest.mark.usefixtures("go_extension")
def test_go_extension_no_go_mod_file_error(tmp_path, go_input_yaml):
    (tmp_path / "somefile").write_text("random text")
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, go_input_yaml)
    assert (
        str(exc.value)
        == "missing go.mod file, it should be present in the project directory"
    )
    assert (
        str(exc.value.doc_slug)
        == "/reference/extensions/go-framework/#project-requirements"
    )


@pytest.mark.usefixtures("go_extension")
@pytest.mark.parametrize("build_environment", [[], [{"OTHER_ENV_VAR": "val"}]])
def test_go_extension_base_bare(tmp_path, go_input_yaml, build_environment):
    go_input_yaml["base"] = "bare"
    if build_environment:
        go_input_yaml["parts"] = {
            "go-framework/install-app": {"build-environment": build_environment},
        }
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)

    assert "build-environment" in applied["parts"]["go-framework/install-app"]
    applied_build_environment = applied["parts"]["go-framework/install-app"][
        "build-environment"
    ]
    assert applied_build_environment == [{"CGO_ENABLED": "0"}, *build_environment]

    assert "permissions" in applied["parts"]["go-framework/base-layout"]
    applied_permissions = applied["parts"]["go-framework/base-layout"]["permissions"]
    assert applied_permissions == [{"owner": 584792, "group": 584792}]


@pytest.mark.usefixtures("go_extension")
@pytest.mark.parametrize(
    ("organize", "expected_organize"),
    [
        ({}, {"bin/goprojectname": "usr/local/bin/goprojectname"}),
        (
            {
                "bin/anotherbinary": "usr/local/bin/anotherbinary",
            },
            {
                "bin/goprojectname": "usr/local/bin/goprojectname",
                "bin/anotherbinary": "usr/local/bin/anotherbinary",
            },
        ),
        (
            {
                "bin/anotherbinary": "usr/local/bin/goprojectname",
            },
            {"bin/anotherbinary": "usr/local/bin/goprojectname"},
        ),
    ],
)
def test_go_extension_overrides_organize(
    tmp_path, go_input_yaml, organize, expected_organize
):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    if organize:
        go_input_yaml["parts"] = {
            "go-framework/install-app": {"organize": organize},
        }
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)
    assert applied["parts"]["go-framework/install-app"]["organize"] == expected_organize
    assert sorted(applied["parts"]["go-framework/install-app"]["stage"]) == sorted(
        expected_organize.values()
    )


@pytest.mark.usefixtures("go_extension")
@pytest.mark.parametrize(
    ("build_packages", "build_snaps", "expected_build_snaps"),
    [
        ([], [], ["go"]),
        ([], ["go/1.22/stable"], ["go/1.22/stable"]),
        ([], ["node"], ["go", "node"]),
        (["golang-go"], [], []),
        (["libp-dev"], [], ["go"]),
    ],
)
def test_go_extension_override_build_snaps(
    tmp_path, go_input_yaml, build_packages, build_snaps, expected_build_snaps
):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    if build_snaps or build_packages:
        go_input_yaml["parts"] = {
            "go-framework/install-app": {
                "build-snaps": build_snaps,
                "build-packages": build_packages,
            },
        }
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)
    assert sorted(
        applied["parts"]["go-framework/install-app"]["build-snaps"]
    ) == sorted(expected_build_snaps)


@pytest.mark.usefixtures("go_extension")
def test_go_extension_override_service_go_command(tmp_path, go_input_yaml):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    go_input_yaml["parts"] = {
        "go-framework/install-app": {
            "organize": {
                "bin/randombinary": "usr/local/bin/randombinary",
            },
        },
    }
    go_input_yaml["services"] = {
        "go": {"command": "time /user/local/bin/randombinary"},
    }
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)
    # No extra binary added to organize or stage, as the user decided to override services.go.command
    assert applied["parts"]["go-framework/install-app"]["organize"] == {
        "bin/randombinary": "usr/local/bin/randombinary"
    }
    assert applied["parts"]["go-framework/install-app"]["stage"] == [
        "usr/local/bin/randombinary"
    ]
    assert applied["services"]["go"]["command"] == "time /user/local/bin/randombinary"


@pytest.mark.usefixtures("go_extension")
def test_go_extension_extra_assets(tmp_path, go_input_yaml):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    (tmp_path / "static").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "migrate").write_text("migrate")
    (tmp_path / "migrate.sh").write_text("migrate")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "test").write_text("test")
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)
    assert applied["parts"]["go-framework/assets"] == {
        "plugin": "dump",
        "source": ".",
        "organize": {
            "static": "app/static",
            "migrate": "app/migrate",
            "migrate.sh": "app/migrate.sh",
            "templates": "app/templates",
        },
        "stage": ["app/migrate", "app/migrate.sh", "app/static", "app/templates"],
    }


@pytest.mark.usefixtures("go_extension")
def test_go_extension_extra_assets_overridden(tmp_path, go_input_yaml):
    (tmp_path / "go.mod").write_text("module projectname\n\ngo 1.22.4")
    (tmp_path / "static").mkdir()
    go_input_yaml["parts"] = {
        "go-framework/assets": {
            "plugin": "dump",
            "source": ".",
            "stage": ["app/foobar"],
        }
    }
    applied = extensions.apply_extensions(tmp_path, go_input_yaml)
    assert applied["parts"]["go-framework/assets"] == {
        "plugin": "dump",
        "source": ".",
        "organize": {
            "foobar": "app/foobar",
        },
        "stage": ["app/foobar"],
    }
