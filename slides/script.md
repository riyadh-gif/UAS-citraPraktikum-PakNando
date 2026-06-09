# Presentation Script — Steppable-Surface Segmentation in Staircase Point Clouds

Speaker notes for `presentasi.pptx` (9 slides). Target: ~8.5 minutes, leaving buffer under the 10-minute limit. Speaking pace ~140 words/min. Read naturally, pause at the slash marks if you need a breath.

---

## Slide 1 — Title  (~30 s)

Good morning. My name is Riyadh Lakadimu, from the Master Program in Electrical Engineering at PENS. This is my final project for the Sensor and Signal Processing Systems course. The topic is steppable-surface segmentation in simulated staircase point clouds, where I generate a staircase point cloud from a mathematical model and then compare four classical geometric methods: RANSAC, PCA normal analysis, DBSCAN, and height-histogram analysis.

---

## Slide 2 — Background & Objectives  (~60 s)

Robots that climb or follow stairs, and assistive devices for the visually impaired, all need reliable three-dimensional perception. The key task is to tell which parts of a point cloud are steppable treads, the flat horizontal surfaces, and which are vertical risers or just noise.

This is safety-critical. If the system labels a riser as steppable, a robot could place a foothold onto a vertical face and fall. So we need both high recall and high precision on the tread class.

Deep-learning methods can do this, but they need large amounts of labeled 3D data and offer little interpretability, and there is no controlled benchmark with exact ground truth for this specific problem.

So my objectives are three. First, generate a fully labeled four-step staircase point cloud from a mathematical model. Second, implement and compare four classical geometric methods. Third, evaluate them quantitatively, study the effect of noise, and discuss what the errors mean for robot safety.

---

## Slide 3 — Point Cloud Data Generation  (~70 s)

The staircase is generated analytically from physical parameters: a width of two and a half meters, a tread depth of thirty centimeters, a step height of eighteen centimeters, and four steps.

For each step, tread points are sampled uniformly across the horizontal surface and placed at the step height, with a small Gaussian height noise of two centimeters. Riser points share the same width but sit on a vertical plane, with their height sweeping across one step rise.

On top of this I inject realism: about four percent of the points are random outliers, and every point gets an isotropic LiDAR-like jitter of five millimeters.

The result, shown on the right, is a cloud of eighteen thousand three hundred points: twelve thousand eight hundred tread points in green, four thousand eight hundred riser points in red, and the rest as grey clutter. Because the generator emits the label for every point, we get exact ground truth for free.

---

## Slide 4 — Four Segmentation Methods  (~65 s)

All four methods output the same three classes: tread, riser, and other.

The first is RANSAC plane fitting. I run it in two phases: first extract horizontal planes as treads, then vertical planes as risers. The orientation gate is essential, otherwise RANSAC locks onto the oblique ramp that spans the whole staircase.

The second is PCA normal analysis. For each point I estimate a surface normal and classify it by how vertical that normal is.

The third is DBSCAN with slope analysis. I first split points by orientation, then cluster them spatially, so each physical surface becomes one cluster, and confirm each cluster by its slope.

The fourth, the advanced method, is height-histogram analysis. The peaks of the height histogram are the tread levels, and the bands between them are risers.

The brief required at least two methods; I implemented four for a thorough comparison.

---

## Slide 5 — Methodology & Algorithms  (~65 s)

Here are the core formulas. In RANSAC, each point is scored by its distance to the candidate plane, and inliers are points closer than a threshold tau of thirty-five millimeters. The orientation gate keeps planes whose normal is nearly vertical for treads, and nearly horizontal for risers.

For PCA, I build the local covariance matrix over the fifty nearest neighbors, and the eigenvector with the smallest eigenvalue is the surface normal. A point is a tread when its normal is steep enough, and a riser when it is flat enough. These thresholds are looser than RANSAC's, because per-point normals are noisier than a fitted plane.

DBSCAN clusters with a radius of eight centimeters inside each orientation group, then confirms by slope.

One key insight: the global staircase ramp has a verticality of about zero point eight six, which is why an ungated RANSAC fails and why the orientation gate is necessary.

---

## Slide 6 — Experimental Results  (~70 s)

This table reports the tread-class metrics. The winner is DBSCAN with slope analysis, with an F1 of zero point nine four three and an IoU of zero point eight nine two.

PCA normals is a very close second, with F1 of zero point nine two seven, and it has the highest precision of all, zero point nine five four, because it only accepts points whose normal is clearly vertical.

The height-histogram has the highest recall, zero point nine eight four, since treads concentrate sharply at discrete heights, but its precision is lower because the bands also catch some riser points.

Plain RANSAC is the weakest, with a precision of only zero point seven one four. The reason is that the horizontal planes it fits at each tread height also absorb riser points sitting at that height. On the right you can see the DBSCAN segmentation matches the ground truth very cleanly.

---

## Slide 7 — 3D Visualization & Histogram  (~50 s)

These visualizations make the behavior concrete. On the left is the height histogram. You can clearly see four sharp peaks, which are exactly the four tread levels at zero, eighteen, thirty-six, and fifty-four centimeters, matching the parameters we used to generate the data.

On the right is the PCA-normals segmentation in 3D, ground truth on the left and the result on the right. Green is tread, red is riser, grey is other. Each tread forms a clean horizontal level, and the risers fill the vertical bands in between.

---

## Slide 8 — Noise Analysis & Robot Safety  (~70 s)

I also studied how the methods hold up under noise. As the height noise sigma-z grows from one to seven centimeters, the tread F1 falls from zero point nine five six down to zero point five four three. The drop becomes steep once the noise approaches half the step height, around nine centimeters, because at that point the normals can no longer separate treads from risers.

For robot safety, this matters. An IoU near zero point eight nine is good enough for coarse foothold planning. But no method reached perfect precision, which means some riser points are still labeled steppable, and that is exactly the dangerous error.

So for a real deployment I recommend three safeguards: ensemble voting across the methods, eroding the tread edges to add a safety margin, and temporal verification across consecutive scans before committing a foothold.

---

## Slide 9 — Conclusion  (~45 s)

To conclude: I built a fully labeled synthetic staircase benchmark and compared four classical geometric methods. DBSCAN with slope analysis was the best, and plain RANSAC the weakest. Normal-based methods win because the orientation contrast between treads and risers is a strong, robust cue. Performance degrades as noise approaches half the step height.

The results are good enough for coarse foothold planning but need safety margins before real robot use. Future work includes a multi-method ensemble, validation on real LiDAR data, and a comparison against deep-learning segmenters. All the code, the paper, and the slides are on the GitHub repository shown here. Thank you, and I am happy to take any questions.

---

### Timing summary
| Slide | Topic | Time |
|---|---|---|
| 1 | Title | 0:30 |
| 2 | Background & Objectives | 1:00 |
| 3 | Data Generation | 1:10 |
| 4 | Four Methods | 1:05 |
| 5 | Methodology & Algorithms | 1:05 |
| 6 | Results | 1:10 |
| 7 | Visualization | 0:50 |
| 8 | Noise & Safety | 1:10 |
| 9 | Conclusion | 0:45 |
| **Total** | | **~8:45** |

Tip: if you run long, trim the formula details on Slide 5 and the safeguard list on Slide 8 first.
