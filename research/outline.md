# Paper Outline & Shared Specs — Stair Point-Cloud Segmentation

**Target:** 8-page IEEE conference paper (IEEEtran, `[conference]`), English, international submission. Each writer produces ONE file `report/sections/<name>.tex` containing exactly one `\section{...}` (+ subsections). NO preamble, NO `\begin{document}`, NO bibliography — those live in `main.tex`.

## Hard rules for all writers
- **Language:** formal academic English. Past tense for what we did/observed; present for general truths.
- **Citations:** use ONLY `\cite` keys listed in `research/citations.md`. NEVER invent keys. Cite as `\cite{key}` or `\cite{k1,k2}`. Do not write "Ref." or "[1]" manually.
- **Numbers:** use EXACT values from `metrics.json` / table below. Do not round differently.
- **Notation (consistent):** point $\mathbf{x}\in\R^3$; unit surface normal $\nvec$; vertical axis $\zhat$; staircase params width $w=2.5$\,m, tread depth $d=0.30$\,m, step height $h=0.18$\,m, $N=4$ steps; height noise $\sigma_z=0.02$\,m. Macros `\nvec \zhat \R` are predefined in main.tex.
- **Cross-refs:** `\eqref{}` for equations, `Fig.~\ref{}` for figures, `Table~\ref{}` for tables, `Algorithm~\ref{}`. Use the labels defined below so they resolve across files.
- **Floats:** only the OWNER section defines each float (labels below). Other sections may `\ref` them.
- IEEE style: figure captions BELOW, table captions ABOVE. Keep it tight — total budget is 8 pages.

## The three classes
LABEL 0 = **tread** (steppable horizontal surface), LABEL 1 = **riser** (vertical face), LABEL 2 = **other** (edges/noise/outliers). Primary class of interest = tread.

## Exact results (tread class, one-vs-rest)
| Method | Acc | Prec | Rec | F1 | IoU |
|---|---|---|---|---|---|
| RANSAC | 0.681 | 0.714 | 0.904 | 0.798 | 0.664 |
| PCA-Normals | 0.901 | 0.954 | 0.901 | 0.927 | 0.864 |
| DBSCAN-Slope | 0.920 | 0.936 | 0.949 | 0.943 | 0.892 |
| Height-Histogram | 0.827 | 0.809 | 0.984 | 0.888 | 0.799 |

3-class overall accuracy: RANSAC 0.667, PCA 0.834, DBSCAN 0.909, Histogram 0.816.
Cloud: 18,333 pts (12,800 tread / 4,800 riser / 733 other). Detected tread levels (Height-Hist peaks): z ≈ {0.00, 0.18, 0.36, 0.54} m.
Noise sweep (σ_z → F1 / IoU): 0.01→0.956/0.915, 0.02→0.927/0.864, 0.03→0.857/0.750, 0.04→0.758/0.610, 0.05→0.667/0.500, 0.07→0.543/0.373.

## Figure/table inventory (labels + OWNER + ready code)
All `\includegraphics` resolve via graphicspath; pgfplots `table{data/...}` resolve from `report/`.

- `eq:tread`, `eq:riser` — generation model (OWNER: method)
- `eq:plane`, `eq:cov` — RANSAC plane distance + PCA covariance (OWNER: method)
- `alg:pipeline` — Algorithm block (OWNER: method)
- `tab:metrics` — metrics table (OWNER: evaluation)
- `fig:profile` — PNG ground-truth side profile (OWNER: evaluation)
- `fig:seg3d` — PNG 3D DBSCAN before/after (OWNER: evaluation)
- `fig:hist` — pgfplots height histogram (OWNER: evaluation)
- `fig:noise` — pgfplots noise curve (OWNER: evaluation)
- `fig:bars` — pgfplots per-method F1/IoU bars (OWNER: evaluation)

### Ready-to-paste float code (paste verbatim, write prose around)

**Generation equations (method):**
```
\begin{equation}\label{eq:tread}
\begin{cases}
x \sim \mathcal{U}(0,\,w) \\
y \sim \mathcal{U}(i d,\,(i{+}1) d) \\
z = i h + \epsilon_z,\quad \epsilon_z \sim \mathcal{N}(0,\sigma_z^2)
\end{cases}
\end{equation}
\begin{equation}\label{eq:riser}
\begin{cases}
x \sim \mathcal{U}(0,\,w) \\
y = i d + \epsilon_y,\quad \epsilon_y \sim \mathcal{N}(0,\sigma_y^2) \\
z \sim \mathcal{U}((i{-}1) h,\, i h)
\end{cases}
\end{equation}
```

**RANSAC distance + PCA covariance (method):**
```
\begin{equation}\label{eq:plane}
d(\mathbf{x}) = |\,\nvec^\top \mathbf{x} + b\,|,\qquad
\mathcal{I} = \{\mathbf{x} : d(\mathbf{x}) < \tau\}
\end{equation}
\begin{equation}\label{eq:cov}
\mathbf{C}_p = \frac{1}{k}\sum_{j\in\mathcal{N}_k(p)}
(\mathbf{x}_j-\bar{\mathbf{x}})(\mathbf{x}_j-\bar{\mathbf{x}})^\top,\quad
\nvec_p = \mathbf{v}_{\min}(\mathbf{C}_p)
\end{equation}
```
Orientation gate: horizontal if $|\nvec^\top\zhat|\ge 0.93$ (tread); vertical if $|\nvec^\top\zhat|\le 0.25$ (riser). RANSAC $\tau=0.035$\,m; PCA $k=50$.

**Algorithm (method):**
```
\begin{algorithm}[t]
\caption{Orientation-aware segmentation (generic)}\label{alg:pipeline}
\begin{algorithmic}[1]
\STATE estimate per-point normals $\nvec_p$ via PCA over $k$ neighbours \eqref{eq:cov}
\STATE split points into horizontal / vertical orientation groups
\STATE cluster or fit planes within each group
\STATE confirm each region by its plane tilt $|\nvec^\top\zhat|$
\STATE label tread / riser / other
\end{algorithmic}
\end{algorithm}
```

**Metrics table (evaluation):**
```
\begin{table}[t]
\caption{Tread-class segmentation metrics (one-vs-rest). Best per column in bold.}
\label{tab:metrics}
\centering
\begin{tabular}{lccccc}
\toprule
Method & Acc & Prec & Rec & F1 & IoU \\
\midrule
RANSAC          & 0.681 & 0.714 & 0.904 & 0.798 & 0.664 \\
PCA-Normals     & 0.901 & \textbf{0.954} & 0.901 & 0.927 & 0.864 \\
DBSCAN-Slope    & \textbf{0.920} & 0.936 & 0.949 & \textbf{0.943} & \textbf{0.892} \\
Height-Histogram& 0.827 & 0.809 & \textbf{0.984} & 0.888 & 0.799 \\
\bottomrule
\end{tabular}
\end{table}
```

**PNG figures (evaluation):**
```
\begin{figure}[t]\centering
\includegraphics[width=0.95\columnwidth]{profile_ground_truth.png}
\caption{Side profile ($y$--$z$) of the ground-truth cloud: green = tread, red = riser, grey = other.}
\label{fig:profile}
\end{figure}

\begin{figure}[t]\centering
\includegraphics[width=\columnwidth]{seg_dbscan_slope.png}
\caption{3D segmentation by DBSCAN with slope analysis (right) vs.\ ground truth (left).}
\label{fig:seg3d}
\end{figure}
```

**Height histogram (evaluation, pgfplots):**
```
\begin{figure}[t]\centering
\begin{tikzpicture}
\begin{axis}[width=\columnwidth,height=4.2cm,xlabel={$z$ (m)},ylabel={count},
  ymin=0,xmin=-0.1,xmax=0.65,enlarge x limits=false,tick label style={font=\footnotesize}]
\addplot[draw=blue!60!black,fill=blue!25] table[x=z,y=count]{data/hist.dat} \closedcycle;
\foreach \px in {0.004,0.183,0.362,0.541}{
  \draw[green!55!black,dashed,thick] (axis cs:\px,0) -- (axis cs:\px,560);}
\end{axis}
\end{tikzpicture}
\caption{Height histogram of $z$; dashed lines mark the four detected tread levels.}
\label{fig:hist}
\end{figure}
```

**Noise curve (evaluation, pgfplots):**
```
\begin{figure}[t]\centering
\begin{tikzpicture}
\begin{axis}[width=\columnwidth,height=4.4cm,xlabel={$\sigma_z$ (m)},
  ylabel={tread-class score},ymin=0,ymax=1,legend pos=south west,
  grid=major,tick label style={font=\footnotesize}]
\addplot[blue,mark=*] table[x=sigma,y=f1]{data/noise.dat}; \addlegendentry{F1}
\addplot[red,mark=square*] table[x=sigma,y=iou]{data/noise.dat}; \addlegendentry{IoU}
\end{axis}
\end{tikzpicture}
\caption{Tread-class F1 and IoU versus height noise $\sigma_z$ (PCA-Normals).}
\label{fig:noise}
\end{figure}
```

**Per-method bars (evaluation, pgfplots):**
```
\begin{figure}[t]\centering
\begin{tikzpicture}
\begin{axis}[width=\columnwidth,height=4.6cm,ybar,bar width=6pt,ymin=0,ymax=1,
  symbolic x coords={RANSAC,PCANormals,DBSCANSlope,HeightHistogram},
  xtick=data,xticklabel style={rotate=20,anchor=east,font=\footnotesize},
  ylabel={score},legend pos=south east,enlarge x limits=0.15]
\addplot table[x=method,y=f1]{data/metrics.dat}; \addlegendentry{F1}
\addplot table[x=method,y=iou]{data/metrics.dat}; \addlegendentry{IoU}
\end{axis}
\end{tikzpicture}
\caption{Per-method tread-class F1 and IoU.}
\label{fig:bars}
\end{figure}
```

## Per-section briefs

### 1. Introduction (`intro.tex`, ~0.9 col) — OWNER: writer-intro
Motivate stair perception for stair-climbing/following robots and assistive devices. Steppable-surface (tread) detection is safety-critical; mislabeling a riser as steppable causes foothold failure. State the gap: deep methods need large labeled data and lack controlled, reproducible benchmarks for this specific sub-problem; classical geometric methods are fast/interpretable but under-compared on stairs. Contributions (bullet/enumerate): (i) a parametric, fully labeled staircase point-cloud generator with LiDAR noise + outliers; (ii) a unified 3-class formulation and implementation of four classical methods (RANSAC, PCA-normals, DBSCAN+slope, height-histogram); (iii) quantitative comparison + noise-sensitivity study; (iv) safety discussion for robotic traversal. Cite: matsumura2022deep, marion2017director, belter2016adaptive, stelzer2012stereo, agarwal2022legged, chavezgarcia2017learning, qi2016pointnet, gomes2023survey. End with paper roadmap sentence.

### 2. Related Work (`related.tex`, ~1.2 col) — OWNER: writer-related
Thematic synthesis (NOT a list), grouped subsections:
- *Geometric plane segmentation:* RANSAC and variants for planar structure — li2017improved, jalal2021rgb, zhou2021lsam.
- *Normal estimation & surface analysis:* huang2009consolidation, castillo2013point.
- *Clustering & region growing:* zhou2024identification (DBSCAN), xu2021object (Euclidean clustering), luo2021supervoxel (region growing).
- *Ground/LiDAR segmentation:* gomes2023survey.
- *Learning-based segmentation:* qi2016pointnet, sarker2024comprehensive, li2022hybridcr, zhao2020few, he2023prototype — note data hunger / lack of interpretability.
- *Robotic stair & terrain perception:* matsumura2022deep, marion2017director, belter2016adaptive, stelzer2012stereo, agarwal2022legged, chavezgarcia2017learning.
Close with the gap our paper fills (controlled benchmark + apples-to-apples classical comparison with ground-truth labels).

### 3. Proposed Method (`method.tex`, ~2.4 col) — OWNER: writer-method
Subsections: (A) Problem formulation + 3-class scheme. (B) Parametric data generation — present \eqref{eq:tread},\eqref{eq:riser}, outliers (~4%), LiDAR jitter $\mathcal{N}(0,0.005^2)$, total 18,333 pts. (C) Four methods, each a short subsection with the key math:
  - *RANSAC plane fitting* — \eqref{eq:plane}; two-phase orientation-gated (horizontal→tread then vertical→riser); note the oblique "ramp" failure (global stair plane has $|\nvec^\top\zhat|\approx0.86$) motivating the gate; high min-inlier count rejects thin riser slices. Cite li2017improved, jalal2021rgb.
  - *PCA normal analysis* — \eqref{eq:cov}, smallest-eigenvector normal, $k=50$; classify by $|\nvec^\top\zhat|$ thresholds (tread $\ge0.80$, riser $\le0.50$). Cite huang2009consolidation, castillo2013point.
  - *DBSCAN + slope* — orientation pre-split then spatial DBSCAN ($\varepsilon=0.08$) within each group so each physical surface is one cluster and outliers fall to noise; per-cluster slope confirmation. Cite zhou2024identification, luo2021supervoxel.
  - *Height-histogram (advanced)* — peaks of $z$-histogram = tread levels; bands between = riser.
  Present Algorithm~\ref{alg:pipeline}. Keep derivations compact.

### 4. Evaluation (`evaluation.tex`, ~2.2 col) — OWNER: writer-evaluation
Subsections: (A) Setup — dataset stats, metrics defined (Accuracy, Precision, Recall, F1, IoU = Jaccard) for tread one-vs-rest; seed/reproducibility. (B) Results — present Table~\ref{tab:metrics}; reference Fig.~\ref{fig:profile}, Fig.~\ref{fig:seg3d}, Fig.~\ref{fig:hist}, Fig.~\ref{fig:bars}; narrate ranking (DBSCAN best, PCA close, histogram high-recall, RANSAC low-precision) with the WHY (RANSAC horizontal planes absorb riser points at tread heights; histogram bands include riser; normals separate orientations robustly). (C) Noise sensitivity — Fig.~\ref{fig:noise}; F1 0.956→0.543 as σ_z 0.01→0.07; explain degradation when σ_z approaches half step height. (D) Safety discussion for stair-following robots — IoU≈0.89 supports coarse foothold planning but precision<1 mislabels risers → recommend ensemble voting, tread-edge erosion margin, temporal verification. Cite chavezgarcia2017learning, gomes2023survey, matsumura2022deep. DEFINE all 5 floats listed as OWNER above (paste ready code).

### 5. Conclusion (`conclusion.tex`, ~0.5 col) — OWNER: writer-conclusion
Summarize the benchmark + finding (DBSCAN+slope best, F1 0.943/IoU 0.892; RANSAC weakest), the noise limit, and the safety takeaway. Future work: ensemble fusion, validation on real LiDAR stairs, and comparison against learned segmenters (qi2016pointnet, sarker2024comprehensive) under low-label regimes. No new floats.
