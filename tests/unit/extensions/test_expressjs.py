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
def package_json_file(tmp_path, expressjs_project_name):
    (tmp_path / "package.json").write_text(
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
        "name": "foo-bar",
        "platforms": {
            "amd64": {},
        },
        "run-user": "_daemon_",
        "parts": {
            "expressjs-framework/install-app": {
                "plugin": "npm",
                "npm-include-node": False,
                "source": "app/",
                "organise": {
                    f"lib/node_modules/{expressjs_project_name}/package.json": "app/package.json",
                },
                "override-prime": f"rm -rf lib/node_modules/{expressjs_project_name}",
            },
            "expressjs-framework/runtime-dependencies": {
                "plugin": "nil",
                "stage-packages": [
                    "ca-certificates_data",
                    "libpq5",
                    "node",
                ],
            },
        },
        "services": {
            "app": {
                "command": "npm start",
                "on-failure": "shutdown",
                "on-success": "shutdown",
                "override": "replace",
                "startup": "enabled",
                "working-dir": "/app",
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
    tmp_path, expressjs_input_yaml, package_json_contents, error_message
):
    (tmp_path / "package.json").write_text(package_json_contents)
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert str(exc.value) == error_message
    assert str(exc.value.doc_slug) == "/reference/extensions/expressjs-framework"


@pytest.mark.parametrize(
    "existing_files, missing_files, expected_organise",
    [
        pytest.param(
            ["lib/node_modules/test-expressjs-project/app.js"],
            [],
            {"lib/node_modules/test-expressjs-project/app.js": "app/app.js"},
            id="single file defined",
        ),
    ],
)
@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_install_app_prime_to_organise_map(
    tmp_path, expressjs_input_yaml, existing_files, missing_files, expected_organise
):
    for file in existing_files:
        (tmp_path / file).parent.mkdir(parents=True)
        (tmp_path / file).touch()
    prime_files = [*existing_files, *missing_files]
    expressjs_input_yaml["parts"] = {
        "expressjs-framework/install-app": {"prime": prime_files}
    }
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert (
        applied["parts"]["expressjs-framework/install-app"]["organise"]
        == expected_organise
    )
