import json
import subprocess
from pathlib import Path
from typing import cast

import pytest
from craft_application import ServiceFactory
from craft_platforms import DebianArchitecture
from rockcraft import oci
from rockcraft.models.project import Project
from rockcraft.services import package


@pytest.mark.usefixtures("fake_project_file")
def test_media_type_in_packed_image_manifest(fake_services: ServiceFactory):
    base_image = oci.Image.new_oci_image(
        image_name="bare@original",
        image_dir=Path("images"),
        arch=DebianArchitecture.from_host(),
    )[0]

    fake_services.get("project").configure(platform="risky", build_for="riscv64")
    project = cast(Project, fake_services.get("project").get())

    # pylint: disable=protected-access
    archive_name = package._pack(
        prime_dir=Path("prime"),
        project=project,
        project_base_image=base_image,
        base_digest=b"deadbeef",
        rock_suffix="risky",
        build_for=project.platforms["risky"].build_for[0],
        base_layer_dir=Path("base_layer"),
    )

    manifest = subprocess.check_output(
        ["skopeo", "inspect", "--raw", f"oci-archive:{archive_name}"],
        stderr=subprocess.STDOUT,
    )
    manifest_content = json.loads(manifest)

    assert manifest_content["mediaType"] == "application/vnd.oci.image.manifest.v1+json"
