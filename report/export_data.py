"""Export numeric data for native pgfplots figures in the paper.

Writes whitespace-delimited .dat files into report/data/:
  hist.dat     : z-bin centers and point counts (height histogram)
  peaks.dat    : detected tread-level z positions (vertical markers)
  noise.dat    : sigma_z vs F1 / IoU (noise sensitivity)
  metrics.dat  : per-method tread-class metrics (bar chart / table source)
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

from stair_segmentation.generate import StairParams, generate_stair_cloud
from stair_segmentation import segment as seg

OUT = Path("report/data")
OUT.mkdir(parents=True, exist_ok=True)

# --- Height histogram + detected peaks ------------------------------------
params = StairParams()
points, labels = generate_stair_cloud(params)
z = points[:, 2]
counts, edges = np.histogram(z, bins=90)
centers = 0.5 * (edges[:-1] + edges[1:])
with open(OUT / "hist.dat", "w", encoding="utf-8") as f:
    f.write("z count\n")
    for c, n in zip(centers, counts):
        f.write(f"{c:.4f} {n}\n")

_, peaks = seg.height_histogram_segment(points)
with open(OUT / "peaks.dat", "w", encoding="utf-8") as f:
    f.write("z\n")
    for p in peaks:
        f.write(f"{p:.4f}\n")

# --- Noise sweep + per-method metrics (from metrics.json) -----------------
m = json.load(open("metrics.json", encoding="utf-8"))
sw = m["noise_sweep"]
with open(OUT / "noise.dat", "w", encoding="utf-8") as f:
    f.write("sigma f1 iou\n")
    for s, f1, iou in zip(sw["sigma_z"], sw["f1"], sw["iou"]):
        f.write(f"{s:.3f} {f1:.4f} {iou:.4f}\n")

order = ["RANSAC", "PCA-Normals", "DBSCAN-Slope", "Height-Histogram"]
tm = m["tread_metrics"]
with open(OUT / "metrics.dat", "w", encoding="utf-8") as f:
    f.write("method acc prec rec f1 iou\n")
    for name in order:
        d = tm[name]
        label = name.replace("-", "")
        f.write(f"{label} {d['accuracy']:.4f} {d['precision']:.4f} "
                f"{d['recall']:.4f} {d['f1']:.4f} {d['iou']:.4f}\n")

print("Wrote", *[p.name for p in OUT.glob('*.dat')])
print("peaks:", [round(p, 3) for p in peaks])
