"""Plot measured throughput versus COCO mAP, joining workshop result summaries."""

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKSHOP = Path(__file__).resolve().parents[1]


def indexed(rows, key):
    result = {}
    for row in rows:
        name = row[key]
        if name in result:
            raise ValueError(f"Duplicate result: {name}")
        result[name] = row
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-results", type=Path, default=WORKSHOP / "eval/output/RESULTS.json"
    )
    parser.add_argument(
        "--benchmark-results",
        type=Path,
        default=WORKSHOP / "benchmarks/output/RESULTS.json",
    )
    parser.add_argument("--output-dir", type=Path, default=WORKSHOP / "tools/output")
    args = parser.parse_args()
    evaluation = json.loads(args.eval_results.read_text())
    benchmark = json.loads(args.benchmark_results.read_text())
    accuracy = indexed(evaluation["results"], "variant")
    speed = indexed(benchmark["results"], "model")
    for name in sorted(accuracy.keys() ^ speed.keys()):
        print(f"Skipping {name}: missing accuracy or benchmark result.")
    points = []
    for name in sorted(accuracy.keys() & speed.keys()):
        if name == 'int8_wrong_calibration':
            continue
        metrics = [
            m["values"]
            for m in accuracy[name]["metrics"]
            if m["name"] == "BboxMeanAveragePrecision"
        ]
        if len(metrics) != 1:
            raise ValueError(f"{name}: expected one BboxMeanAveragePrecision metric")
        ap = float(metrics[0]["AP"])
        fps = float(speed[name]["values"]["fps"])
        if (
            not math.isfinite(ap)
            or not 0 <= ap <= 1
            or not math.isfinite(fps)
            or fps <= 0
        ):
            raise ValueError(f"{name}: invalid AP or FPS")
        points.append({"variant": name, "fps": fps, "map_percent": ap * 100})
    if not points:
        raise ValueError("No variants have both accuracy and throughput results.")
    points.sort(key=lambda p: (p["fps"], p["variant"]))
    for i, p in enumerate(points, 1):
        p["id"] = i
        p["pareto_optimal"] = not any(
            q["fps"] >= p["fps"]
            and q["map_percent"] >= p["map_percent"]
            and (q["fps"] > p["fps"] or q["map_percent"] > p["map_percent"])
            for q in points
        )
    frontier = [p for p in points if p["pareto_optimal"]]
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    labels = {
        'fp16_unoptimized': 'FP16 unoptimized',
        'fp16_optimized': 'FP16 optimized',
        'int8_int16': 'INT8 / INT16 (W8A16)',
        'int8_per_channel': 'INT8 per-channel',
        'int8_per_tensor': 'INT8 per-tensor',
    }
    for i, p in enumerate(points):
        ax.scatter(p['fps'], p['map_percent'], s=90, color=f'C{i % 10}',
                   label=labels.get(p['variant'], p['variant']), zorder=3)
    ax.plot([p['fps'] for p in frontier], [p['map_percent'] for p in frontier],
            '--', color='0.45', linewidth=1.5, label='Pareto frontier', zorder=1)
    ax.set_title(f"{benchmark.get('model_family', 'Model')}: accuracy vs. throughput")
    ax.set_xlabel('Throughput (FPS)')
    ax.set_ylabel('COCO mAP@0.50:0.95 (%)')
    ax.grid(alpha=0.2)
    ax.set_axisbelow(True)
    ax.margins(x=0.08, y=0.15)
    ax.legend(loc='lower left', frameon=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / 'pareto_fps_map.png'
    fig.savefig(path, dpi=180, facecolor='white')
    print(f'Wrote {path}')
    plt.close(fig)
    with (args.output_dir / "pareto_fps_map.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["id", "variant", "fps", "map_percent", "pareto_optimal"]
        )
        writer.writeheader()
        writer.writerows(points)
    print("Pareto frontier: " + ", ".join(p["variant"] for p in frontier))


if __name__ == "__main__":
    main()
