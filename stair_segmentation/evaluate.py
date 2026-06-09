"""Evaluation metrics and visualization for stair segmentation."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless backend, save figures to disk
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)
from sklearn.metrics import (
    accuracy_score,
    jaccard_score,
    precision_recall_fscore_support,
)

from .generate import LABEL_TREAD, LABEL_RISER, LABEL_OTHER

# Colour map for the 3 classes (green=steppable, red=riser, grey=other).
CLASS_COLORS = {
    LABEL_TREAD: "#2ca02c",
    LABEL_RISER: "#d62728",
    LABEL_OTHER: "#999999",
}
CLASS_LABELS = {LABEL_TREAD: "Tread (steppable)", LABEL_RISER: "Riser", LABEL_OTHER: "Other"}


def tread_metrics(y_true, y_pred) -> dict:
    """Binary one-vs-rest metrics for the steppable (tread) class."""
    t_true = (np.asarray(y_true) == LABEL_TREAD).astype(int)
    t_pred = (np.asarray(y_pred) == LABEL_TREAD).astype(int)
    prec, rec, f1, _ = precision_recall_fscore_support(
        t_true, t_pred, average="binary", zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(t_true, t_pred)),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "iou": float(jaccard_score(t_true, t_pred, zero_division=0)),
    }


def multiclass_accuracy(y_true, y_pred) -> float:
    """Overall 3-class accuracy."""
    return float(accuracy_score(y_true, y_pred))


def metrics_table(results: dict) -> str:
    """Pretty ASCII table of per-method tread metrics."""
    hdr = f"{'Method':<18}{'Acc':>8}{'Prec':>8}{'Recall':>8}{'F1':>8}{'IoU':>8}"
    lines = [hdr, "-" * len(hdr)]
    for name, m in results.items():
        lines.append(
            f"{name:<18}{m['accuracy']:>8.3f}{m['precision']:>8.3f}"
            f"{m['recall']:>8.3f}{m['f1']:>8.3f}{m['iou']:>8.3f}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------
def _scatter3d(ax, points, labels, title, max_pts=8000, seed=0):
    if points.shape[0] > max_pts:
        rng = np.random.default_rng(seed)
        sel = rng.choice(points.shape[0], max_pts, replace=False)
        points, labels = points[sel], labels[sel]
    for cls, color in CLASS_COLORS.items():
        m = labels == cls
        if m.any():
            ax.scatter(points[m, 0], points[m, 1], points[m, 2],
                       s=2, c=color, label=CLASS_LABELS[cls], depthshade=False)
    ax.set_title(title)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_zlabel("z (m)")
    ax.view_init(elev=18, azim=-60)


def plot_before_after(points, y_true, y_pred, method_name, out_path):
    """Side-by-side 3D: ground truth vs predicted segmentation."""
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    _scatter3d(ax1, points, y_true, "Ground truth")
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    _scatter3d(ax2, points, y_pred, f"Segmented: {method_name}")
    handles, labels = ax2.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, markerscale=4)
    fig.suptitle(f"Stair segmentation - {method_name}")
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def plot_side_profile(points, labels, title, out_path, max_pts=12000, seed=1):
    """2D y-z side profile (clearest view of stair structure)."""
    if points.shape[0] > max_pts:
        rng = np.random.default_rng(seed)
        sel = rng.choice(points.shape[0], max_pts, replace=False)
        points, labels = points[sel], labels[sel]
    fig, ax = plt.subplots(figsize=(7, 5))
    for cls, color in CLASS_COLORS.items():
        m = labels == cls
        if m.any():
            ax.scatter(points[m, 1], points[m, 2], s=3, c=color,
                       label=CLASS_LABELS[cls])
    ax.set_xlabel("y (m)  - depth")
    ax.set_ylabel("z (m)  - height")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.legend(markerscale=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def plot_height_histogram(points, peaks, out_path, bins=120):
    """Histogram of z with detected tread peaks marked."""
    z = points[:, 2]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(z, bins=bins, color="#4c72b0", alpha=0.8)
    for pk in peaks:
        ax.axvline(pk, color="#2ca02c", linestyle="--", linewidth=1.5)
    ax.set_xlabel("z (m)  - height")
    ax.set_ylabel("point count")
    ax.set_title(f"Height histogram ({len(peaks)} tread levels detected)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def plot_noise_curve(noise_sigmas, f1s, ious, out_path):
    """F1 / IoU of the tread class vs noise level."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(noise_sigmas, f1s, "o-", label="F1")
    ax.plot(noise_sigmas, ious, "s-", label="IoU")
    ax.set_xlabel("tread height noise sigma_z (m)")
    ax.set_ylabel("score (tread class)")
    ax.set_title("Noise sensitivity")
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def save_json(obj, path):
    Path(path).write_text(json.dumps(obj, indent=2), encoding="utf-8")
