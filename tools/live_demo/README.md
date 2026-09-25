# Live YOLO demo

Run a local YOLO NN archive on an OAK camera with DepthAI v3. The preview shows
bounding boxes, class labels, confidence scores, and average inference FPS.

## Setup and run

Requires a connected OAK camera and a compatible YOLO NN archive (`.tar.xz`).
Run this using the requirements from `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python3 main.py --model /path/to/model.tar.xz
```

Use an archive compiled for your OAK device, with YOLO parser metadata.

To select a device by IP, add `-d` (or `--device`); omit it for automatic selection:

```bash
python3 main.py --model /path/to/model.tar.xz -d 192.168.1.100
```

## Controls

Focus the preview window before pressing keys:

| Key | Action |
| --- | --- |
| `w` / `s` | Increase / decrease confidence threshold by 0.05 |
| `e` / `d` | Increase / decrease IoU threshold by 0.05 |
| `q` | Quit |

Thresholds stay within 0–1; updated values are printed in the terminal.
