"""Point cloud generation for a 4-step staircase.

Implements the mathematical model from the project brief:

Tread (horizontal, steppable) for step i = 0..N-1:
    x ~ Uniform(0, width)
    y ~ Uniform(i*depth, (i+1)*depth)
    z = i*height + eps_z,   eps_z ~ N(0, sigma_z^2)

Riser (vertical) for step i = 1..N-1:
    x ~ Uniform(0, width)
    y = i*depth + eps_y,    eps_y ~ N(0, sigma_y^2)
    z ~ Uniform((i-1)*height, i*height)

Plus uniform random outliers and small isotropic LiDAR jitter.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Ground-truth / prediction label scheme (shared everywhere).
LABEL_TREAD = 0   # steppable horizontal surface (hijau / green)
LABEL_RISER = 1   # vertical face          (merah / red)
LABEL_OTHER = 2   # edges, outliers, noise (abu-abu / grey)

LABEL_NAMES = {LABEL_TREAD: "tread", LABEL_RISER: "riser", LABEL_OTHER: "other"}


@dataclass
class StairParams:
    """Geometry and sampling configuration for the synthetic staircase."""

    n_steps: int = 4
    width: float = 2.5          # x-axis extent (m), spec: 2.0-3.0
    depth: float = 0.30         # tread depth along y (m), spec: 0.25-0.35
    height: float = 0.18        # rise per step along z (m), spec: 0.15-0.20

    n_tread: int = 3200         # points per tread surface
    n_riser: int = 1600         # points per riser surface
    outlier_frac: float = 0.04  # fraction of total reserved for outliers

    sigma_z: float = 0.02       # tread height noise (m), from spec
    sigma_y: float = 0.02       # riser depth noise (m)
    lidar_jitter: float = 0.005  # extra isotropic per-axis jitter (m)

    seed: int = 42

    @property
    def total_height(self) -> float:
        return self.n_steps * self.height

    @property
    def total_depth(self) -> float:
        return self.n_steps * self.depth


def generate_stair_cloud(params: StairParams | None = None):
    """Generate the staircase point cloud and ground-truth labels.

    Returns
    -------
    points : (N, 3) float array  -- XYZ coordinates in metres.
    labels : (N,) int array      -- one of LABEL_TREAD / LABEL_RISER / LABEL_OTHER.
    """
    p = params or StairParams()
    rng = np.random.default_rng(p.seed)

    pts_chunks: list[np.ndarray] = []
    lbl_chunks: list[np.ndarray] = []

    # --- Treads: one flat surface per step ------------------------------
    for i in range(p.n_steps):
        n = p.n_tread
        x = rng.uniform(0.0, p.width, n)
        y = rng.uniform(i * p.depth, (i + 1) * p.depth, n)
        z = i * p.height + rng.normal(0.0, p.sigma_z, n)
        pts_chunks.append(np.column_stack([x, y, z]))
        lbl_chunks.append(np.full(n, LABEL_TREAD, dtype=int))

    # --- Risers: vertical face at the front edge of steps 1..N-1 --------
    for i in range(1, p.n_steps):
        n = p.n_riser
        x = rng.uniform(0.0, p.width, n)
        y = i * p.depth + rng.normal(0.0, p.sigma_y, n)
        z = rng.uniform((i - 1) * p.height, i * p.height, n)
        pts_chunks.append(np.column_stack([x, y, z]))
        lbl_chunks.append(np.full(n, LABEL_RISER, dtype=int))

    points = np.vstack(pts_chunks)
    labels = np.concatenate(lbl_chunks)

    # --- Outliers: uniform random points inside an inflated bbox --------
    n_struct = points.shape[0]
    n_out = int(round(p.outlier_frac / (1.0 - p.outlier_frac) * n_struct))
    if n_out > 0:
        margin = 0.1
        ox = rng.uniform(-margin, p.width + margin, n_out)
        oy = rng.uniform(-margin, p.total_depth + margin, n_out)
        oz = rng.uniform(-margin, p.total_height + margin, n_out)
        out_pts = np.column_stack([ox, oy, oz])
        points = np.vstack([points, out_pts])
        labels = np.concatenate([labels, np.full(n_out, LABEL_OTHER, dtype=int)])

    # --- Global LiDAR jitter on every point -----------------------------
    if p.lidar_jitter > 0:
        points = points + rng.normal(0.0, p.lidar_jitter, points.shape)

    # Shuffle so methods cannot exploit ordering.
    perm = rng.permutation(points.shape[0])
    return points[perm], labels[perm]


def summarize(labels: np.ndarray) -> dict:
    """Return per-class counts and total for a label array."""
    unique, counts = np.unique(labels, return_counts=True)
    by_class = {LABEL_NAMES[int(u)]: int(c) for u, c in zip(unique, counts)}
    by_class["total"] = int(labels.shape[0])
    return by_class


if __name__ == "__main__":
    pts, lbl = generate_stair_cloud()
    print("Generated point cloud:", summarize(lbl))
    print("bbox min:", pts.min(0).round(3), "max:", pts.max(0).round(3))
