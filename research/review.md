# Peer Review — Classical Geometric Segmentation of Steppable Surfaces in Staircase Point Clouds

**Venue:** IEEE international conference (8-page limit; current build = 7 pages, ~0.7 page free)
**Review mode:** Full multi-perspective review (EIC + methodology + domain + perspective + devil's advocate), cross-checked against `metrics.json`, `citations.md`, and `outline.md`.
**Overall recommendation:** **Minor-to-Major Revision.** The work is sound, internally consistent on most numbers, and honestly scoped as a controlled study, but it has one true BLOCKER (a numeric inconsistency that a reviewer will read as a data error) and a small cluster of MAJOR items around limitations framing, an undefined parameter, and one overstated noise claim. All are fixable within the available page budget.

Severity legend: **[BLOCKER]** must fix before acceptance — wrong/contradictory or unsupported claim; **[MAJOR]** a reviewer will demand it; **[MINOR]** quality/clarity; **[NICE]** optional polish.

---

## Section I — Introduction

**[MINOR] Deep-learning baseline framing is honest but verify it stays that way.**
Lines 22-27 correctly say deep methods are "data hungry" and that the stair sub-problem "lacks controlled, reproducible benchmarks." Good — this does **not** claim we ran a DL baseline. Keep it that way; do not let the rebuttal/camera-ready drift into "we outperform deep methods." No change required, flagged for vigilance.

**[MINOR] Unsupported generality of "leading cause of injurious falls."**
Line 18: "where an undetected step is a leading cause of injurious falls \cite{matsumura2022deep}." `matsumura2022deep` motivates fall prevention for the visually impaired but is an engineering paper, not an epidemiological source for "leading cause." Soften to match what the citation supports.
- Replace: *"where an undetected step is a leading cause of injurious falls \cite{matsumura2022deep}."*
- With: *"where undetected steps are a recognised fall hazard that motivates dedicated stair-detection systems \cite{matsumura2022deep}."*

**[MINOR] Contribution 1 wording vs. reality.**
Lines 40-42 claim the generator models "LiDAR range jitter and outliers." This matches the method (isotropic N(0,0.005^2) jitter + ~4% outliers). Consistent — no change, but see Method [MAJOR] on calling 0.005 m "LiDAR-like" without justification.

**[NICE] Roman-numeral cross-refs.** Lines 56-59 hard-code "Section~II … Section~V." IEEEtran convention is fine, but if `\ref` to section labels is available elsewhere, prefer it for robustness. Optional.

---

## Section II — Related Work

**[MINOR] Citation appropriateness — all keys valid.**
Every `\cite` key in this section (`li2017improved`, `jalal2021rgb`, `zhou2021lsam`, `huang2009consolidation`, `castillo2013point`, `zhou2024identification`, `xu2021object`, `luo2021supervoxel`, `gomes2023survey`, `qi2016pointnet`, `sarker2024comprehensive`, `li2022hybridcr`, `zhao2020few`, `he2023prototype`, `matsumura2022deep`, `marion2017director`, `belter2016adaptive`, `agarwal2022legged`, `stelzer2012stereo`, `chavezgarcia2017learning`) is in the allowed pool. No invented keys. Good.

**[MINOR] "$|\nvec^\top\zhat|\approx 0.86$" claim appears first in Related/Method without derivation.**
Method line 94 asserts the global stair plane has verticality ≈0.86. With d=0.30, h=0.18 the stair ramp slope gives a normal whose vertical component is d/sqrt(d^2+h^2)=0.30/0.350=0.857 → 0.86. This is correct and derivable; consider adding the one-line justification (see Method [MINOR]) so the number is not a magic constant.

**[NICE] British/American spelling mix across sections.**
Related/Method use "organise/organising/labelled/neighbourhood/colour-free"; Intro/Conclusion use "labeled/behavior." IEEE accepts either but demands consistency. Pick one (American is the more common IEEE default) and apply globally. Examples: "organise"→"organize," "labelled"→"labeled," "neighbourhood"→"neighborhood." This is a whole-paper consistency fix.

---

## Section III — Proposed Method

**[BLOCKER] Undefined / inconsistent orientation thresholds between Method prose and the rest of the paper.**
The RANSAC gate is stated two different ways:
- Method line 97-98: tread gate "$|\nvec^\top\zhat|\ge 0.93$," riser gate "$|\nvec^\top\zhat|\le 0.25$."
- `outline.md` line 74 (shared spec) says the same: horizontal ≥0.93, vertical ≤0.25.
But the **PCA-Normals** method (lines 121-122) uses *different* thresholds: tread "$\ge 0.80$," riser "$\le 0.50$," and the **Algorithm** block (generic) leaves the gate symbolic. This is internally consistent *as written* (two methods, two gates) — **however** a reviewer cannot tell whether 0.93/0.25 (RANSAC) vs. 0.80/0.50 (PCA) is intentional or a typo, because nothing states they are deliberately different. Add one sentence making the distinction explicit.
- After Method line 122 add: *"These PCA thresholds (0.80/0.50) are deliberately looser than the RANSAC orientation gate (0.93/0.25): RANSAC fits a global plane whose normal is precise, whereas per-point PCA normals are noisier and require a wider acceptance band."*
This converts an apparent contradiction into a stated design choice. (Severity = BLOCKER because as-is a careful reviewer flags it as a numeric inconsistency.)

**[MAJOR] "LiDAR-like jitter $\mathcal{N}(0,0.005^2)$" is asserted without grounding.**
Lines 73-76 call the 0.005 m isotropic jitter "LiDAR-like … emulating range quantisation and beam divergence." No sensor or datasheet is cited, and the value is arbitrary. For an international reviewer this is the central honesty issue of a *synthetic* benchmark: the noise model is the entire claim to realism. Either (a) cite/justify the 5 mm figure against a real sensor class, or (b) explicitly label it as a nominal modelling choice.
- Replace: *"emulating range quantisation and beam divergence."*
- With: *"approximating the few-millimetre range noise typical of indoor depth sensors; we treat this value as a nominal modelling choice rather than a calibrated sensor model, and we probe its main axis ($\sigma_z$) directly in Section~IV-C."*

**[MAJOR] $\sigma_y$ for risers introduced as a parameter but its role is asymmetric and unexamined.**
Lines 61-68: risers get along-depth jitter $\sigma_y=0.02$ m, treads get height jitter $\sigma_z=0.02$ m. The noise sweep (Sec IV-C) varies only $\sigma_z$. State why the sweep is on $\sigma_z$ only (it is the safety-critical axis that confuses tread/riser separation) — otherwise a reviewer asks "why not sweep $\sigma_y$?".
- After Method line 70 (or in Eval IV-C) add: *"We sweep $\sigma_z$ rather than $\sigma_y$ because vertical jitter is the axis that directly degrades the tread/riser orientation contrast; depth jitter $\sigma_y$ chiefly broadens riser planes and does not move tread points across step levels."*

**[MINOR] Provide the 0.86 derivation.**
Method line 93-94. Add inline: *"(its normal's vertical component equals $d/\sqrt{d^2+h^2}=0.30/0.35\approx0.86$)"* so the constant is reproducible.

**[MINOR] Parameter table would improve reproducibility.**
RANSAC $\tau=0.035$, min-inlier count (called "high" but never numerically given, line 100-101), PCA $k=50$, DBSCAN $\varepsilon=0.08$, histogram peak-window width (never given, lines 149-151), tread/riser thresholds. The **min-inlier count** and the **histogram window width** are undefined numerically — a reviewer cannot reproduce. Either give the numbers in prose or add a compact parameter table (fits the page budget).
- Concretely: line 100-101 "impose a high minimum-inlier count" → give the actual integer used.
- Lines 149-151 "a narrow window around each peak" → give the window half-width in metres.

**[MINOR] Eq. (2) riser z-range uses $((i{-}1)h, ih)$.**
Lines 62-63: for $i=0$ this gives $z\in(-h,0)$, i.e. a riser *below* the first tread (the face down to the floor). If the staircase has no step below tread 0, $i$ should start at 1 for risers, or the text should note the leading riser is the face from floor to tread 0. Clarify the index range for risers vs. treads (treads use $i\in\{0,\dots,N-1\}$, line 47).

---

## Section IV — Evaluation

**[BLOCKER] "Acc" column vs. "three-class accuracy" prose are different quantities with no disambiguation — reads as a data contradiction.**
- Table~\ref{tab:metrics} (lines 71-74) "Acc": RANSAC **0.681**, DBSCAN **0.920**, PCA 0.901, Hist 0.827. These equal `metrics.json` *tread_metrics.accuracy* (one-vs-rest): 0.6805/0.9196/0.9009/0.8270. ✓
- Prose line 95: DBSCAN "highest three-class accuracy ($0.909$)"; line 147: RANSAC "three-class accuracy ($0.667$)." These equal `metrics.json` *overall_accuracy*: 0.9095/0.6665. ✓
Both sets are individually correct, **but the paper never tells the reader the table reports one-vs-rest accuracy while the prose quotes three-class accuracy.** A reviewer comparing "DBSCAN Acc = 0.920" (table) with "three-class accuracy 0.909" (text) will flag a contradiction. **Fix by labelling both.**
- Table caption line 64: append *"; the Acc column is one-vs-rest tread accuracy."*
- Or rename the column header "Acc" → "Acc$_{\text{1vR}}$" and add to the Setup/§A a sentence: *"We distinguish one-vs-rest tread accuracy (Table~\ref{tab:metrics}) from overall three-class accuracy quoted in the text."*
- Then make the prose explicit: line 95 *"the highest \emph{three-class} accuracy ($0.909$)"* and line 147 *"three-class accuracy ($0.667$)"* (already says three-class on line 147 — make line 95 match by also saying "three-class," which it does; the missing half is labelling the TABLE). Severity BLOCKER because uncorrected it looks like the numbers disagree.

**[MAJOR] No Limitations subsection — international reviewers will demand it.**
The paper is a single synthetic staircase (N=4, one geometry, one material-free noise model, no real LiDAR, no occlusion, no curved/spiral/open stairs, no varying tread depth). Sec IV-D discusses safety but not study limitations, and the Conclusion only mentions real-LiDAR validation as future work. Add a short explicit **Limitations** paragraph (the ~0.7 page of slack is best spent here). Suggested content to insert at the end of Sec IV (new IV-E "Limitations and Threats to Validity") or before IV-D:
> *"Several limitations bound the scope of these conclusions. First, the benchmark is synthetic: a single rectangular straight-flight staircase with one fixed geometry ($w,d,h,N$) and an idealized, axis-aligned layout, so absolute scores should be read as relative method rankings rather than field-deployable accuracies. Second, the sensor model is a nominal Gaussian jitter plus uniform outliers; it omits occlusion, missing returns, incidence-angle effects, multi-path, and structured LiDAR scan patterns, all of which a real sensor exhibits. Third, the height-histogram method assumes a regular, gravity-aligned staircase and would not transfer to spiral, open-riser, or unaligned scans without modification. Fourth, all hyper-parameters were tuned once on this cloud; we report no cross-configuration parameter sensitivity beyond the $\sigma_z$ sweep. These constraints motivate the real-LiDAR validation identified in Section~V."*

**[MAJOR] Parameter-sensitivity caveat is too narrow.**
The only sensitivity study is $\sigma_z$ for *one* method (PCA-Normals, lines 160-162). The other three methods and all the threshold/$\varepsilon$/$\tau$/$k$ parameters are evaluated at a single operating point. State this limitation explicitly (covered by the Limitations paragraph above, item 4), and soften any wording implying robustness was established generally. Specifically line 178-179 "Performance degrades monotonically" applies to PCA-Normals only — make sure the reader knows the sweep is single-method (line 161 already says "re-evaluated the PCA-Normals method" — good; keep that scoping in the Conclusion too, see Conclusion [MAJOR]).

**[MINOR] "near-ideal" / "near unit precision" wording.**
Line 179 "near-ideal (F1 0.956…)" and line 203 "no method reaches unit precision." Fine, but ensure no sentence implies deployable real-world accuracy. Line 197-202 already hedges with "coarse foothold planning" and cites `chavezgarcia2017learning,gomes2023survey` — acceptable. No change required.

**[MINOR] Metric definitions: overall accuracy formula is the binary form, not 3-class.**
Lines 35-37 define $\mathrm{Acc}=(TP+TN)/(TP+TN+FP+FN)$ and say it is "computed across the full three-class labelling." That binary formula is the **one-vs-rest** accuracy, not multi-class accuracy (which is correct-points/total). This compounds the BLOCKER above. Fix: state that the tabulated Acc is the one-vs-rest accuracy from this formula, and that the "three-class accuracy" quoted in §B is (#correctly-labelled points)/(total points) over all three classes.
- After line 37 add: *"We additionally report overall three-class accuracy in the text, defined as the fraction of all points whose 3-way label is correct; this differs from the one-vs-rest Acc of Table~\ref{tab:metrics}."*

**[MINOR] Figure 6 (noise) y-axis upper claim vs. data.** metrics.json noise IoU at $\sigma_z=0.07$ is 0.3727; paper says "IoU 0.373" (line 181) ✓ and F1 0.543 ✓. All noise-sweep numbers (0.956/0.915, 0.543/0.373) match metrics.json exactly. Good.

**[MINOR] "$h/2=0.09$\,m" mechanism claim.** Line 184: noise comparable to half step height. h=0.18 → h/2=0.09 ✓. The mechanism argument is sound. The sweep reaches 0.07 < 0.09, so technically the cloud never *reaches* h/2; the steep drop at 0.05-0.07 supports "as σ_z approaches half the step height." Acceptable; consider "approaches" (already used) — fine.

**[NICE] Fig.~\ref{fig:bars} and Table duplicate the same F1/IoU.** The bar chart re-plots two table columns. Given the page budget pressure, this is defensible (visual aid) but a reviewer may call it redundant. Optional: drop `fig:bars` if space is needed for the Limitations paragraph.

---

## Section V — Conclusion

**[BLOCKER] (consistency) — confirm conclusion numbers.**
Conclusion (line 2) quotes F1 0.943, IoU 0.892 (DBSCAN), precision 0.714 (RANSAC), F1 0.956→0.543 noise. All match `metrics.json` (0.9428→0.943, 0.8918→0.892, 0.7141→0.714, 0.9556→0.956, 0.5431→0.543). ✓ No numeric error. Downgrade: this is actually clean — **no fix needed**, listed only to record the cross-check passed.

**[MAJOR] Noise claim attributed paper-wide but established for one method only.**
Line 2: "A noise-sensitivity sweep showed that performance is robust at realistic jitter but degrades sharply…" — the sweep was PCA-Normals only. Scope it.
- Replace: *"A noise-sensitivity sweep showed that performance is robust at realistic jitter but degrades sharply as the height noise approaches half the step height, with tread F1 falling from $0.956$…"*
- With: *"A noise-sensitivity sweep on the PCA-Normals method showed its performance is robust at realistic jitter but degrades sharply as the height noise approaches half the step height, with tread F1 falling from $0.956$…"*

**[MAJOR] Conclusion should explicitly name the synthetic-only limitation, not only as future work.**
Currently real-LiDAR appears only as future work ("validation on real LiDAR staircases beyond the synthetic generator"). Add one clause acknowledging the present results are synthetic-only so the contribution is not over-claimed.
- After "a close second." (early in the paragraph) add: *"We emphasise that these findings are established on a single synthetic staircase under a controlled noise model and should be read as relative method rankings pending real-sensor validation."*

**[MINOR] "apples-to-apples" appears in both Intro/Conclusion and outline.** Acceptable informal idiom for a conference paper, but some IEEE editors dislike colloquialism. Optional: "a like-for-like comparison." NICE.

---

## Cross-Section Consistency Audit (numbers & notation)

| Item | Sources | Verdict |
|---|---|---|
| Cloud size 18,333 = 12,800 + 4,800 + 733 | Method L76, Eval L16-18, metrics.json | ✓ consistent and arithmetically exact |
| Geometry w=2.5,d=0.30,h=0.18,N=4 | Method L45-46, Eval L14-15, metrics.json, outline | ✓ |
| Tread-class table (Acc/P/R/F1/IoU) | Table L71-74 vs metrics.json tread_metrics | ✓ all 20 cells match |
| Overall 3-class acc 0.667/0.909 in prose | Eval L95,L147 vs metrics.json overall_accuracy | ✓ values correct, **but mislabeled vs table** (see Eval BLOCKER) |
| Height peaks {0.00,0.18,0.36,0.54} | Method L152, Eval L125, Fig dashed lines 0.004/0.183/0.362/0.541 vs metrics.json [0.0035,0.1826,0.3616,0.5407] | ✓ rounding consistent |
| Noise sweep F1/IoU | Eval L179-181, Conclusion vs metrics.json noise_sweep | ✓ exact |
| Orientation gates 0.93/0.25 (RANSAC) vs 0.80/0.50 (PCA) | Method L97-98 vs L121-122 vs outline L74 | ⚠ correct but **undisambiguated** (Method BLOCKER) |
| $\sigma_z=0.02$, $\sigma_y=0.02$, jitter 0.005 | Method L68-74 vs outline L9 | ✓ ($\sigma_z$ nominal matches; $\sigma_y$ and 0.005 are new vs outline — fine, but justify, see Method MAJORs) |
| Spelling (organise/labelled vs labeled/behavior) | Related/Method vs Intro/Conclusion | ⚠ mixed (Related NICE) |

No fabricated citations detected. No claim of running a deep-learning baseline detected. Synthetic scope is acknowledged in Intro/Related but under-stated in Eval/Conclusion (addressed by Limitations MAJOR).

---

## Devil's Advocate — strongest counter-argument

*"The benchmark is rigged in favour of the geometric methods and the safety story is built on a number the authors chose."* The single synthetic staircase is axis-aligned, gravity-aligned, rectangular, and noise-free except for a hand-picked 5 mm Gaussian — exactly the regime where PCA normals and height histograms excel. The 'best method, IoU 0.89' headline therefore measures how well the methods fit *the generator's own assumptions*, not stair perception. Because the noise model, the outlier fraction (4%), and every threshold were set by the authors and tuned once, the ranking (DBSCAN > PCA > Hist > RANSAC) could be an artifact of parameter choices rather than a property of the algorithms. The paper's own noise sweep shows the collapse to F1 0.54 at σ_z=0.07 — i.e., the methods are fragile precisely on the axis the synthetic cloud keeps clean. **Mitigation:** the requested Limitations paragraph + the "relative rankings, not deployable accuracies" framing + justifying the 5 mm value directly answer this; with those edits the contribution is honestly bounded and the counter-argument loses its teeth. This is why the Limitations items are MAJOR, not NICE.

---

## Top fixes to apply (prioritized)

1. **[BLOCKER] Disambiguate "Acc" (one-vs-rest, Table) vs "three-class accuracy" (prose).** Relabel the table column/caption and add one defining sentence in §A (Eval). Highest risk: looks like contradictory data.
2. **[BLOCKER] State that PCA gates (0.80/0.50) are intentionally looser than RANSAC gates (0.93/0.25).** One sentence after Method L122.
3. **[MAJOR] Add a Limitations / Threats-to-Validity paragraph** (synthetic single staircase, nominal noise model, single operating point, histogram assumes aligned stairs). Use the ~0.7-page slack here. Insert end of Sec IV.
4. **[MAJOR] Justify or down-label the "LiDAR-like" 5 mm jitter** as a nominal modelling choice (Method L73-76).
5. **[MAJOR] Scope the noise claim to PCA-Normals in the Conclusion** and add the "synthetic-only, relative-ranking" caveat to the Conclusion.
6. **[MAJOR] Explain why only $\sigma_z$ is swept** (and only one method) — one sentence in Method/Eval.
7. **[MINOR] Define the two missing numeric parameters:** RANSAC minimum-inlier count and histogram peak-window width.
8. **[MINOR] Fix the overall-accuracy formula gloss** (the binary formula is one-vs-rest, not multi-class) — add the 3-class definition.
9. **[MINOR] Add the 0.86 derivation** ($d/\sqrt{d^2+h^2}$) and clarify the riser index range in Eq. (2).
10. **[MINOR/NICE] Unify spelling** (American throughout) and soften "leading cause of injurious falls" in the Intro.

**Net page impact:** items 1, 2, 4, 5, 6, 8, 9 are sentence-level (~0.2 page total); item 3 is ~0.25-0.3 page. Comfortably within the 1-page slack; optionally drop the redundant `fig:bars` (Eval NICE) if tight.
