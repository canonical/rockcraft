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

from importlib import import_module
from typing import TYPE_CHECKING

from ._utils import apply_extensions
from .app_parts import gen_logging_part
from .registry import get_extension_class, get_extension_names, register, unregister

if TYPE_CHECKING:
    from .registry import ExtensionLoader, ExtensionType

__all__ = [
    "get_extension_class",
    "get_extension_names",
    "apply_extensions",
    "register",
    "unregister",
    "gen_logging_part",
]

# Registered extension name -> (framework submodule, class name). The framework
# modules pull in heavy deps (e.g. `packaging`), so they are imported lazily:
# only resolved when an extension is actually applied or listed. This keeps
# `rockcraft pack` of an extension-free rock from paying the import cost.
_LAZY_EXTENSIONS = {
    "django-framework": ("gunicorn", "DjangoFramework"),
    "expressjs-framework": ("expressjs", "ExpressJSFramework"),
    "fastapi-framework": ("fastapi", "FastAPIFramework"),
    "flask-framework": ("gunicorn", "FlaskFramework"),
    "go-framework": ("go", "GoFramework"),
    "spring-boot-framework": ("springboot", "SpringBootFramework"),
}


def _make_loader(module_suffix: str, class_name: str) -> "ExtensionLoader":
    def _load() -> "ExtensionType":
        module = import_module(f".{module_suffix}", __name__)
        return getattr(module, class_name)  # type: ignore[no-any-return]

    return _load


for _name, (_module_suffix, _class_name) in _LAZY_EXTENSIONS.items():
    register(_name, _make_loader(_module_suffix, _class_name))

# Class name -> (framework submodule, class name), for the __getattr__ below.
_CLASS_TO_MODULE = {
    class_name: (module_suffix, class_name)
    for module_suffix, class_name in _LAZY_EXTENSIONS.values()
}


def __getattr__(name: str) -> "ExtensionType":
    """Lazily expose the framework classes as `extensions.<ClassName>`.

    The classes are no longer imported at module load (see `_LAZY_EXTENSIONS`),
    but accessing them as attributes of this package still works -- the relevant
    framework module is imported on first access.
    """
    if name in _CLASS_TO_MODULE:
        module_suffix, class_name = _CLASS_TO_MODULE[name]
        module = import_module(f".{module_suffix}", __name__)
        return getattr(module, class_name)  # type: ignore[no-any-return]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
