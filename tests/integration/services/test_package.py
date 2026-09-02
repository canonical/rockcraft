import argparse
import json
import subprocess
from pathlib import Path
from typing import cast

import pytest
from craft_application import ServiceFactory
from craft_application.commands.lifecycle import PackCommand
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
    archive_path = Path(
        f"{project.name}_{project.version}_risky.rock"
    )
    package._create_rock(
        path=archive_path,
        prime_dir=Path("prime"),
        project=project,
        project_base_image=base_image,
        base_digest=b"deadbeef",
        build_for=project.platforms["risky"].build_for[0],
        base_layer_dir=Path("base_layer"),
    )

    manifest = subprocess.check_output(
        ["skopeo", "inspect", "--raw", f"oci-archive:{archive_path}"],
        stderr=subprocess.STDOUT,
    )
    manifest_content = json.loads(manifest)

    assert manifest_content["mediaType"] == "application/vnd.oci.image.manifest.v1+json"


@pytest.mark.usefixtures("fake_project_file")
def test_pack_command_skips_current_artifact(
    emitter,
    fake_app_config,
    fake_services: ServiceFactory,
    mocker,
    tmp_path,
):
    fake_services.get("project").configure(platform="risky", build_for="riscv64")
    package_service = fake_services.get("package")
    artifact_path = tmp_path / "test-rock_0.1_risky.rock"
    lifecycle_service = mocker.Mock(requires_repack=False)
    real_get = fake_services.get

    def get_service(service_name: str):
        if service_name == "lifecycle":
            return lifecycle_service
        return real_get(service_name)

    mocker.patch.object(fake_services, "get", side_effect=get_service)
    mock_pack = mocker.patch.object(
        package_service,
        "_pack",
        side_effect=lambda *, name=None, path: path.touch(),
    )

    package_service.set_output_dir(tmp_path)

    command = PackCommand(fake_app_config)
    mocker.patch.object(PackCommand, "_relativize_paths", side_effect=lambda packages, root: packages)

    parsed_args = argparse.Namespace(fetch_service_policy=None)
    command._run_pack(parsed_args, shell_after=False, debug=False)

    assert artifact_path.is_file()
    first_mtime = artifact_path.stat().st_mtime_ns
    emitter.assert_progress(f"Packed {artifact_path.name}", permanent=True)

    state = package_service.read_state()
    assert state.artifact == artifact_path

    command._run_pack(parsed_args, shell_after=False, debug=False)

    assert artifact_path.stat().st_mtime_ns == first_mtime
    mock_pack.assert_called_once()
    emitter.assert_progress("Skipping pack (already ran)")
    emitter.assert_progress(f"Already packed: {artifact_path}", permanent=True)

    state = package_service.read_state()
    assert state.artifact == artifact_path
