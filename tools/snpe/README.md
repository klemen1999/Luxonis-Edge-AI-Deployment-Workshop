# Optional SNPE inspection wrappers

These tools are only needed to rerun model analysis. You can instead use the
prepared analysis results and HTML plots from Google Drive, as described in the
[analysis README](../../analysis/README.md), without setting up these tools.

These executables let `modelconverter analyze` call `snpe-dlc-info` and
`snpe-diagview` without installing the Qualcomm SDK on the host. They run the
SNPE 2.41 tools inside the pinned ModelConverter RVC4 Docker image specified in
`run_snpe.py`.

From the workshop root, with the workshop Python environment active:

```bash
export PATH="$PWD/tools/snpe:$PATH"
snpe-dlc-info --help
snpe-diagview --help
```

Docker must be running and accessible to your user. The first invocation may
pull the image. Repeat the PATH setup in each new shell, then follow the
[analysis commands](../../analysis/README.md).

Run from within the workshop folder. The wrappers mount that folder and `/tmp`
at their original absolute paths so the analyzer can pass file paths into the
container. Keep input/output files within those locations. Files are written
with your host user ID. Tool arguments and exit codes are passed through.
