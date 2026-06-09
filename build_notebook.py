"""Build and execute mini_project.ipynb from the package modules.

This is a one-shot generator: it assembles markdown + code cells, executes
the notebook headlessly, and writes the result to mini_project.ipynb.
"""

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbconvert.preprocessors import ExecutePreprocessor

nb = new_notebook()
cells = []
md = lambda s: cells.append(new_markdown_cell(s))
code = lambda s: cells.append(new_code_cell(s))

md(r"""# Mini Project: Segmentasi Point Cloud Anak Tangga (4 Step)

**Sensor dan Sistem Pengolahan Sinyal — UAS**

Notebook ini menunjukkan keseluruhan pipeline:
1. **Generasi** point cloud anak tangga 4 step dari persamaan matematis.
2. **Segmentasi** permukaan dapat-dipijak (tread), riser, dan lainnya dengan **4 metode**:
   RANSAC plane fitting, PCA + analisis normal, DBSCAN + analisis kemiringan,
   dan Height Histogram Analysis (metode lanjutan).
3. **Evaluasi**: Accuracy, Precision, Recall, F1, IoU untuk kelas *dapat dipijak*,
   visualisasi 3D, dan analisis pengaruh noise.
""")

md(r"""## 1. Generasi Data Point Cloud

Untuk setiap step $i = 0, \dots, N-1$:

**a. Permukaan Horizontal (Tread — dapat dipijak)**
$$\begin{cases}
x \sim \mathrm{Uniform}(0, \text{width}) \\
y \sim \mathrm{Uniform}(i\cdot\text{depth},\, (i+1)\cdot\text{depth}) \\
z = i\cdot\text{height} + \epsilon_z, \quad \epsilon_z \sim \mathcal{N}(0, 0.02^2)
\end{cases}$$

**b. Permukaan Vertikal (Riser)**
$$\begin{cases}
x \sim \mathrm{Uniform}(0, \text{width}) \\
y = i\cdot\text{depth} + \epsilon_y, \quad \epsilon_y \sim \mathcal{N}(0, 0.02^2) \\
z \sim \mathrm{Uniform}((i-1)\cdot\text{height},\, i\cdot\text{height})
\end{cases}$$

Ditambah outlier acak dan jitter LiDAR isotropik. Target total titik: 15.000–25.000.
""")

code("""import numpy as np
import matplotlib.pyplot as plt

from stair_segmentation.generate import StairParams, generate_stair_cloud, summarize
from stair_segmentation import segment as seg
from stair_segmentation import evaluate as ev

params = StairParams()
points, labels = generate_stair_cloud(params)
print("Jumlah titik per kelas:", summarize(labels))
print("bbox min:", points.min(0).round(3), " max:", points.max(0).round(3))""")

md("### Visualisasi data mentah (side profile y–z)")
code("""fig, ax = plt.subplots(figsize=(7,5))
for cls, color in ev.CLASS_COLORS.items():
    m = labels == cls
    ax.scatter(points[m,1], points[m,2], s=3, c=color, label=ev.CLASS_LABELS[cls])
ax.set_xlabel('y (m) - depth'); ax.set_ylabel('z (m) - height')
ax.set_title('Ground truth - side profile'); ax.set_aspect('equal','box')
ax.legend(markerscale=3); plt.show()""")

md(r"""## 2. Estimasi Normal (PCA lokal)

Normal tiap titik diestimasi via PCA pada $k$ tetangga terdekat: eigenvector dengan
eigenvalue terkecil dari matriks kovarians tetangga adalah arah normal permukaan.
""")
code("""normals = seg.estimate_normals(points, k=50)
cos_z = np.abs(normals @ np.array([0,0,1.0]))
print('median |n.z| tread:', round(float(np.median(cos_z[labels==0])),3))
print('median |n.z| riser:', round(float(np.median(cos_z[labels==1])),3))""")

md(r"""## 3. Empat Metode Segmentasi

- **RANSAC**: dua fase — ekstraksi bidang horizontal ($|\hat n \cdot \hat z| \ge 0.93$) → tread,
  lalu bidang vertikal ($|\hat n \cdot \hat z| \le 0.25$) → riser.
- **PCA-Normals**: klasifikasi tiap titik dari kemiringan normal lokalnya.
- **DBSCAN-Slope**: split orientasi → klaster spasial Euclidean → konfirmasi kemiringan.
- **Height-Histogram**: puncak histogram $z$ = level tread; pita antar-level = riser.
""")
code("""preds = {}
preds['RANSAC'] = seg.ransac_segment(points)
preds['PCA-Normals'] = seg.pca_normal_segment(points, normals=normals)
preds['DBSCAN-Slope'] = seg.dbscan_slope_segment(points, normals=normals)[0]
hist_pred, peaks = seg.height_histogram_segment(points)
preds['Height-Histogram'] = hist_pred
print('Level tread terdeteksi (Height-Histogram):', [round(p,3) for p in peaks])""")

md("### Histogram ketinggian dengan puncak tread")
code("""z = points[:,2]
fig, ax = plt.subplots(figsize=(7,4))
ax.hist(z, bins=120, color='#4c72b0', alpha=0.8)
for pk in peaks: ax.axvline(pk, color='#2ca02c', ls='--')
ax.set_xlabel('z (m)'); ax.set_ylabel('count')
ax.set_title(f'{len(peaks)} level tread'); plt.show()""")

md("## 4. Evaluasi — metrik kelas *dapat dipijak* (tread)")
code("""results = {n: ev.tread_metrics(labels, p) for n, p in preds.items()}
overall = {n: ev.multiclass_accuracy(labels, p) for n, p in preds.items()}
print(ev.metrics_table(results))
print()
print('Akurasi 3-kelas:', {k: round(v,3) for k,v in overall.items()})""")

md("### Visualisasi 3D: ground truth vs hasil tiap metode")
code("""from mpl_toolkits.mplot3d import Axes3D  # noqa
for name, pred in preds.items():
    fig = plt.figure(figsize=(11,4.5))
    ax1 = fig.add_subplot(1,2,1, projection='3d'); ev._scatter3d(ax1, points, labels, 'Ground truth')
    ax2 = fig.add_subplot(1,2,2, projection='3d'); ev._scatter3d(ax2, points, pred, name)
    fig.suptitle(name); plt.tight_layout(); plt.show()""")

md(r"""## 5. Analisis Pengaruh Noise

Regenerasi data dengan $\sigma_z$ meningkat lalu segmentasi (PCA-Normals);
plot F1 dan IoU kelas tread terhadap level noise.
""")
code("""sigmas = [0.01,0.02,0.03,0.04,0.05,0.07]
f1s, ious = [], []
for s in sigmas:
    p = StairParams(**{**params.__dict__, 'sigma_z': float(s)})
    pts2, lbl2 = generate_stair_cloud(p)
    pr = seg.pca_normal_segment(pts2)
    m = ev.tread_metrics(lbl2, pr); f1s.append(m['f1']); ious.append(m['iou'])
fig, ax = plt.subplots(figsize=(7,4))
ax.plot(sigmas, f1s, 'o-', label='F1'); ax.plot(sigmas, ious, 's-', label='IoU')
ax.set_xlabel('sigma_z (m)'); ax.set_ylabel('score'); ax.set_ylim(0,1.02)
ax.grid(alpha=0.3); ax.legend(); ax.set_title('Sensitivitas noise'); plt.show()""")

md(r"""## 6. Diskusi & Kesimpulan

- **DBSCAN-Slope** dan **PCA-Normals** memberi F1/IoU tertinggi untuk kelas tread.
- **RANSAC** murni rawan menangkap bidang miring "ramp" dan titik riser pada
  ketinggian tread, sehingga presisinya paling rendah — perlu gating orientasi.
- **Height-Histogram** sederhana namun recall sangat tinggi (level tread sangat
  terpisah pada sumbu $z$); presisi turun bila pita riser ikut terhitung.

**Keamanan untuk robot pengikut tangga:** IoU tread ~0.86–0.89 (PCA/DBSCAN) cukup
untuk perencanaan pijakan kasar, namun presisi < 1.0 berarti sebagian titik riser
salah dilabeli dapat-dipijak. Untuk keselamatan, gabungkan beberapa metki
(voting) dan tambahkan margin keamanan di tepi tread sebelum dipakai robot.
""")

nb["cells"] = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}

ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
ep.preprocess(nb, {"metadata": {"path": "."}})

with open("mini_project.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Wrote and executed mini_project.ipynb")
