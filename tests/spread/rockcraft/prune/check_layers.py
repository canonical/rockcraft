import filecmp
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path


def _get_tarfile_path(sha: str) -> Path:
    """Get the path to the layer file identified by ``sha``."""
    if ":" in sha:
        sha = sha[sha.find(":") + 1 :]

    layers_dir = Path("blobs/sha256")
    return layers_dir / sha


def _get_tar_contents(sha: str):
    """Get a mapping (filename -> TarInfo) for the layer identified by ``sha``."""
    filename = _get_tarfile_path(sha)

    contents = {}
    with tarfile.open(filename) as tar:
        # Filter only the regular files, as that's all we prune.
        members = tar.getmembers()
        for member in members:
            if member.isfile():
                contents[member.name] = member

    return contents


def _get_stats(tarinfo):
    """Get size, permission bits, owner and group from a TarInfo."""
    return tarinfo.size, tarinfo.mode, tarinfo.uid, tarinfo.gid


def _get_tar_file(tarinfo: tarfile.TarInfo, sha: str, dest_dir: Path) -> Path:
    """Extract file indicated by ``tarinfo`` from the layer identified by ``sha``.

    Returns the path to the extracted file.
    """
    filename = _get_tarfile_path(sha)

    with tarfile.open(filename) as tar:
        tar.extract(tarinfo, path=dest_dir)

    return dest_dir / tarinfo.name


rock_name = sys.argv[1]

inspect = subprocess.check_output(
    ["/snap/rockcraft/current/bin/skopeo", "inspect", f"oci-archive:{rock_name}"]
)
as_json = json.loads(inspect)

base_layer_sha = as_json["Layers"][0]
base_layer_contents = _get_tar_contents(base_layer_sha)

lifecycle_layer_sha = as_json["Layers"][1]
lifecycle_contents = _get_tar_contents(lifecycle_layer_sha)

duplicates = set(base_layer_contents).intersection(lifecycle_contents)

for duplicate in duplicates:
    base_tarinfo = base_layer_contents[duplicate]
    base_stats = _get_stats(base_tarinfo)

    lifecycle_tarinfo = lifecycle_contents[duplicate]
    lifecycle_stats = _get_stats(lifecycle_tarinfo)

    # If the filename is present in both layers then it's expected that the size,
    # or ownership, or permissions, or finally contents, are different.

    if base_stats != lifecycle_stats:
        # Different size, ownership or permissions: OK
        continue

    # If we get here we have to check the contents of the files.
    tmp_dir = Path("tmp-diff")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    base_file = _get_tar_file(base_tarinfo, base_layer_sha, tmp_dir / "base")
    lifecycle_file = _get_tar_file(
        lifecycle_tarinfo, lifecycle_layer_sha, tmp_dir / "lifecycle"
    )

    if filecmp.cmp(base_file, lifecycle_file, shallow=False):
        raise RuntimeError(f"File {duplicate} is the same in both layers")
