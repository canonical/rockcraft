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
import textwrap
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


def write_java_project():
    Path("pom.xml").write_text(
        textwrap.dedent(
            """
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<parent>
		<groupId>org.springframework.boot</groupId>
		<artifactId>spring-boot-starter-parent</artifactId>
		<version>3.2.3</version>
		<relativePath/> <!-- lookup parent from repository -->
	</parent>
	<groupId>example</groupId>
	<artifactId>app</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>app</name>
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-web</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-actuator</artifactId>
		</dependency>
	</dependencies>

	<build>
		<plugins>
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
			</plugin>
		</plugins>
	</build>

</project>
            """
        )
    )

    Path("app/src/main/java/example/app/Main.java").write_text(
        textwrap.dedent(
            """
        package example.app;

        import org.springframework.boot.SpringApplication;
        import org.springframework.boot.autoconfigure.SpringBootApplication;

        @SpringBootApplication
        public class Application {

            public Application(){
                System.out.println("Hello world!");
            }

            public static void main(String[] args) {
                SpringApplication.run(Application.class, args);
            }

        }
    """
        )
    )


def test_jlink_plugin_base(tmp_path, run_lifecycle):
    # pylint: disable=line-too-long
    # chisel snap is confined to user home
    user_home_tmp = Path(f"{os.path.expanduser("~")}/{os.path.basename(tmp_path)}")
    atexit.register(lambda: shutil.rmtree(user_home_tmp))
    parts = {
        "my-part": {
            "plugin": "jlink",
            "source": "https://github.com/vpa1977/chisel-releases",
            "source-type": "git",
            "source-branch": "24.04-openjdk-21-jre-headless",
        }
    }
    project = create_test_project("ubuntu@24.04", parts)
    run_lifecycle(project=project, work_dir=user_home_tmp)
    java = user_home_tmp / "stage/usr/bin/java"
    assert java.is_file()
