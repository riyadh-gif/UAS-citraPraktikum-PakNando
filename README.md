# Steppable-Surface Segmentation in Simulated Staircase Point Clouds

Mini project for *Sensor dan Sistem Pengolahan Sinyal* (UAS). Generates a
4-step staircase point cloud from a parametric mathematical model, segments
the **steppable surfaces (treads)** from **risers** and **other/noise**, and
evaluates four classical geometric methods.

## Methods
1. **RANSAC plane fitting** (orientation-gated, two-phase) — horizontal planes → tread, vertical → riser.
2. **PCA + normal-vector analysis** — per-point normals via local PCA, classified by verticality.
3. **DBSCAN + slope analysis** — orientation pre-split, spatial clustering, per-cluster slope confirmation.
4. **Height-histogram analysis** (advanced) — z-histogram peaks = tread levels.

## Results (tread class, one-vs-rest)
| Method | Acc | Prec | Rec | F1 | IoU |
|---|---|---|---|---|---|
| RANSAC | 0.681 | 0.714 | 0.904 | 0.798 | 0.664 |
| PCA-Normals | 0.901 | 0.954 | 0.901 | 0.927 | 0.864 |
| **DBSCAN-Slope** | **0.920** | 0.936 | 0.949 | **0.943** | **0.892** |
| Height-Histogram | 0.827 | 0.809 | 0.984 | 0.888 | 0.799 |

Cloud: 18,333 points (12,800 tread / 4,800 riser / 733 other).

## Layout
```
stair_segmentation/      # package: generate.py, segment.py, evaluate.py
main.py                  # end-to-end: generate -> segment -> evaluate -> figures + metrics.json
mini_project.ipynb       # executed submission notebook
figures/                 # 3D/2D visualisations (PNG)
metrics.json             # all reported numbers
report/                  # IEEE conference paper (LaTeX)
  main.tex, sections/, data/, refs.bib, main.pdf
  export_data.py         # emits report/data/*.dat for pgfplots
research/                # citation harvest + outline + peer-review notes
requirements.txt
```

## Setup
```powershell
py -m pip install -r requirements.txt
```
(Python 3.x via the `py` launcher on Windows; `open3d` is not required.)

## Run
```powershell
# end-to-end pipeline (prints metrics, writes figures/ + metrics.json)
py main.py

# regenerate notebook (optional)
py build_notebook.py
```

## Build the paper
```powershell
cd report
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
Produces `report/main.pdf` (7 pages, IEEE conference format, 20 references).
Requires a TeX distribution with `IEEEtran`, `pgfplots`, and `booktabs`.

## Notes
- All randomness is seeded for reproducibility.
- Figures: 2D plots (histogram, noise curve, metric bars) are native pgfplots;
  3D scatter plots are matplotlib PNGs.
