# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2021,2024 Canonical Ltd.
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

"""Project definition and helpers."""

import re
import typing
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Literal

import craft_cli
import pydantic
import spdx_lookup  # type: ignore[import-untyped]
from craft_application.models import (
    Platform,
)
from craft_application.models import Project as BaseProject
from craft_application.models.base import alias_generator
from craft_application.models.project import DevelBaseInfo
from craft_platforms import DebianArchitecture
from craft_providers import bases
from craft_providers.bases import BuilddBaseAlias
from craft_providers.errors import BaseConfigurationError
from typing_extensions import override

from rockcraft.architectures import SUPPORTED_ARCHS
from rockcraft.parts import part_has_overlay
from rockcraft.pebble import Check, Service
from rockcraft.usernames import SUPPORTED_GLOBAL_USERNAMES
from rockcraft.utils import parse_command

# pyright workaround
if TYPE_CHECKING:
    _RunUser = str | None
else:
    _RunUser = Literal[tuple(SUPPORTED_GLOBAL_USERNAMES)] | None


MESSAGE_ENTRYPOINT_CHANGED = (
    "This operation will result in a rock with an "
    "atypical OCI Entrypoint. While that might be acceptable for testing and "
    "personal use, it shall require prior approval before submitting to a "
    "Canonical registry namespace."
)

DEPRECATED_COLON_BASES = ["ubuntu:20.04", "ubuntu:22.04"]


BaseT = Literal[
    "bare",
    "ubuntu@20.04",
    "ubuntu@22.04",
    "ubuntu@24.04",
    "ubuntu@25.10",
    "ubuntu@26.04",
]
BuildBaseT = typing.Annotated[
    Literal[
        "ubuntu@20.04",
        "ubuntu@22.04",
        "ubuntu@24.04",
        "ubuntu@25.10",
        "devel",
    ]
    | None,
    pydantic.Field(validate_default=True),
]


class Project(BaseProject):
    """Rockcraft project definition."""

    # Type of summary is Optional[str] in BaseProject
    summary: str = pydantic.Field(  # type: ignore[reportIncompatibleVariableOverride]
        description="A short, single line description of the rock."
    )
    description: str = pydantic.Field(  # type: ignore[reportIncompatibleVariableOverride]
        description="A full description of the rock, potentially including multiple paragraphs."
    )
    """A full description of the rock, potentially including multiple paragraphs.

    The description should say in full what the rock is for and who may find it useful.
    """
    environment: dict[str, str] | None = pydantic.Field(
        default=None,
        description="Additional environment variables for the base image's OCI environment.",
    )
    run_user: _RunUser = pydantic.Field(
        default=None, description="The default OCI user. If unset, runs as root."
    )
    """The default OCI user. Must be a shared user.

    Currently, the only supported shared user is ``_daemon_`` (UID/GID 584792).
    If unset, the user ``root`` (UID/GID 0) is selected as the default OCI user.
    """
    services: dict[str, Service] | None = pydantic.Field(
        default=None,
        description="Services to run in the rock, using Pebble's layer specification syntax.",
    )
    """Services to run in the rock.

    This map of services is added to the Pebble configuration layer conforming to the
    :external+pebble:ref:`layer specification <layer-specification>`.
    """
    checks: dict[str, Check] | None = pydantic.Field(
        default=None,
        description="Health checks for this rock.",
    )
    entrypoint_service: str | None = pydantic.Field(
        default=None,
        description=(
            "The optional name of the Pebble service to serve as the entrypoint."
        ),
        examples=["my-service"],
    )
    """The optional name of the Pebble service to serve as the `OCI entrypoint
    <https://specs.opencontainers.org/image-spec/config/?v=v1.0.1#properties>`_.

    .. caution::

        Only set this key when the deployment environment has a container image
        entrypoint that is guaranteed to be static.

    If set, this makes Rockcraft extend ``["/bin/pebble", "enter"]`` with
    ``["--args", "<serviceName>"]``. The command of the Pebble service must
    contain an optional argument that will become the `OCI CMD
    <https://specs.opencontainers.org/image-spec/config/?v=v1.0.1#properties>`_.

    This key is mutually incompatible with the ``entrypoint-command`` key.
    """
    entrypoint_command: str | None = pydantic.Field(
        default=None,
        examples=["echo [ Hello ]"],
        description=(
            "Overrides the rock's default Pebble OCI entrypoint and CMD properties."
        ),
    )
    """Overrides the rock's default Pebble OCI ``entrypoint`` and ``CMD`` properties.

    .. important::

        Only set this key for certain categories of general-purpose rocks where
        Pebble services aren't appropriate, such as the Ubuntu OS and base images.

    The value can be suffixed with default entrypoint arguments using square
    brackets (``[]``). These entrypoint arguments become the rock's OCI CMD.

    This key is mutually incompatible with the ``entrypoint-service`` key.
    """
    base: BaseT = pydantic.Field(  # type: ignore[reportIncompatibleVariableOverride]
        description="The base system image for the rock.",
    )
    """
    The base system image that the rock's contents will be layered on.

    :ref:`This system <explanation-bases>` is mounted and made available when using
    overlays. The special value ``bare`` means that the rock will have no base system,
    which is typically used with static binaries or
    :ref:`Chisel slices <explanation-chisel>`.
    """
    build_base: BuildBaseT = pydantic.Field(  # type: ignore[reportIncompatibleVariableOverride]
        default=None, description="The system used to build the rock."
    )
    """The system and version that will be used during the rock's build, but not
    included in the final rock itself.

    The :ref:`build base <explanation-bases>` comprises the set of tools and libraries
    that Rockcraft uses when building the rock's contents.

    This key is mandatory if ``base`` is ``bare``. Otherwise, it is optional and
    defaults to the value of ``base``.
    """

    model_config = pydantic.ConfigDict(
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,
        alias_generator=alias_generator,
        frozen=True,
    )

    @override
    @classmethod
    def _providers_base(cls, base: str) -> bases.BaseAlias | None:
        """Get a BaseAlias from rockcraft's base.

        :param base: The base name.

        :returns: The BaseAlias for the base or None for bare bases.
        :raises ValueError: If the project's base cannot be determined.
        """
        if base == "bare":
            return None

        if base == "devel":
            return bases.get_base_alias(("ubuntu", "devel"))

        try:
            name, channel = base.split("@")
            return bases.get_base_alias(bases.BaseName(name, channel))
        except (ValueError, BaseConfigurationError) as err:
            raise ValueError(f"Unknown base {base!r}") from err

    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_unsupported_options(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Before validation, check if unsupported fields exist. Exit if so."""
        # pylint: disable=unused-argument
        unsupported_msg = str(
            "The fields 'entrypoint', 'cmd' and 'env' are not supported in "
            "Rockcraft. All rocks have Pebble as their entrypoint, so you must "
            "use 'services' to define your container application and "
            "respective environment."
        )
        unsupported_fields = ["cmd", "entrypoint", "env"]
        if any(field in values for field in unsupported_fields):
            raise ValueError(unsupported_msg)

        return values

    @pydantic.field_validator("build_base")
    @classmethod
    def _validate_build_base(
        cls, value: str | None, info: pydantic.ValidationInfo
    ) -> str | None:
        """Build-base defaults to the base value if not specified.

        :raises CraftValidationError: If base validation fails.
        """
        if not value:
            base_value = info.data.get("base")
            if base_value == "bare":
                raise ValueError(
                    'When "base" is "bare", a build-base must be specified.'
                )
            return base_value
        return value

    @pydantic.field_validator("base", mode="before")
    @classmethod
    def _validate_deprecated_base(cls, base_value: str | None) -> str | None:
        return cls._check_deprecated_base(base_value, "base")

    @pydantic.field_validator("build_base", mode="before")
    @classmethod
    def _validate_deprecated_build_base(cls, base_value: str | None) -> str | None:
        return cls._check_deprecated_base(base_value, "build-base")

    @staticmethod
    def _check_deprecated_base(base_value: str | None, field_name: str) -> str | None:
        if base_value in DEPRECATED_COLON_BASES:
            at_value = base_value.replace(":", "@")
            message = (
                f'Warning: use of ":" in field "{field_name}" is deprecated. '
                f'Prefer "{at_value}" instead.'
            )
            craft_cli.emit.message(message)
            return at_value

        return base_value

    @pydantic.field_validator("license")
    @classmethod
    def _validate_license(
        cls,
        license: str | None,  # pylint: disable=redefined-builtin  # noqa: A002
    ) -> str | None:
        """Make sure the provided license is valid and in SPDX format."""
        if not license:
            return None

        if license == "proprietary":
            # This is the license name we use on our stores.
            return license

        lic: spdx_lookup.License | None = spdx_lookup.by_id(license)  # type: ignore[reportUnknownMemberType]
        if lic is None:
            raise ValueError(
                f"License {license} not valid. It must be either 'proprietary' or in SPDX format.",
            )
        return str(lic.id)  # type: ignore[reportUnknownMemberType]

    @pydantic.model_validator(mode="before")
    @classmethod
    def _validate_title(cls, values: dict[str, Any]) -> dict[str, Any]:
        """If title is not provided, it defaults to the provided rock name."""
        if not values.get("title"):
            values["title"] = values.get("name")
        return values

    @pydantic.field_validator("parts")
    @classmethod
    def _validate_base_and_overlay(
        cls, parts: dict[str, Any], info: pydantic.ValidationInfo
    ) -> dict[str, Any]:
        """Projects with "bare" bases cannot use overlays."""
        if info.data.get("base") != "bare":
            return parts

        for part_name, part in parts.items():
            if part_has_overlay(part):
                raise ValueError(
                    f"Part '{part_name}' cannot use overlays with a 'bare' base"
                    " (there is no system to overlay)."
                )
        return parts

    @pydantic.field_validator("entrypoint_service")
    @classmethod
    def _validate_entrypoint_service(
        cls, entrypoint_service: str | None, info: pydantic.ValidationInfo
    ) -> str | None:
        """Verify that the entrypoint_service exists in the services dict."""
        craft_cli.emit.message(
            f"Warning: 'entrypoint-service' is defined. {MESSAGE_ENTRYPOINT_CHANGED}"
        )

        if entrypoint_service not in info.data.get("services", {}):
            raise ValueError(
                f"The provided entrypoint-service '{entrypoint_service}' is not a "
                "valid Pebble service."
            )

        command, args = parse_command(info.data["services"][entrypoint_service].command)

        if args is None:
            raise ValueError(
                f"The Pebble service '{entrypoint_service}' has a command {' '.join(command)} "
                "without default arguments and thus cannot be used as the "
                "entrypoint-service."
            )

        return entrypoint_service

    @pydantic.field_validator("entrypoint_command")
    @classmethod
    def _validate_entrypoint_command(
        cls, entrypoint_command: str, info: pydantic.ValidationInfo
    ) -> str | None:
        if info.data.get("entrypoint_service", None):
            raise ValueError(
                "The option 'entrypoint-command' cannot be used along 'entrypoint-service'."
            )

        craft_cli.emit.message(
            f"Warning: 'entrypoint-command' is defined. {MESSAGE_ENTRYPOINT_CHANGED}"
        )

        # Check arguments
        parse_command(entrypoint_command)

        return entrypoint_command

    @pydantic.field_validator("environment")
    @classmethod
    def _forbid_env_var_bash_interpolation(
        cls, environment: dict[str, str] | None
    ) -> dict[str, str]:
        """Variable interpolation isn't yet supported, so forbid attempts to do it."""
        if not environment:
            return {}

        values_with_dollar_signs = list(
            filter(lambda v: "$" in str(v[:-1]), environment.values())
        )
        if values_with_dollar_signs:
            raise ValueError(
                str(
                    "String interpolation not allowed for: "
                    f"{' ; '.join(values_with_dollar_signs)}"
                )
            )

        return environment

    def generate_metadata(
        self,
        generation_time: str,
        base_digest: bytes,
        architecture: DebianArchitecture | str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Generate the rock's metadata (both the OCI annotation and internal metadata.

        :param generation_time: the UTC time at the time of calling this method
        :param base_digest: digest of the base image

        :return: both the OCI annotation and internal metadata, as a tuple
        """
        metadata = {
            "name": self.name,
            "summary": self.summary,
            "title": self.title,
            "version": self.version,
            "created": generation_time,
            "base": self.base,
            "base-digest": base_digest.hex(),
            # `architecture` "looks like" a string since it inherits from it, but serialization
            # represents it as a DebianArchitecture, which comes out wrong (see rockcraft#992)
            # instead, explicitly cast it to just be an actual string
            "architecture": str(architecture),
        }

        if self.build_base == "devel":
            # Annotate that this project was built with a development base.
            metadata["grade"] = "devel"

        annotations = {
            "org.opencontainers.image.version": self.version,
            "org.opencontainers.image.title": self.title,
            "org.opencontainers.image.ref.name": self.name,
            "org.opencontainers.image.created": generation_time,
            "org.opencontainers.image.base.digest": base_digest.hex(),
            "org.opencontainers.image.description": re.sub(
                r"\n{2,}", "\n", self.summary
            )
            + f"\n\n{self.description}",
        }
        if self.license:
            annotations["org.opencontainers.image.licenses"] = self.license

        return (annotations, metadata)

    @override
    @classmethod
    def model_reference_slug(cls) -> str | None:
        return "/reference/rockcraft-yaml"

    @pydantic.field_validator("platforms")
    @classmethod
    def _validate_all_platforms(
        cls, platforms: dict[str, Platform]
    ) -> dict[str, Platform]:
        """Make sure all provided platforms are tangible and sane."""
        for platform_label, platform in platforms.items():
            error_prefix = f"Error for platform entry '{platform_label}'"

            # build_on and build_for are validated
            # let's also validate the platform label
            build_on_one_of = platform.build_on or [platform_label]

            # If the label maps to a valid architecture and
            # `build-for` is present, then both need to have the same value,
            # otherwise the project is invalid.
            if platform.build_for:
                build_target = platform.build_for[0]
                if platform_label in SUPPORTED_ARCHS and platform_label != build_target:
                    raise ValueError(
                        str(
                            f"{error_prefix}: if 'build-for' is provided and the "
                            "platform entry label corresponds to a valid architecture, then "
                            f"both values must match. {platform_label} != {build_target}"
                        )
                    )
            else:
                build_target = platform_label

            # Both build and target architectures must be supported
            if not any(b_o in SUPPORTED_ARCHS for b_o in build_on_one_of):
                raise ValueError(
                    str(
                        f"{error_prefix}: trying to build rock in one of "
                        f"{build_on_one_of}, but none of these build architectures is supported. "
                        f"Supported architectures: {list(SUPPORTED_ARCHS.keys())}"
                    )
                )

            if build_target not in SUPPORTED_ARCHS:
                raise ValueError(
                    str(
                        f"{error_prefix}: trying to build rock for target "
                        f"architecture {build_target}, which is not supported. "
                        f"Supported architectures: {list(SUPPORTED_ARCHS.keys())}"
                    )
                )

        return platforms

    @classmethod
    @override
    def _get_devel_bases(cls) -> Iterable[DevelBaseInfo]:
        return [
            DevelBaseInfo(
                current_devel_base=BuilddBaseAlias.RESOLUTE,
                devel_base=BuilddBaseAlias.DEVEL,
            )
        ]
