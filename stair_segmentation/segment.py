"""Segmentation methods for stair point clouds.

All methods classify every point into the shared label scheme:
    LABEL_TREAD (0)  steppable horizontal surface
    LABEL_RISER (1)  vertical face
    LABEL_OTHER (2)  edges / noise / outliers

Methods
-------
ransac_segment          : sequential RANSAC plane fitting (manual).
pca_normal_segment      : per-point normal estimation via local PCA.
dbscan_slope_segment    : DBSCAN clustering + per-cluster slope analysis.
height_histogram_segment: height (z) histogram peak analysis (advanced).
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from .generate import LABEL_TREAD, LABEL_RISER, LABEL_OTHER

Z_AXIS = np.array([0.0, 0.0, 1.0])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fit_plane(p3: np.ndarray):
    """Plane through 3 points -> (unit normal, d) with n . x + d = 0."""
    v1 = p3[1] - p3[0]
    v2 = p3[2] - p3[0]
    n = np.cross(v1, v2)
    norm = np.linalg.norm(n)
    if norm < 1e-9:
        return None
    n = n / norm
    d = -n.dot(p3[0])
    return n, d


def _plane_pca(points: np.ndarray):
    """Best-fit plane normal of a set of points via PCA (smallest eigenvector)."""
    c = points.mean(axis=0)
    cov = np.cov((points - c).T)
    w, v = np.linalg.eigh(cov)
    return v[:, 0]  # eigenvector of smallest eigenvalue = surface normal


# ---------------------------------------------------------------------------
# 1. RANSAC plane fitting (manual)
# ---------------------------------------------------------------------------
def _extract_planes(points, remaining, pred, label, want_horizontal,
                    rng, distance_thresh, max_planes, iters, min_inliers,
                    horiz_cos, vert_cos):
    """Orientation-gated sequential RANSAC.

    Only 3-point hypotheses whose normal matches the desired orientation
    (horizontal for treads, vertical for risers) are considered. This stops
    RANSAC from latching onto the oblique "ramp" plane that diagonally
    spans the whole staircase.
    """
    for _ in range(max_planes):
        if remaining.size < min_inliers:
            break
        sub = points[remaining]
        best_inliers = None
        for _ in range(iters):
            idx = rng.choice(sub.shape[0], 3, replace=False)
            plane = _fit_plane(sub[idx])
            if plane is None:
                continue
            n, d = plane
            cos_z = abs(float(n @ Z_AXIS))
            if want_horizontal and cos_z < horiz_cos:
                continue
            if (not want_horizontal) and cos_z > vert_cos:
                continue
            dist = np.abs(sub @ n + d)
            inliers = np.where(dist < distance_thresh)[0]
            if best_inliers is None or inliers.size > best_inliers.size:
                best_inliers = inliers
        if best_inliers is None or best_inliers.size < min_inliers:
            break
        global_inliers = remaining[best_inliers]
        pred[global_inliers] = label
        remaining = np.setdiff1d(remaining, global_inliers, assume_unique=False)
    return remaining


def ransac_segment(points, distance_thresh=0.035, iters=2000,
                   n_treads=4, n_risers=3,
                   min_tread_inliers=2000, min_riser_inliers=300,
                   horiz_cos=0.93, vert_cos=0.25, seed=0):
    """Two-phase RANSAC: horizontal planes -> tread, then vertical -> riser.

    Phase 1 extracts up to ``n_treads`` near-horizontal planes
    (|normal . z| >= horiz_cos) and labels their inliers as treads. A high
    ``min_tread_inliers`` rejects thin horizontal slices that cut through a
    riser (those bands are far smaller than a real tread surface).

    Phase 2 extracts up to ``n_risers`` near-vertical planes
    (|normal . z| <= vert_cos) from the leftovers and labels them risers.
    Everything never claimed by a plane stays LABEL_OTHER.
    """
    rng = np.random.default_rng(seed)
    pred = np.full(points.shape[0], LABEL_OTHER, dtype=int)
    remaining = np.arange(points.shape[0])

    remaining = _extract_planes(
        points, remaining, pred, LABEL_TREAD, True, rng,
        distance_thresh, n_treads, iters, min_tread_inliers, horiz_cos, vert_cos)
    remaining = _extract_planes(
        points, remaining, pred, LABEL_RISER, False, rng,
        distance_thresh, n_risers, iters, min_riser_inliers, horiz_cos, vert_cos)
    return pred


# ---------------------------------------------------------------------------
# 2. PCA + normal vector analysis
# ---------------------------------------------------------------------------
def estimate_normals(points, k=50):
    """Per-point unit normal from PCA over k nearest neighbours."""
    nn = NearestNeighbors(n_neighbors=k).fit(points)
    _, idx = nn.kneighbors(points)
    normals = np.empty_like(points)
    for i, nbrs in enumerate(idx):
        normals[i] = _plane_pca(points[nbrs])
    return normals


def pca_normal_segment(points, k=50, horiz_cos=0.80, vert_cos=0.50,
                       normals=None):
    """Classify points by the tilt of their local surface normal."""
    if normals is None:
        normals = estimate_normals(points, k=k)
    cos_z = np.abs(normals @ Z_AXIS)
    pred = np.full(points.shape[0], LABEL_OTHER, dtype=int)
    pred[cos_z >= horiz_cos] = LABEL_TREAD
    pred[cos_z <= vert_cos] = LABEL_RISER
    return pred


# ---------------------------------------------------------------------------
# 3. DBSCAN clustering + slope analysis
# ---------------------------------------------------------------------------
def dbscan_slope_segment(points, eps=0.08, min_samples=10, min_cluster=300,
                         horiz_cos=0.90, vert_cos=0.35,
                         seed_horiz_cos=0.65, seed_vert_cos=0.60,
                         normals=None, k=50):
    """Orientation-aware Euclidean clustering + per-cluster slope analysis.

    The raw staircase is one connected surface, so position-only DBSCAN
    merges everything into a single cluster. We therefore:

    1. Estimate per-point normals and split points into orientation groups
       (horizontal-normal candidates vs vertical-normal candidates).
    2. Run spatial DBSCAN *within* each group. Because the 4 treads sit at
       distinct heights and the 3 risers at distinct depths, each physical
       surface becomes its own dense cluster, while sparse outliers fall to
       DBSCAN noise (label -1).
    3. Keep clusters above `min_cluster` and confirm their label by the tilt
       (slope) of the cluster's best-fit plane.

    Returns (pred, cluster_ids) where cluster_ids encodes the spatial
    clusters for visualization (-1 = noise/other).
    """
    if normals is None:
        normals = estimate_normals(points, k=k)
    cos_z = np.abs(normals @ Z_AXIS)
    pred = np.full(points.shape[0], LABEL_OTHER, dtype=int)
    cluster_ids = np.full(points.shape[0], -1, dtype=int)

    # Loose per-point seeds gather candidates; the strict cluster-level
    # slope test below makes the final call, so a generous seed widens recall
    # without hurting precision.
    groups = [
        (np.where(cos_z >= seed_horiz_cos)[0], LABEL_TREAD, True),
        (np.where(cos_z <= seed_vert_cos)[0], LABEL_RISER, False),
    ]
    next_id = 0
    for idx, group_label, want_horiz in groups:
        if idx.size < min_cluster:
            continue
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(points[idx])
        for c in np.unique(db.labels_):
            if c == -1:
                continue
            cmask = db.labels_ == c
            if cmask.sum() < min_cluster:
                continue
            members = idx[cmask]
            n = _plane_pca(points[members])
            czc = abs(float(n @ Z_AXIS))
            # Slope confirmation: only label if cluster orientation agrees.
            if want_horiz and czc >= horiz_cos:
                pred[members] = LABEL_TREAD
            elif (not want_horiz) and czc <= vert_cos:
                pred[members] = LABEL_RISER
            cluster_ids[members] = next_id
            next_id += 1
    return pred, cluster_ids


# ---------------------------------------------------------------------------
# 4. Height histogram analysis (advanced)
# ---------------------------------------------------------------------------
def height_histogram_segment(points, bin_width=0.01, band=0.05,
                             smooth=3, min_peak_frac=0.02):
    """Detect tread levels as peaks in the z-histogram.

    Points within +/- `band` of a detected peak are treads; points whose
    height sits in the gap between consecutive tread levels are risers;
    the rest are other.
    """
    z = points[:, 2]
    zmin, zmax = z.min(), z.max()
    n_bins = max(8, int(np.ceil((zmax - zmin) / bin_width)))
    hist, edges = np.histogram(z, bins=n_bins, range=(zmin, zmax))
    centers = 0.5 * (edges[:-1] + edges[1:])

    # Simple moving-average smoothing.
    if smooth > 1:
        kernel = np.ones(smooth) / smooth
        hist_s = np.convolve(hist, kernel, mode="same")
    else:
        hist_s = hist.astype(float)

    thresh = min_peak_frac * hist_s.max()
    peak_z = []
    for i in range(1, len(hist_s) - 1):
        if hist_s[i] >= hist_s[i - 1] and hist_s[i] > hist_s[i + 1] and hist_s[i] >= thresh:
            peak_z.append(centers[i])
    peak_z = _merge_close(peak_z, min_gap=band)

    pred = np.full(points.shape[0], LABEL_OTHER, dtype=int)
    if not peak_z:
        return pred, []

    # Distance from each point's z to the nearest peak.
    peak_arr = np.array(peak_z)
    d_to_peak = np.abs(z[:, None] - peak_arr[None, :]).min(axis=1)
    pred[d_to_peak <= band] = LABEL_TREAD

    # Between adjacent tread levels -> riser.
    if len(peak_arr) >= 2:
        lo, hi = peak_arr.min(), peak_arr.max()
        between = (z > lo + band) & (z < hi - band) & (pred != LABEL_TREAD)
        pred[between] = LABEL_RISER
    return pred, peak_z


def _merge_close(values, min_gap):
    """Merge sorted scalar peaks that are closer than min_gap."""
    if not values:
        return []
    values = sorted(values)
    merged = [values[0]]
    for v in values[1:]:
        if v - merged[-1] < min_gap:
            merged[-1] = 0.5 * (merged[-1] + v)
        else:
            merged.append(v)
    return merged


# Registry used by the driver / evaluation for uniform iteration.
METHODS = {
    "RANSAC": lambda pts: ransac_segment(pts),
    "PCA-Normals": lambda pts: pca_normal_segment(pts),
    "DBSCAN-Slope": lambda pts: dbscan_slope_segment(pts)[0],
    "Height-Histogram": lambda pts: height_histogram_segment(pts)[0],
}
