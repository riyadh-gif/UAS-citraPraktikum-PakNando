"""Generate the 8-10 slide presentation deck (16:9) for the mini project.

Run from repo root:  py slides/build_slides.py
Output: slides/presentasi.pptx
"""
from __future__ import annotations
import json
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
METRICS = json.load(open(ROOT / "metrics.json", encoding="utf-8"))

# Palette
NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2B, 0x6C, 0xB0)
GREEN = RGBColor(0x2C, 0xA0, 0x2C)
RED = RGBColor(0xC0, 0x39, 0x2B)
GREY = RGBColor(0x66, 0x66, 0x66)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x22, 0x22, 0x22)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


def _set(tf_para, text, size, bold=False, color=DARK, align=PP_ALIGN.LEFT):
    tf_para.text = text
    tf_para.font.size = Pt(size)
    tf_para.font.bold = bold
    tf_para.font.color.rgb = color
    tf_para.alignment = align


def add_slide():
    return prs.slides.add_slide(BLANK)


def bar(slide, color=NAVY, h=1.15):
    box = slide.shapes.add_shape(1, 0, 0, SW, Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = color
    box.line.fill.background()
    box.shadow.inherit = False
    return box


def header(slide, title, kicker=None):
    bar(slide)
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.18), SW - Inches(1.0), Inches(0.85))
    tf = tb.text_frame; tf.word_wrap = True
    _set(tf.paragraphs[0], title, 30, True, WHITE)
    if kicker:
        p = tf.add_paragraph(); _set(p, kicker, 14, False, RGBColor(0xCB, 0xDC, 0xF0))


def bullets(slide, items, left, top, width, height, size=18, gap=6):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.word_wrap = True
    for i, (txt, lvl, bold, color) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        prefix = "" if lvl == 0 else ("  " * lvl)
        mark = "" if bold and lvl == 0 else ("•  " if lvl == 0 else "–  ")
        _set(p, f"{prefix}{mark}{txt}", size - lvl * 2, bold, color)
        p.space_after = Pt(gap)
        p.level = lvl
    return tb


def pic(slide, name, left, top, width=None, height=None):
    kw = {}
    if width: kw["width"] = width
    if height: kw["height"] = height
    return slide.shapes.add_picture(str(FIG / name), left, top, **kw)


def caption(slide, text, left, top, width):
    tb = slide.shapes.add_textbox(left, top, width, Inches(0.4))
    _set(tb.text_frame.paragraphs[0], text, 12, False, GREY, PP_ALIGN.CENTER)


# ---------------------------------------------------------------- Slide 1 title
s = add_slide()
big = s.shapes.add_shape(1, 0, 0, SW, SH)
big.fill.solid(); big.fill.fore_color.rgb = NAVY; big.line.fill.background()
big.shadow.inherit = False
accent = s.shapes.add_shape(1, 0, Inches(5.0), SW, Inches(0.12))
accent.fill.solid(); accent.fill.fore_color.rgb = BLUE; accent.line.fill.background()
accent.shadow.inherit = False
tb = s.shapes.add_textbox(Inches(0.9), Inches(1.6), SW - Inches(1.8), Inches(3.2))
tf = tb.text_frame; tf.word_wrap = True
_set(tf.paragraphs[0],
     "Steppable-Surface Segmentation in Simulated Staircase Point Clouds", 36, True, WHITE)
p = tf.add_paragraph()
_set(p, "A Comparison of RANSAC, PCA Normal Analysis, DBSCAN, and Height-Histogram Methods",
     18, False, RGBColor(0xCB, 0xDC, 0xF0))
sub = s.shapes.add_textbox(Inches(0.9), Inches(5.3), SW - Inches(1.8), Inches(1.6))
tf2 = sub.text_frame; tf2.word_wrap = True
_set(tf2.paragraphs[0], "Riyadh Lakadimu", 20, True, WHITE)
for t in ["Master Program in Electrical Engineering - Politeknik Elektronika Negeri Surabaya (PENS)",
          "Course: Sensor and Signal Processing Systems (Final Project)"]:
    pp = tf2.add_paragraph(); _set(pp, t, 14, False, RGBColor(0xCB, 0xDC, 0xF0))

# ---------------------------------------------------------------- Slide 2 motivation
s = add_slide(); header(s, "Background & Objectives", "Introduction")
bullets(s, [
    ("Stair-climbing/following robots and assistive devices need reliable 3D perception.", 0, False, DARK),
    ("Must separate steppable surfaces (tread) from vertical faces (riser) and noise.", 0, False, DARK),
    ("Mislabeling a riser as steppable -> foothold onto a vertical face -> fall hazard.", 1, False, RED),
    ("Deep-learning methods need large labeled data and lack interpretability.", 0, False, DARK),
    ("No controlled benchmark with exact ground-truth labels for this sub-problem.", 1, False, DARK),
    ("Objectives:", 0, True, NAVY),
    ("Generate a labeled 4-step staircase point cloud from a mathematical model.", 1, False, DARK),
    ("Implement and compare four classical geometric methods.", 1, False, DARK),
    ("Quantitative evaluation + noise analysis + robot-safety discussion.", 1, False, DARK),
], Inches(0.6), Inches(1.45), SW - Inches(1.2), Inches(5.6), size=20)

# ---------------------------------------------------------------- Slide 3 data
s = add_slide(); header(s, "Point Cloud Data Generation", "Mathematical 4-step model")
bullets(s, [
    ("Parameters: width w=2.5 m, depth d=0.30 m, height h=0.18 m, N=4 steps.", 0, False, DARK),
    ("Tread (i=0..3):", 0, True, GREEN),
    ("x~U(0,w),  y~U(i·d,(i+1)·d),  z=i·h+εz,  εz~N(0,0.02²)", 1, False, DARK),
    ("Riser (i=1..3):", 0, True, RED),
    ("x~U(0,w),  y=i·d+εy,  z~U((i-1)·h, i·h)", 1, False, DARK),
    ("+ ~4% random outliers and LiDAR jitter N(0,0.005²).", 0, False, DARK),
    (f"Total {METRICS['point_counts']['total']:,} points "
     f"({METRICS['point_counts']['tread']:,} tread / "
     f"{METRICS['point_counts']['riser']:,} riser / "
     f"{METRICS['point_counts']['other']} other).", 0, True, NAVY),
], Inches(0.6), Inches(1.45), Inches(6.4), Inches(5.6), size=18)
pic(s, "profile_ground_truth.png", Inches(7.2), Inches(1.7), width=Inches(5.7))
caption(s, "Side profile (y-z): green=tread, red=riser, grey=other",
        Inches(7.2), Inches(6.35), Inches(5.7))

# ---------------------------------------------------------------- Slide 4 methods overview
s = add_slide(); header(s, "Four Segmentation Methods", "Three-class scheme: tread / riser / other")
bullets(s, [
    ("1. RANSAC Plane Fitting (orientation-gated)", 0, True, NAVY),
    ("Horizontal phase -> tread, vertical phase -> riser; rejects the oblique 'ramp' plane.", 1, False, DARK),
    ("2. PCA Normal Analysis", 0, True, NAVY),
    ("Per-point normals via PCA over k-NN; classified by tilt |n·z|.", 1, False, DARK),
    ("3. DBSCAN + Slope Analysis", 0, True, NAVY),
    ("Orientation split -> spatial clustering -> per-cluster slope confirmation.", 1, False, DARK),
    ("4. Height-Histogram Analysis (advanced)", 0, True, NAVY),
    ("Peaks of the z-histogram = tread levels; bands between = riser.", 1, False, DARK),
    ("Minimum 2 methods required -> 4 implemented for a thorough comparison.", 0, True, GREEN),
], Inches(0.6), Inches(1.45), SW - Inches(1.2), Inches(5.6), size=19)

# ---------------------------------------------------------------- Slide 5 algorithm
s = add_slide(); header(s, "Methodology & Algorithms", "Core formulas")
bullets(s, [
    ("RANSAC: point-to-plane distance", 0, True, NAVY),
    ("d(x)=|n·x+b|,  inliers I={x: d(x)<τ},  τ=0.035 m", 1, False, DARK),
    ("Orientation gate: horizontal |n·z|≥0.93 (tread), vertical ≤0.25 (riser).", 1, False, DARK),
    ("PCA Normal: local k-NN covariance (k=50)", 0, True, NAVY),
    ("C_p=(1/k)Σ(x_j-x̄)(x_j-x̄)ᵀ,  n_p=eigvec_min(C_p)", 1, False, DARK),
    ("Tread |n·z|≥0.80, riser ≤0.50 (looser: per-point normals are noisier).", 1, False, DARK),
    ("DBSCAN: ε=0.08 m within each orientation group, then slope confirmation.", 0, True, NAVY),
    ("Global stair 'ramp' plane: |n·z|=d/√(d²+h²)≈0.86 -> motivates the orientation gate.", 0, False, RED),
], Inches(0.6), Inches(1.45), SW - Inches(1.2), Inches(5.6), size=19)

# ---------------------------------------------------------------- Slide 6 results table
s = add_slide(); header(s, "Experimental Results", "Tread-class metrics (one-vs-rest)")
tm = METRICS["tread_metrics"]
order = ["RANSAC", "PCA-Normals", "DBSCAN-Slope", "Height-Histogram"]
rows, cols = len(order) + 1, 6
tbl_shape = s.shapes.add_table(rows, cols, Inches(0.6), Inches(1.55),
                               Inches(7.0), Inches(2.6))
table = tbl_shape.table
hdr = ["Method", "Acc", "Prec", "Rec", "F1", "IoU"]
for j, h in enumerate(hdr):
    c = table.cell(0, j); c.text = h
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
    pr = c.text_frame.paragraphs[0]; pr.font.size = Pt(14); pr.font.bold = True
    pr.font.color.rgb = WHITE; pr.alignment = PP_ALIGN.CENTER
best = {"accuracy": "DBSCAN-Slope", "precision": "PCA-Normals", "recall": "Height-Histogram",
        "f1": "DBSCAN-Slope", "iou": "DBSCAN-Slope"}
keys = ["accuracy", "precision", "recall", "f1", "iou"]
for i, name in enumerate(order, 1):
    table.cell(i, 0).text = name
    for j, k in enumerate(keys, 1):
        v = tm[name][k]
        c = table.cell(i, j); c.text = f"{v:.3f}"
        pr = c.text_frame.paragraphs[0]; pr.font.size = Pt(13)
        pr.alignment = PP_ALIGN.CENTER
        pr.font.bold = (best[k] == name)
        if best[k] == name:
            pr.font.color.rgb = GREEN
    table.cell(i, 0).text_frame.paragraphs[0].font.size = Pt(13)
    table.cell(i, 0).text_frame.paragraphs[0].font.bold = True
bullets(s, [
    ("DBSCAN-Slope is best: F1 0.943, IoU 0.892.", 0, True, GREEN),
    ("PCA-Normals close behind: F1 0.927, highest precision 0.954.", 0, False, DARK),
    ("Height-Histogram: highest recall 0.984, lower precision.", 0, False, DARK),
    ("Plain RANSAC weakest: precision 0.714 (risers absorbed by tread planes).", 0, False, RED),
], Inches(0.6), Inches(4.4), SW - Inches(1.2), Inches(2.6), size=17)
pic(s, "seg_dbscan_slope.png", Inches(7.85), Inches(1.55), width=Inches(5.0))
caption(s, "DBSCAN 3D segmentation vs ground truth", Inches(7.85), Inches(3.7), Inches(5.0))

# ---------------------------------------------------------------- Slide 7 visuals
s = add_slide(); header(s, "3D Visualization & Histogram", "Experimental results")
pic(s, "height_histogram.png", Inches(0.5), Inches(1.6), width=Inches(6.1))
caption(s, "Height histogram: 4 tread levels detected (z≈0,0.18,0.36,0.54 m)",
        Inches(0.5), Inches(5.45), Inches(6.1))
pic(s, "seg_pca_normals.png", Inches(6.9), Inches(1.6), width=Inches(6.0))
caption(s, "PCA-Normals 3D segmentation (left GT, right result)",
        Inches(6.9), Inches(3.7), Inches(6.0))
bullets(s, [
    ("Each tread forms a sharp z-level; risers fill the bands between levels.", 0, False, DARK),
    ("Green=tread, red=riser, grey=other/outlier.", 0, False, GREY),
], Inches(6.9), Inches(4.3), Inches(6.0), Inches(1.6), size=16)

# ---------------------------------------------------------------- Slide 8 noise + safety
s = add_slide(); header(s, "Noise Analysis & Robot Safety", "Discussion")
pic(s, "noise_sensitivity.png", Inches(0.5), Inches(1.7), width=Inches(6.0))
caption(s, "Tread F1/IoU vs σz (PCA-Normals)", Inches(0.5), Inches(5.2), Inches(6.0))
sw = METRICS["noise_sweep"]
bullets(s, [
    ("Effect of noise:", 0, True, NAVY),
    (f"F1 drops {sw['f1'][0]:.3f} -> {sw['f1'][-1]:.3f} as σz 0.01 -> 0.07 m.", 1, False, DARK),
    ("Sharp fall as σz approaches ½ step height (0.09 m): normals become ambiguous.", 1, False, DARK),
    ("Safety for stair-following robots:", 0, True, NAVY),
    ("IoU≈0.89 is adequate for coarse foothold planning.", 1, False, DARK),
    ("Precision <1.0 -> some risers mislabeled steppable = hazard.", 1, False, RED),
    ("Mitigation: ensemble voting, tread-edge erosion margin, temporal verification.", 1, False, GREEN),
], Inches(6.8), Inches(1.5), Inches(6.1), Inches(5.6), size=18)

# ---------------------------------------------------------------- Slide 9 conclusion
s = add_slide(); header(s, "Conclusion", "Summary")
bullets(s, [
    ("A fully labeled synthetic staircase benchmark + comparison of four classical methods.", 0, False, DARK),
    ("DBSCAN + slope analysis is best (F1 0.943, IoU 0.892); plain RANSAC is weakest.", 0, True, NAVY),
    ("Normal-based methods (PCA, DBSCAN) win: tread vs riser orientation is a strong cue.", 0, False, DARK),
    ("Segmentation degrades as noise approaches half the step height.", 0, False, DARK),
    ("Adequate for coarse foothold planning; needs safety margins before robot use.", 0, False, DARK),
    ("Future work: multi-method ensemble, real LiDAR validation, comparison vs deep learning.", 0, False, DARK),
    ("Code + paper + repo: github.com/riyadh-gif/UAS-citraPraktikum-PakNando", 0, True, BLUE),
], Inches(0.6), Inches(1.6), SW - Inches(1.2), Inches(5.4), size=19)
tb = s.shapes.add_textbox(Inches(0.6), Inches(6.7), SW - Inches(1.2), Inches(0.6))
_set(tb.text_frame.paragraphs[0], "Thank you.", 20, True, NAVY)

out = Path(__file__).resolve().parent / "presentasi.pptx"
prs.save(out)
print(f"Wrote {out}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
