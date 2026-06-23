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

"""Extension processor and related utilities."""

from ._utils import apply_extensions
from .app_parts import gen_logging_part
from .expressjs import ExpressJSFramework, ExpressJSFrameworkFactory, ExpressJSFrameworkV2
from .fastapi import FastAPIFramework, FastAPIFrameworkV2, FastAPIFrameworkFactory
from .go import GoFramework
from .gunicorn import (
    DjangoFramework,
    DjangoFrameworkV2,
    DjangoFrameworkFactory,
    FlaskFramework,
    FlaskFrameworkV2,
    FlaskFrameworkFactory,
)
from .registry import get_extension_class, get_extension_names, register, unregister
from .springboot import SpringBootFramework

__all__ = [
    "get_extension_class",
    "get_extension_names",
    "apply_extensions",
    "register",
    "unregister",
    "gen_logging_part",
    "DjangoFramework",
    "DjangoFrameworkV2",
    "ExpressJSFramework",
    "ExpressJSFrameworkV2",
    "FastAPIFramework",
    "FastAPIFrameworkV2",
    "FlaskFramework",
    "FlaskFrameworkV2",
]

register("django-framework", DjangoFrameworkFactory)  # type: ignore[arg-type]
register("expressjs-framework", ExpressJSFrameworkFactory)  # type: ignore[arg-type]
register("fastapi-framework", FastAPIFrameworkFactory)  # type: ignore[arg-type]
register("flask-framework", FlaskFrameworkFactory)  # type: ignore[arg-type]
register("go-framework", GoFramework)
register("spring-boot-framework", SpringBootFramework)
