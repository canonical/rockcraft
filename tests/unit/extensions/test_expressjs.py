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

_expressjs_project_name = "test-expressjs-project"


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
def expressjs_extension(mock_extensions):
    extensions.register("expressjs-framework", extensions.ExpressJSFrameworkFactory)


@pytest.fixture
def app_path(tmp_path):
    app_path = tmp_path / "app"
    app_path.mkdir(parents=True, exist_ok=True)
    return app_path


@pytest.fixture
def package_json_file(app_path):
    (app_path / "package.json").write_text(
        f"""{{
    "name": "{_expressjs_project_name}",
    "scripts": {{
        "start": "node ./bin/www"
    }}
}}"""
    )


@pytest.mark.parametrize(
    ("base", "npm_include_node", "node_version", "expected_yaml_dict"),
    [
        pytest.param(
            "ubuntu@24.04",
            False,
            None,
            {
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
                        "npm-include-node": False,
                        "npm-node-version": None,
                        "override-build": "rm -rf node_modules\n"
                        "craftctl default\n"
                        "npm config set script-shell=bash --location project\n"
                        "cp ${CRAFT_PART_BUILD}/.npmrc ${CRAFT_PART_INSTALL}/lib/node_modules/"
                        f"{_expressjs_project_name}/.npmrc\n"
                        f"chown -R 584792:584792 ${{CRAFT_PART_INSTALL}}/lib/node_modules/{_expressjs_project_name}\n"
                        f"ln -s /lib/node_modules/{_expressjs_project_name} "
                        "${CRAFT_PART_INSTALL}/app\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/app\n",
                        "build-packages": ["nodejs", "npm"],
                        "stage-packages": ["ca-certificates_data", "nodejs_bins"],
                        "build-environment": [{"UV_USE_IO_URING": "0"}],
                    },
                    "expressjs-framework/runtime": {
                        "plugin": "nil",
                        "stage": ["-etc/ssl/certs/ca-certificates.crt"],
                        "stage-packages": ["npm"],
                    },
                    "expressjs-framework/logging": {
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
                    "expressjs": {
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                        "command": "npm start",
                        "environment": {"NODE_ENV": "production"},
                    },
                },
            },
            id="ubuntu@24.04",
        ),
        pytest.param(
            "ubuntu@24.04",
            True,
            "1.0.0",
            {
                "base": "ubuntu@24.04",
                "build-base": "ubuntu@24.04",
                "name": "foo-bar",
                "parts": {
                    "expressjs-framework/install-app": {
                        "npm-include-node": True,
                        "npm-node-version": "1.0.0",
                        "override-build": "rm -rf node_modules\n"
                        "craftctl default\n"
                        "npm config set script-shell=bash --location project\n"
                        "cp ${CRAFT_PART_BUILD}/.npmrc "
                        "${CRAFT_PART_INSTALL}/lib/node_modules/test-expressjs-project/.npmrc\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/lib/node_modules/test-expressjs-project\n"
                        "ln -s /lib/node_modules/test-expressjs-project "
                        "${CRAFT_PART_INSTALL}/app\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/app\n",
                        "plugin": "npm",
                        "source": "app/",
                        "stage-packages": ["ca-certificates_data"],
                        "build-environment": [{"UV_USE_IO_URING": "0"}],
                    },
                    "expressjs-framework/logging": {
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
                "platforms": {
                    "amd64": {},
                },
                "run-user": "_daemon_",
                "services": {
                    "expressjs": {
                        "command": "npm start",
                        "environment": {
                            "NODE_ENV": "production",
                        },
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    },
                },
            },
            id="ubuntu@24.04",
        ),
        pytest.param(
            "bare",
            False,
            None,
            {
                "base": "bare",
                "build-base": "ubuntu@24.04",
                "name": "foo-bar",
                "parts": {
                    "expressjs-framework/install-app": {
                        "build-packages": [
                            "nodejs",
                            "npm",
                        ],
                        "npm-include-node": False,
                        "npm-node-version": None,
                        "override-build": "rm -rf node_modules\n"
                        "craftctl default\n"
                        "npm config set script-shell=bash --location project\n"
                        "cp ${CRAFT_PART_BUILD}/.npmrc "
                        "${CRAFT_PART_INSTALL}/lib/node_modules/test-expressjs-project/.npmrc\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/lib/node_modules/test-expressjs-project\n"
                        "ln -s /lib/node_modules/test-expressjs-project "
                        "${CRAFT_PART_INSTALL}/app\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/app\n"
                        "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh",
                        "plugin": "npm",
                        "source": "app/",
                        "stage-packages": [
                            "bash_bins",
                            "ca-certificates_data",
                            "coreutils_bins",
                        ],
                        "build-environment": [{"UV_USE_IO_URING": "0"}],
                    },
                    "expressjs-framework/runtime": {
                        "plugin": "nil",
                        "stage": ["-etc/ssl/certs/ca-certificates.crt"],
                        "stage-packages": [
                            "libstdc++6",
                            "zlib1g",
                            "npm",
                        ],
                    },
                    "expressjs-framework/logging": {
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
                "platforms": {
                    "amd64": {},
                },
                "run-user": "_daemon_",
                "services": {
                    "expressjs": {
                        "command": "npm start",
                        "environment": {
                            "NODE_ENV": "production",
                        },
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    },
                },
            },
            id="ubuntu@24.04",
        ),
        pytest.param(
            "bare",
            True,
            "1.0.0",
            {
                "base": "bare",
                "build-base": "ubuntu@24.04",
                "name": "foo-bar",
                "parts": {
                    "expressjs-framework/install-app": {
                        "npm-include-node": True,
                        "npm-node-version": "1.0.0",
                        "override-build": "rm -rf node_modules\n"
                        "craftctl default\n"
                        "npm config set script-shell=bash --location project\n"
                        "cp ${CRAFT_PART_BUILD}/.npmrc "
                        "${CRAFT_PART_INSTALL}/lib/node_modules/test-expressjs-project/.npmrc\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/lib/node_modules/test-expressjs-project\n"
                        "ln -s /lib/node_modules/test-expressjs-project "
                        "${CRAFT_PART_INSTALL}/app\n"
                        "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/app\n"
                        "ln -sf /usr/bin/bash ${CRAFT_PART_INSTALL}/usr/bin/sh",
                        "plugin": "npm",
                        "source": "app/",
                        "stage-packages": [
                            "bash_bins",
                            "ca-certificates_data",
                            "coreutils_bins",
                        ],
                        "build-environment": [{"UV_USE_IO_URING": "0"}],
                    },
                    "expressjs-framework/runtime": {
                        "plugin": "nil",
                        "stage": ["-etc/ssl/certs/ca-certificates.crt"],
                        "stage-packages": ["libstdc++6", "zlib1g"],
                    },
                    "expressjs-framework/logging": {
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
                "platforms": {
                    "amd64": {},
                },
                "run-user": "_daemon_",
                "services": {
                    "expressjs": {
                        "command": "npm start",
                        "environment": {
                            "NODE_ENV": "production",
                        },
                        "override": "replace",
                        "startup": "enabled",
                        "user": "_daemon_",
                        "working-dir": "/app",
                    },
                },
            },
            id="ubuntu@24.04",
        ),
    ],
)
@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_extension_default(
    tmp_path,
    expressjs_input_yaml,
    base,
    npm_include_node,
    node_version,
    expected_yaml_dict,
):
    expressjs_input_yaml["base"] = base
    expressjs_input_yaml["parts"] = {
        "expressjs-framework/install-app": {
            "npm-include-node": npm_include_node,
            "npm-node-version": node_version,
        }
    }
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)

    assert applied == expected_yaml_dict


@pytest.mark.usefixtures("expressjs_extension")
def test_expressjs_no_package_json_error(tmp_path, expressjs_input_yaml):
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert str(exc.value) == "missing package.json file in 'app' directory"
    assert (
        str(exc.value.doc_slug)
        == "/reference/extensions/express-framework/#project-requirements"
    )


@pytest.mark.parametrize(
    ("package_json_path", "package_json_contents", "error_message"),
    [
        ("invalid-path", "", "missing package.json file in 'app' directory"),
        ("package.json", "[]", "invalid package.json file"),
        (
            "package.json",
            "{",
            "failed to parse package.json; it might contain invalid JSON",
        ),
        ("package.json", "{}", "missing 'scripts.start' field in package.json"),
        (
            "package.json",
            '{"scripts":{}}',
            "missing 'scripts.start' field in package.json",
        ),
        (
            "package.json",
            '{"scripts":{"start":"node ./bin/www"}}',
            "missing 'name' field in package.json",
        ),
    ],
)
@pytest.mark.usefixtures("expressjs_extension")
def test_expressjs_invalid_package_json_scripts_error(
    tmp_path,
    app_path,
    expressjs_input_yaml,
    package_json_path,
    package_json_contents,
    error_message,
):
    (app_path / package_json_path).write_text(package_json_contents)
    with pytest.raises(ExtensionError) as exc:
        extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert str(exc.value) == error_message
    assert (
        str(exc.value.doc_slug)
        == "/reference/extensions/express-framework/#project-requirements"
    )


@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_extension_bare_base_with_ubuntu2604_build_base(
    tmp_path, monkeypatch, expressjs_input_yaml
):
    """base:bare + build-base:ubuntu@26.04 should dispatch to V2 without error."""
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    expressjs_input_yaml["base"] = "bare"
    expressjs_input_yaml["build-base"] = "ubuntu@26.04"
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)
    assert isinstance(
        extensions.ExpressJSFrameworkFactory(
            project_root=tmp_path,
            yaml_data={"name": "x", "base": "bare", "build-base": "ubuntu@26.04"},
        ),
        extensions.ExpressJSFrameworkV2,
    )
    assert applied["base"] == "bare"
    assert applied["build-base"] == "ubuntu@26.04"


def test_expressjs_factory_dispatch(tmp_path):
    factory = extensions.ExpressJSFrameworkFactory

    v1 = factory(project_root=tmp_path, yaml_data={"name": "x", "base": "ubuntu@24.04"})
    assert isinstance(v1, extensions.ExpressJSFramework)
    assert not isinstance(v1, extensions.ExpressJSFrameworkV2)

    v2 = factory(project_root=tmp_path, yaml_data={"name": "x", "base": "ubuntu@26.04"})
    assert isinstance(v2, extensions.ExpressJSFrameworkV2)


def test_expressjs_v2_and_factory_supported_bases():
    assert "ubuntu@26.04" in extensions.ExpressJSFrameworkV2.get_supported_bases()

    factory_bases = extensions.ExpressJSFrameworkFactory.get_supported_bases()
    assert "ubuntu@26.04" in factory_bases
    for base in extensions.ExpressJSFramework.get_supported_bases():
        assert base in factory_bases


@pytest.mark.usefixtures("expressjs_extension", "package_json_file")
def test_expressjs_extension_ubuntu2604_default(
    tmp_path, monkeypatch, expressjs_input_yaml
):
    monkeypatch.setenv("ROCKCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS", "1")
    expressjs_input_yaml["base"] = "ubuntu@26.04"
    expressjs_input_yaml["build-base"] = "ubuntu@26.04"
    expressjs_input_yaml["parts"] = {
        "expressjs-framework/install-app": {
            "npm-include-node": False,
            "npm-node-version": None,
        }
    }
    applied = extensions.apply_extensions(tmp_path, expressjs_input_yaml)

    expected = {
        "base": "ubuntu@26.04",
        "build-base": "ubuntu@26.04",
        "name": "foo-bar",
        "platforms": {"amd64": {}},
        "run-user": "_daemon_",
        "parts": {
            "expressjs-framework/install-app": {
                "plugin": "npm",
                "source": "app/",
                "npm-include-node": False,
                "npm-node-version": None,
                "override-build": (
                    "rm -rf node_modules\n"
                    "craftctl default\n"
                    "npm config set script-shell=bash --location project\n"
                    "cp ${CRAFT_PART_BUILD}/.npmrc ${CRAFT_PART_INSTALL}/lib/node_modules/"
                    f"{_expressjs_project_name}/.npmrc\n"
                    f"chown -R 584792:584792 ${{CRAFT_PART_INSTALL}}/lib/node_modules/{_expressjs_project_name}\n"
                    f"ln -s /lib/node_modules/{_expressjs_project_name} "
                    "${CRAFT_PART_INSTALL}/app\n"
                    "chown -R 584792:584792 ${CRAFT_PART_INSTALL}/app\n"
                ),
                "build-packages": ["nodejs", "npm"],
                "stage-packages": ["ca-certificates_data", "nodejs_bins"],
                "build-environment": [{"UV_USE_IO_URING": "0"}],
            },
            "expressjs-framework/runtime": {
                "plugin": "nil",
                "stage-packages": ["npm"],
                "stage": ["-etc/ssl/certs/ca-certificates.crt"],
            },
            "expressjs-framework/logging": {
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
            "expressjs": {
                "override": "replace",
                "startup": "enabled",
                "user": "_daemon_",
                "working-dir": "/app",
                "command": "npm start",
                "environment": {"NODE_ENV": "production"},
            },
        },
    }
    assert applied == expected
