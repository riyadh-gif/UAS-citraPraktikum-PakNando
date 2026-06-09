"""End-to-end driver: generate -> segment -> evaluate -> save figures/metrics.

Run:  py main.py
Outputs: figures/*.png  and  metrics.json
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from stair_segmentation.generate import (
    StairParams,
    generate_stair_cloud,
    summarize,
)
from stair_segmentation import segment as seg
from stair_segmentation import evaluate as ev

FIG_DIR = Path("figures")


def run_all_methods(points, normals=None):
    """Run the 4 segmentation methods, return {name: predicted labels}."""
    preds = {}
    preds["RANSAC"] = seg.ransac_segment(points)
    preds["PCA-Normals"] = seg.pca_normal_segment(points, normals=normals)
    preds["DBSCAN-Slope"] = seg.dbscan_slope_segment(points, normals=normals)[0]
    hist_pred, peaks = seg.height_histogram_segment(points)
    preds["Height-Histogram"] = hist_pred
    return preds, peaks


def noise_sensitivity(base: StairParams, sigmas):
    """Re-generate at increasing tread-noise sigma; segment with PCA-Normals."""
    f1s, ious = [], []
    for s in sigmas:
        p = StairParams(**{**base.__dict__, "sigma_z": float(s)})
        pts, lbl = generate_stair_cloud(p)
        pred = seg.pca_normal_segment(pts)
        m = ev.tread_metrics(lbl, pred)
        f1s.append(m["f1"])
        ious.append(m["iou"])
    return list(map(float, f1s)), list(map(float, ious))


def main():
    FIG_DIR.mkdir(exist_ok=True)
    params = StairParams()

    print("== Generating point cloud ==")
    points, labels = generate_stair_cloud(params)
    counts = summarize(labels)
    print("counts:", counts)
    assert 15000 <= counts["total"] <= 25000, "total points out of spec range"

    print("\n== Estimating normals (shared by PCA method) ==")
    normals = seg.estimate_normals(points, k=50)

    print("== Running segmentation methods ==")
    preds, peaks = run_all_methods(points, normals=normals)

    results = {name: ev.tread_metrics(labels, pred) for name, pred in preds.items()}
    overall = {name: ev.multiclass_accuracy(labels, pred) for name, pred in preds.items()}

    print("\n== Tread-class metrics ==")
    print(ev.metrics_table(results))
    print("\n3-class overall accuracy:",
          {k: round(v, 3) for k, v in overall.items()})

    print("\n== Saving figures ==")
    ev.plot_side_profile(points, labels, "Ground-truth side profile (y-z)",
                         FIG_DIR / "profile_ground_truth.png")
    for name, pred in preds.items():
        slug = name.lower().replace("-", "_")
        ev.plot_before_after(points, labels, pred, name,
                             FIG_DIR / f"seg_{slug}.png")
    ev.plot_side_profile(points, preds["PCA-Normals"],
                         "PCA-Normals side profile (y-z)",
                         FIG_DIR / "profile_pca.png")
    ev.plot_height_histogram(points, peaks, FIG_DIR / "height_histogram.png")

    print("== Noise sensitivity sweep ==")
    sigmas = [0.01, 0.02, 0.03, 0.04, 0.05, 0.07]
    f1s, ious = noise_sensitivity(params, sigmas)
    ev.plot_noise_curve(sigmas, f1s, ious, FIG_DIR / "noise_sensitivity.png")

    metrics_out = {
        "geometry": {
            "n_steps": params.n_steps, "width": params.width,
            "depth": params.depth, "height": params.height,
        },
        "point_counts": counts,
        "tread_metrics": results,
        "overall_accuracy": overall,
        "height_peaks": [round(float(p), 4) for p in peaks],
        "noise_sweep": {"sigma_z": sigmas, "f1": f1s, "iou": ious},
    }
    ev.save_json(metrics_out, "metrics.json")
    print("\nWrote metrics.json and figures/*.png")


if __name__ == "__main__":
    main()
