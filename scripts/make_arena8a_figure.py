#!/usr/bin/env python3
"""Generate publication-grade 4-panel diagnostic figure docs/assets/fig_arena8a_mdrc.png."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402


def main() -> int:
    ev_dir = evidence_dir()
    wdir = work_dir()
    ddir = data_dir()
    dl_dir = downloads_dir()
    out_png = ROOT / "docs" / "assets" / "fig_arena8a_mdrc.png"
    out_png.parent.mkdir(parents=True, exist_ok=True)

    exp1 = json.loads((ev_dir / "arena8a_exp1_canary_and_domains.json").read_text())
    exp2 = json.loads((ev_dir / "arena8a_exp2_oof_comparison.json").read_text())
    exp3 = json.loads((ev_dir / "arena8a_exp3_crest_and_gates.json").read_text())
    rc = json.loads((ev_dir / "arena8a_run_card.json").read_text())

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.edgecolor": "#334155",
        "axes.linewidth": 0.8,
    })

    fig, axes = plt.subplots(2, 2, figsize=(14.5, 10.4), dpi=160)
    fig.patch.set_facecolor("#ffffff")

    # ---------------- Panel A: Repaired Visible-Only B-Ladder vs Broken catalogue_hidden ----------------
    ax = axes[0, 0]
    bs = [0, 1, 2, 3]
    vis_vals = [exp1["repaired_visible_only_b_ladder_on_d28"][f"B={b}"]["pooled_dti"] for b in bs]
    legacy_vals = [0.09832, 0.03104, 0.00460, 0.00120]  # IR-32-INSTR-03 measured full-cat B-gate collapse
    live_pts = [(0, 0.2600, "d2.8 (0.2600)"), (1, 0.2708, "solo (0.2708)"), (2, 0.2778, "h33-2-b2 (0.2778)")]

    ax.plot(bs, vis_vals, "o-", color="#0f766e", lw=2.4, ms=7, label="Repaired visible-only HOLDOUT-DTI (v3)")
    ax.plot(bs, legacy_vals, "s--", color="#dc2626", lw=1.8, ms=6, label="Legacy full-cat gate (IR-32-INSTR-03)")
    ax.scatter([2], [vis_vals[2]], s=130, facecolors="none", edgecolors="#0f766e", lw=2.2, zorder=5)
    ax.annotate(
        f"Global peak B=2: {vis_vals[2]:.4f}\n(matches live 0.2778 winner!)",
        xy=(2, vis_vals[2]),
        xytext=(1.05, 0.072),
        arrowprops=dict(arrowstyle="->", color="#0f766e", lw=1.2),
        fontsize=8.5,
        color="#0f766e",
        fontweight="bold",
    )
    ax2 = ax.twinx()
    ax2.plot([p[0] for p in live_pts], [p[1] for p in live_pts], "^:", color="#1d4ed8", lw=1.8, ms=7, label="Live ORGANIZER/OWNER DTI")
    ax2.set_ylabel("Live Leaderboard DTI (right axis)", color="#1d4ed8", fontsize=9)
    ax2.tick_params(axis="y", labelcolor="#1d4ed8")
    ax2.set_ylim(0.245, 0.285)

    ax.set_xticks(bs)
    ax.set_xticklabels(["B=0\n(0 m)", "B=1\n(100 m)", "B=2\n(200 m)", "B=3\n(300 m)"])
    ax.set_ylabel("Local Holdout DTI (left axis)", color="#0f172a")
    ax.set_ylim(0.0, 0.115)
    ax.grid(True, alpha=0.25)
    ax.set_title("A. Resolution of IR-32-INSTR-03: Visible-Only B-Ladder")
    ax.legend(loc="lower left", fontsize=8, framealpha=0.92)

    # ---------------- Panel B: Visible-Only Spatially-Blocked HOLDOUT-DTI Progression ----------------
    ax = axes[0, 1]
    rows_b = [
        ("Random-B2 (37.7k)", exp1["random_b2_baseline"]["visible_only_holdout"], "#94a3b8"),
        ("D1: 1m LiDAR Dipole", exp1["solo_unsupervised_domains"]["D1_LiDAR_Dipole"]["visible_only_holdout"], "#64748b"),
        ("D2: True Mag Tilt", exp1["solo_unsupervised_domains"]["D2_True_Mag_Tilt"]["visible_only_holdout"], "#64748b"),
        ("D4: Hydrothermal Alt", exp1["solo_unsupervised_domains"]["D4_Hydrothermal_Alt"]["visible_only_holdout"], "#64748b"),
        ("MDRC Unsup 4-Domain", exp1["solo_unsupervised_domains"]["MDRC_Unsup_4Domain"]["visible_only_holdout"], "#0284c7"),
        ("CTRL 35-ch OOF", exp2["ctrl_35ch_oof_37654"]["visible_only_holdout"], "#d97706"),
        ("D2.8 vis-B2 (0.2778 parent)", exp1["repaired_visible_only_b_ladder_on_d28"]["B=2"], "#1d4ed8"),
        ("MDRC-DualOOF (37.7k)", exp2["mdrc_dualoof_unsharpened_37654"]["visible_only_holdout"], "#0d9488"),
        ("MDRC-Crest (37.7k)", exp3["arms_compared"]["MDRC_Crest_37654"]["visible_only_holdout"], "#059669"),
        ("MDRC-Crest-Bar (44.1k)", exp3["arms_compared"]["MDRC_Crest_CreditBar"]["visible_only_holdout"], "#047857"),
    ]
    y_pos = np.arange(len(rows_b))
    means = [r[1]["pooled_dti"] for r in rows_b]
    err_lo = [r[1]["pooled_dti"] - r[1]["ci95"][0] for r in rows_b]
    err_hi = [r[1]["ci95"][1] - r[1]["pooled_dti"] for r in rows_b]
    colors = [r[2] for r in rows_b]

    ax.barh(y_pos, means, xerr=[err_lo, err_hi], color=colors, alpha=0.88, height=0.68, capsize=3, ecolor="#1e293b")
    ax.axvline(exp1["repaired_visible_only_b_ladder_on_d28"]["B=2"]["pooled_dti"], color="#1d4ed8", ls="--", lw=1.3)
    for yi, mv, eh in zip(y_pos, means, err_hi):
        ax.text(mv + eh + 0.0018, yi, f"{mv:.4f}", va="center", fontsize=8, fontweight="bold", color="#0f172a")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([r[0] for r in rows_b], fontsize=8.5)
    ax.set_xlim(0.0, 0.148)
    ax.set_xlabel("Pooled Visible-Only HOLDOUT-DTI (22,232 withheld px, 95% CI)")
    ax.grid(True, axis="x", alpha=0.25)
    ax.set_title("B. Visible-Only Blocked Holdout (7/8 Cells Won vs D2.8)")

    # ---------------- Panel C: Off-Catalogue SGMC Benchmark & Negative-Label Bias Discovery ----------------
    ax = axes[1, 0]
    rows_c = [
        ("CTRL 35-ch Supervised OOF", exp2["ctrl_35ch_oof_37654"]["sgmc_prevalence_calibrated_dti"], "#d97706"),
        ("MDRC-DualOOF (unsharpened)", exp2["mdrc_dualoof_unsharpened_37654"]["sgmc_prevalence_calibrated_dti"], "#64748b"),
        ("MDRC-Crest (37,654 px)", exp3["arms_compared"]["MDRC_Crest_37654"]["sgmc_prevalence_calibrated_dti"], "#059669"),
        ("MDRC-Crest-Bar (44,090 px)", exp3["arms_compared"]["MDRC_Crest_CreditBar"]["sgmc_prevalence_calibrated_dti"], "#047857"),
        ("D2.8 (live 0.2600)", exp1["champion_benchmarks"]["D28_sgmc_cal"], "#3b82f6"),
        ("CHAMPION h33-2-b2 (live 0.2778)", exp1["champion_benchmarks"]["CHAMPION_h33-2-b2_sgmc_cal"], "#1d4ed8"),
        ("MDRC Unsup 4-Domain (0 labels)", exp1["solo_unsupervised_domains"]["MDRC_Unsup_4Domain"]["sgmc_prevalence_calibrated_dti"], "#7c3aed"),
        ("D1: 1m LiDAR Dipole (0 labels)", exp1["solo_unsupervised_domains"]["D1_LiDAR_Dipole"]["sgmc_prevalence_calibrated_dti"], "#9333ea"),
    ]
    yc = np.arange(len(rows_c))
    vals_c = [r[1] for r in rows_c]
    ax.barh(yc, vals_c, color=[r[2] for r in rows_c], alpha=0.88, height=0.66)
    ax.axvline(exp1["champion_benchmarks"]["CHAMPION_h33-2-b2_sgmc_cal"], color="#dc2626", ls="--", lw=1.5, label="Gate G5 bar (Champion 0.0641)")
    for yi, vv in zip(yc, vals_c):
        ax.text(vv + 0.0012, yi, f"{vv:.4f}", va="center", fontsize=8, fontweight="bold")
    ax.set_yticks(yc)
    ax.set_yticklabels([r[0] for r in rows_c], fontsize=8.5)
    ax.set_xlim(0.0, 0.118)
    ax.set_xlabel("Off-Catalogue USGS SGMC Prevalence-Calibrated DTI (62,703 px)")
    ax.grid(True, axis="x", alpha=0.25)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("C. Why Gate G5 Triggered NEGATIVE: Supervised y=0 Suppresses Pre-Q Faults")

    # ---------------- Panel D: Spatial Map Comparison (Downsampled 4x for Crisp Rendering) ----------------
    ax = axes[1, 1]
    ctx = holdout.load_holdout_context(ddir)
    champ = holdout.read_binary(dl_dir / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif")
    cand = np.load(wdir / "arena8a_best_mask.npy")

    step = 4
    foot_s = ctx.foot[::step, ::step]
    lab_s = gaussian_filter(ctx.labels.astype(np.float32), 1.5)[::step, ::step] > 0.06
    ch_s = gaussian_filter(champ.astype(np.float32), 3.0)[::step, ::step]
    ca_s = gaussian_filter(cand.astype(np.float32), 3.0)[::step, ::step]

    rgb = np.ones((foot_s.shape[0], foot_s.shape[1], 3), dtype=np.float32) * 0.96
    rgb[foot_s] = np.array([0.09, 0.12, 0.18], dtype=np.float32)
    rgb[lab_s & foot_s] = np.array([0.45, 0.50, 0.58], dtype=np.float32)

    ch_n = np.clip(ch_s / max(float(np.percentile(ch_s[foot_s], 99.2)), 1e-6), 0.0, 1.0)
    ca_n = np.clip(ca_s / max(float(np.percentile(ca_s[foot_s], 99.2)), 1e-6), 0.0, 1.0)

    # Cyan = Champion (0.2778), Amber/Coral = Unique A8A MDRC-Crest
    rgb[:, :, 0] = np.where(foot_s, np.clip(rgb[:, :, 0] + 0.85 * ca_n, 0, 1), rgb[:, :, 0])
    rgb[:, :, 1] = np.where(foot_s, np.clip(rgb[:, :, 1] + 0.65 * ch_n + 0.42 * ca_n, 0, 1), rgb[:, :, 1])
    rgb[:, :, 2] = np.where(foot_s, np.clip(rgb[:, :, 2] + 0.88 * ch_n, 0, 1), rgb[:, :, 2])

    ax.imshow(rgb, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        f"D. Map: A8A MDRC (Amber, {int(cand.sum()):,} px) vs Champion (Cyan, 37,654 px)\n"
        f"Surf |rho|={rc['correlation_and_overlap_vs_registry']['vs_champion_02778']['surface_spearman_before_placement']:.3f}, "
        f"Within-3px={rc['correlation_and_overlap_vs_registry']['vs_champion_02778']['frac_candidate_dots_within_3px_of_registry']*100:.1f}% (UNIQUE)"
    )

    fig.suptitle(
        "GEMSDOE32 Arena8a (MDRC): Multi-Domain Ridge-Crest Concordance — Pre-Registered Validation & Automated Gate Audit",
        fontsize=12.5,
        fontweight="bold",
        y=0.985,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.962])
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Wrote {out_png} ({out_png.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
