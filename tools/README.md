# Accuracy–throughput Pareto plot

Run from the repository root using the workshop environment:

```bash
workskop_material/env/bin/python workskop_material/tools/plot_pareto.py
```

The script joins `eval/output/RESULTS.json` and `benchmarks/output/RESULTS.json`
by variant name. It plots benchmark FPS on the horizontal axis and COCO
mAP@0.50:0.95 (%) on the vertical axis. Both objectives are maximized.
A point is dominated if another point is at least as good on both axes and
strictly better on at least one. Equal points both remain on the frontier.

Outputs are saved in `tools/output/`:

- `pareto_fps_map.png`: ready to use in slides.
- `pareto_fps_map.csv`: joined values and Pareto membership, preserving precision.


Paths default relative to the script, so it can run from any working directory.
Override inputs or output location with:

```bash
python plot_pareto.py --eval-results /path/to/eval/RESULTS.json \
  --benchmark-results /path/to/benchmarks/RESULTS.json \
  --output-dir /path/to/plots
```
