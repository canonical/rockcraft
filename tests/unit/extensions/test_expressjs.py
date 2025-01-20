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


@pytest.fixture(name="expressjs_input_yaml")
def expressjs_input_yaml_fixture():
    return {
        "name": "foo-bar",
        "base": "ubuntu@24.04",
        "build-base": "ubuntu@24.04",
        "platforms": {"amd64": {}},
        "extensions": ["expressjs-framework"],
    }


@pytest.fixture
def expressjs_extension(mock_extensions, monkeypatch):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    extensions.register("expressjs-framework", extensions.ExpressJSFramework)


@pytest.fixture
def expressjs_project_name():
    return "test-expressjs-project"


@pytest.fixture
def app_path(tmp_path):
    app_path = tmp_path / "app"
    app_path.mkdir(parents=True, exist_ok=True)
    return app_path


@pytest.fixture
def package_json_file(app_path, expressjs_project_name):
    (app_path / "package.json").write_text(
        f"""{{
    "name": "{expressjs_project_name}",
    "scripts": {{
        "start": "node ./bin/www"
    }}
}}"""
    )


@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_extension_default(
    tmp_path, expressjs_project_name, expressjs_input_yaml
):
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)

    assert applied == {
        "base": "ubuntu@24.04",
        "build-base": "ubuntu@24.04",
        "name": "foo-bar",
        "platforms": {
            "amd64": {},
        },
        "run-user": "_daemon_",
        "parts": {
            "expressjs-framework/install-app": {
                "plugin": "npm",
                "source": "app/",
                "override-build": (
                    "craftctl default\n"
                    "npm config set script-shell=bash --location project\n"
                    "cp ${CRAFT_PART_BUILD}/.npmrc ${CRAFT_PART_INSTALL}/lib/node_modules/"
                    f"{expressjs_project_name}/.npmrc\n"
                    f"ln -s /lib/node_modules/{expressjs_project_name} "
                    "${CRAFT_PART_INSTALL}/app\n"
                ),
                "build-packages": ["nodejs", "npm"],
                "stage-packages": ["ca-certificates_data", "nodejs_bins"],
            },
            "expressjs-framework/runtime": {"plugin": "nil", "stage-packages": ["npm"]},
        },
        "services": {
            "expressjs": {
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
                "working-dir": "/app",
                "command": "npm start",
            },
        },
    }


@pytest.mark.usefixtures("expressjs_extension")
def test_expressjs_no_package_json_error(tmp_path, expressjs_input_yaml):
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert str(exc.value) == "missing package.json file"
    assert str(exc.value.doc_slug) == "/reference/extensions/expressjs-framework"


@pytest.mark.parametrize(
    "package_json_contents, error_message",
    [
        ("{}", "missing start script"),
        ('{"scripts":{}}', "missing start script"),
        ('{"scripts":{"start":"node ./bin/www"}}', "missing application name"),
    ],
)
@pytest.mark.usefixtures("expressjs_extension")
def test_expressjs_invalid_package_json_scripts_error(
    tmp_path, app_path, expressjs_input_yaml, package_json_contents, error_message
):
    (app_path / "package.json").write_text(package_json_contents)
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert str(exc.value) == error_message
    assert str(exc.value.doc_slug) == "/reference/extensions/expressjs-framework"


@pytest.mark.parametrize(
    "base, expected_build_packages, expected_stage_packages",
    [
        pytest.param(
            "ubuntu@24.04",
            ["nodejs", "npm"],
            ["ca-certificates_data", "nodejs_bins"],
            id="ubuntu@24.04",
        ),
        pytest.param(
            "bare",
            ["nodejs", "npm"],
            ["bash_bins", "ca-certificates_data", "nodejs_bins", "coreutils_bins"],
            id="bare",
        ),
    ],
)
@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_install_app_default_node_install(
    tmp_path,
    expressjs_input_yaml,
    base,
    expected_build_packages,
    expected_stage_packages,
):
    expressjs_input_yaml["base"] = base
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)

    assert applied["parts"]["expressjs-framework/install-app"]["build-packages"] == (
        expected_build_packages
    )
    assert applied["parts"]["expressjs-framework/install-app"]["stage-packages"] == (
        expected_stage_packages
    )


@pytest.mark.parametrize(
    "base, expected_stage_packages",
    [
        pytest.param(
            "ubuntu@24.04",
            ["ca-certificates_data"],
            id="24.04 base",
        ),
        pytest.param(
            "bare",
            ["bash_bins", "ca-certificates_data", "nodejs_bins", "coreutils_bins"],
            id="bare base",
        ),
    ],
)
@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_install_app_user_defined_node_install(
    tmp_path,
    expressjs_input_yaml,
    base,
    expected_stage_packages,
):
    expressjs_input_yaml["base"] = base
    expressjs_input_yaml["parts"] = {
        "expressjs-framework/install-app": {
            "npm-include-node": True,
            "npm-node-version": "node",
        }
    }
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)

    assert applied["parts"]["expressjs-framework/install-app"]["build-packages"] == []
    assert (
        applied["parts"]["expressjs-framework/install-app"]["stage-packages"]
        == expected_stage_packages
    )


@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_runtime_user_defined_node_install(tmp_path, expressjs_input_yaml):
    expressjs_input_yaml["parts"] = {
        "expressjs-framework/install-app": {
            "npm-include-node": True,
            "npm-node-version": "node",
        }
    }
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)

    assert applied["parts"]["expressjs-framework/runtime"]["stage-packages"] == []
