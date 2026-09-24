"""Expose the pinned container's SNPE inspection tools to the host analyzer."""
import os
from pathlib import Path
import subprocess
import sys

IMAGE = "ghcr.io/luxonis/modelconverter-rvc4@sha256:372b4eb95febd07519f606baa00836e90751a010a8aeb075b4dfd554dbbc9cbe"


def main(tool):
    if tool not in {"snpe-dlc-info", "snpe-diagview"}:
        raise SystemExit(f"Unsupported SNPE tool: {tool}")
    workshop = Path(__file__).resolve().parents[2]
    cwd = Path.cwd().resolve()
    if not cwd.is_relative_to(workshop):
        raise SystemExit(f"Run this tool from within {workshop}")
    command = [
        "docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{workshop}:{workshop}", "-v", "/tmp:/tmp",
        "-w", str(cwd), "--entrypoint", "/bin/bash", IMAGE,
        "-c", 'source /opt/snpe/bin/envsetup.sh >/dev/null; exec "$@"',
        "snpe-wrapper", tool, *sys.argv[1:],
    ]
    try:
        return subprocess.call(command)
    except FileNotFoundError:
        raise SystemExit("Docker is required and must be on PATH.") from None
