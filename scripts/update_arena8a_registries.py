#!/usr/bin/env python3
"""Idempotently synchronize registry/*.json and docs/score-ledger.csv with Arena8a receipts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    rc = json.loads((ROOT / "evidence" / "arena8a_run_card.json").read_text())
    exp1 = json.loads((ROOT / "evidence" / "arena8a_exp1_canary_and_domains.json").read_text())
    exp3 = json.loads((ROOT / "evidence" / "arena8a_exp3_crest_and_gates.json").read_text())

    # 1. Update registry/submission_build.json to feature the NEW UNIQUE Arena8a deliverable
    #    with unmistakable automated verdict (`OK TO DOWNLOAD: YES | OK TO SUBMIT: NO — NEGATIVE`),
    #    while preserving the 0.2778 champion (with repaired 186,378-byte zip!) in `pack`.
    tif_rel = rc["raster_path"]
    zip_rel = rc["zip_path"]
    nan_rel = f"docs/downloads/{rc['nan_twin_filename']}"
    tif_bytes = (ROOT / tif_rel).stat().st_size
    nan_bytes = (ROOT / nan_rel).stat().st_size

    champ_tif_rel = "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    champ_zip_rel = "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.zip"

    sub_build = {
        "name": Path(tif_rel).stem,
        "note": rc["submission_note"],
        "verdict": rc["verdict"],
        "ok_to_download": rc["ok_to_download"],
        "ok_to_submit": rc["ok_to_submit"],
        "status_line": (
            f"LATEST UNIQUE SESSION DELIVERABLE = {rc['submission_name']} (2026-10-26): "
            f"OK TO DOWNLOAD = YES (100% portal-legal [0, 1] float32, 0 NaN, genuinely unique: "
            f"pre-placement surface |rho|={rc['correlation_and_overlap_vs_registry']['worst_abs_surface_spearman_before_placement']:.4f}<=0.90, "
            f"within-3px={rc['correlation_and_overlap_vs_registry']['worst_frac_within_3px_genuine_models']*100:.2f}%<=70%; "
            f"52.89% vs 0.2778 champion). "
            f"OK TO SPEND WEEKLY LEADERBOARD SLOT = NO — AUTOMATED VERDICT: NEGATIVE (DO NOT SUBMIT). "
            f"Beats both CTRL-35ch (0.09893) and D2.8 vis-B2 (0.09920) on repaired visible-only HOLDOUT-DTI "
            f"at {rc['holdout_dti']['primary_visible_only_holdout']['pooled_dti']:.5f} "
            f"[95% CI {rc['holdout_dti']['primary_visible_only_holdout']['ci95'][0]:.5f}, "
            f"{rc['holdout_dti']['primary_visible_only_holdout']['ci95'][1]:.5f}] (7/8 cells won vs D2.8), "
            f"and beats CTRL-35ch on off-catalogue SGMC (0.05509 vs 0.05019), but fails Gate G5 vs "
            f"CHAMPION h33-2-b2 on off-catalogue SGMC (0.05509 < 0.06412). Keep reigning 0.2778 champion; do not waste a weekly slot."
        ),
        "status_line_2026_10_25": (
            f"LATEST UNIQUE SESSION DELIVERABLE = {rc['submission_name']} (2026-10-26): "
            f"OK TO DOWNLOAD = YES (12/12 + strict [0,1] GeoTIFF checks PASS, unique lane PASS) · "
            f"OK TO SUBMIT TO PORTAL = NO — AUTOMATED VERDICT: NEGATIVE (DO NOT SPEND WEEKLY SLOT). "
            f"Repaired visible-only HOLDOUT-DTI = {rc['holdout_dti']['primary_visible_only_holdout']['pooled_dti']:.5f} "
            f"(beats CTRL-35ch 0.09893 & D2.8 vis-B2 0.09920; 7/8 cells won vs D2.8), "
            f"but off-catalogue SGMC = {rc['holdout_dti']['secondary_sgmc_off_catalogue']['sgmc_prevalence_calibrated_dti']:.5f} "
            f"< 0.2778 champion (0.06412, Gate G5 FAIL). Reigning live-scored portfolio champion remains "
            f"h33-h33-2-b2 (0.2778 ORGANIZER-CONFIRMED owner receipt; already submitted — do not resubmit)."
        ),
        "file": {
            "path": tif_rel,
            "sha256": rc["raster_sha256"],
            "bytes": tif_bytes,
            "positive_px": rc["emitted_positive_pixels"],
        },
        "file_zeros": {
            "path": tif_rel,
            "sha256": rc["raster_sha256"],
            "bytes": tif_bytes,
        },
        "zip": {
            "path": zip_rel,
            "sha256": rc["zip_sha256"],
            "bytes": rc["zip_bytes"],
        },
        "candidate_id": rc["submission_name"].replace("GEMSDOE32-", ""),
        "tier": 0,
        "hypothesis": "A8A-H1 (MDRC_Crest_CreditBar)",
        "visible_only_holdout_dti": rc["holdout_dti"]["primary_visible_only_holdout"]["pooled_dti"],
        "visible_only_holdout_ci95": rc["holdout_dti"]["primary_visible_only_holdout"]["ci95"],
        "catalogue_hidden_mean": None,
        "drift_corrected_holdout_mean": None,
        "sgmc_prevalence_calibrated_dti": rc["holdout_dti"]["secondary_sgmc_off_catalogue"]["sgmc_prevalence_calibrated_dti"],
        "on_catalogue_pixels": 0,
        "anchor": {
            "role": "PORTFOLIO LIVE CHAMPION (0.2778 ORGANIZER-CONFIRMED — already submitted; do not resubmit)",
            "path": champ_tif_rel,
            "zip_path": champ_zip_rel,
            "zip_sha256": "5a6f3ee02e6392089d53361976dbc9d5dec43ef4205001097c6806fe487bef11",
            "zip_bytes": 186378,
            "note": "37,654 dots; B=2 prune of solo (0.2708); highest-scoring artifact across all GEMSDOE sites",
        },
        "pack": [
            {
                "role": "SECONDARY — NaN-outside twin of Arena8a unique deliverable",
                "path": nan_rel,
                "sha256": rc["nan_twin_sha256"],
                "bytes": nan_bytes,
                "positive_px": rc["emitted_positive_pixels"],
                "note": "Identical 44,090 in-footprint binary predictions; NaN outside footprint (DO NOT SUBMIT — research audit twin)",
            },
            {
                "role": "HISTORICAL PORTFOLIO CHAMPION (0.2778 — ALREADY SUBMITTED, DO NOT RESUBMIT)",
                "path": champ_tif_rel,
                "sha256": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
                "bytes": 219065,
                "positive_px": 37654,
                "note": "ORGANIZER-CONFIRMED 0.2778 (owner receipt 2026-10-25); valid ZIP 186,378 B sha256 5a6f3ee0...",
            },
            {
                "role": "AVAILABLE DOWNLOAD",
                "path": "docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
                "sha256": "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
                "bytes": 1603424,
                "positive_px": 44090,
                "note": "kept for audit trail (0.2600 owner-reported parent)",
            },
        ],
        "rule": rc["mechanism"],
        "provenance": (
            f"built {rc['generated_utc']} on {rc['session_branch']} from {rc['holdout_dti']['primary_visible_only_holdout']['evaluator_version']}, "
            f"22,232 withheld positives, 12/12 + strict [0,1] checks PASS, canary max AUC {rc['automated_gates']['G1_leakage_canary_auc_le_090']['worst_auc']} <= 0.90"
        ),
    }
    (ROOT / "registry" / "submission_build.json").write_text(json.dumps(sub_build, indent=1) + "\n")

    # 2. Update registry/hypotheses.json with A8A-H1..A8A-H5 (idempotent)
    hyp_path = ROOT / "registry" / "hypotheses.json"
    hyp_doc = json.loads(hyp_path.read_text())
    existing = [h for h in hyp_doc["hypotheses"] if not str(h.get("id", "")).startswith("A8A-")]
    a8a_hyps = [
        {
            "id": "A8A-H1",
            "rank": 1,
            "status": "measured (HOLDOUT WIN +0.0076 vs D2.8; Gate G5 SGMC NEGATIVE — DO NOT SUBMIT)",
            "title": "Multi-Domain Ridge-Crest Concordance (MDRC): Valid-Tile-Aware 1 m LiDAR Dipole + True RTP/TMI Magnetic Tilt + Gravity/MT Step + Label-Free Hydrothermal Conduits",
            "layers": [
                "lidar_scarp_features_u8 (b2 step_max, b3/b4 lapneg*lappos, b7/b8 |downface-upface|, b9 cross, b10 coh100, b11 strike, b12 valid)",
                "training_features (rtp b2, tmi b1, tmi_hg b3, iso_grav_anom b13, grav_hg b18, depth_to_base_surf b15, cond_surf b17, det_elev b12, geod_shearrate b8)",
                "geodawn_rad_u8 (K, eU, eTh) + gdr_wellspring_in_footprint.csv (temp_c, na_k_c, chalcedony_c; dist_known_fault_px dropped)"
            ],
            "signature": "One-sided 1 m LiDAR crest-toe dipole (missing tiles routed via native NaN) concordant with true Miller-Singh (1994) RTP/TMI tilt-zero lineaments, gravity/MT basement steps, and K/Th + geothermometer halos; sharpened onto 1-px cross-strike crests",
            "why_off_catalogue": "Catches sub-metre degraded scarps on valid 3DEP tiles and covered sub-alluvial transfer/step-over faults where >=2 subsurface/hydrothermal domains align; dual-head piedmont weighting mitigates range-front domain shift",
            "differs_from_repo": "Fixes IR-32-BAND6-TC-01 (Band 6 is radiometric TC, not magnetic tilt) and IR-32-LIDAR-BANDS-01 (12-band LiDAR mis-indexing + 24.6% missing-tile zeros); adds 1-px cross-strike crest sharpening; Mimic: fluvial terrace risers / gullies (suppressed by |downface-upface| & >=2-domain gate)",
            "expected_dti": "HOLDOUT-DTI 0.10679 [0.08765, 0.12850] (beats CTRL 0.09893 & D2.8 0.09920; SGMC-cal 0.05509 < 0.06412)",
            "cost": "3/3 session experiments (~14 min CPU)",
            "data_status": "all inputs hash-pinned in .cache/gems_data",
            "implementation": "src/gems32/mdrc.py; scripts/arena8a_run_experiments.py; evidence/arena8a_run_card.json",
            "measured": {
                "visible_only_holdout_dti_44090": round(rc["holdout_dti"]["primary_visible_only_holdout"]["pooled_dti"], 5),
                "visible_only_holdout_dti_37654": round(exp3["arms_compared"]["MDRC_Crest_37654"]["visible_only_holdout"]["pooled_dti"], 5),
                "ctrl_35ch_visible_only_holdout": 0.09893,
                "d28_vis_b2_holdout": 0.09920,
                "unsupervised_4domain_sgmc_cal": round(exp1["solo_unsupervised_domains"]["MDRC_Unsup_4Domain"]["sgmc_prevalence_calibrated_dti"], 5),
                "supervised_sgmc_cal": round(rc["holdout_dti"]["secondary_sgmc_off_catalogue"]["sgmc_prevalence_calibrated_dti"], 5),
            },
            "verdict": "NEGATIVE (DO NOT SPEND SLOT): beats CTRL-35ch and D2.8 on visible-only HOLDOUT-DTI (7/8 cells), but supervised y=0 training on incomplete catalogue suppresses pre-Quaternary SGMC faults (0.05509 < 0.06412)."
        },
        {
            "id": "A8A-H2",
            "rank": 2,
            "status": "preregistered (channel tested inside MDRC; standalone PU arm deferred)",
            "title": "Salem RTP Magnetic Tilt-Depth vs Gravity Basement-Depth Discordance (Intra-Basin Faulted Volcanics)",
            "layers": [
                "rtp (2), depth_to_base_surf (15), iso_grav_anom (13), grav_hg (18), mag_up150 (geodawn_extensions_u8)"
            ],
            "signature": "Half-width between +/-pi/4 Miller-Singh RTP tilt contours (z_tilt) strictly shallower than gravity depth_to_base_surf (z_tilt << z_base) along a persistence ridge",
            "why_off_catalogue": "Detects blind intra-basin faulted Neogene basalts/tuffs buried 100-400 m beneath playa/alluvial cover above 1.5-3 km Mesozoic basement, invisible to surface mapping",
            "differs_from_repo": "First quantitative comparison of Salem et al. (2007) magnetic source depth against gravity basement depth; Mimic: un-faulted buried volcanic flow margins / dikes",
            "expected_dti": "medium (+0.003 to +0.008 in PU ensemble)",
            "cost": "low (derived from cached rasters)",
            "data_status": "in-repo hash-pinned",
            "verdict": "Channel mag_salem_tilt_depth_discord verified leak-free in EXP1 canary; standalone positive-unlabeled test queued for next session."
        },
        {
            "id": "A8A-H3",
            "rank": 3,
            "status": "preregistered (solo Domain IV measured in EXP1: HOLDOUT-DTI 0.04346, SGMC 0.04669)",
            "title": "Potassic Alteration Edge (K/Th) + Magnetite-Destruction Trough + MT Smectite Clay-Cap Boundary",
            "layers": [
                "geodawn_rad_u8 (K, eTh, eU), rtp (2), tmi_hg (3), cond_surf (17), gdr_wellspring_in_footprint.csv, gdr_volcanic_vents_in_footprint.csv"
            ],
            "signature": "High K/eTh potassic/adularia alteration gradient co-located with RTP demagnetization trough, MT cond_surf clay-cap edge, and >60 C geothermometer outflow",
            "why_off_catalogue": "Upwelling geothermal brines sulfidize magnetite and enrich potassium along blind permeable fault intersections even without Quaternary surface rupture",
            "differs_from_repo": "Pairs K/Th compositional gradients with magnetite-destruction troughs and label-free GDR geothermometers (dropping dist_known_fault_px); Mimic: un-faulted rhyolite tuff contacts & evaporitic playa clays",
            "expected_dti": "solo HOLDOUT-DTI 0.04346; SGMC-cal 0.04669",
            "cost": "low",
            "data_status": "in-repo hash-pinned",
            "verdict": "Solo unsupervised Domain IV measured in EXP1; strongest as a corroborating hydrothermal gate rather than standalone detector."
        },
        {
            "id": "A8A-H4",
            "rank": 4,
            "status": "preregistered (deferred under 3-experiment budget)",
            "title": "Walker Lane Transtensional Strike-Deflection & Relay-Ramp Curvature",
            "layers": [
                "lidar_scarp_features_u8 (b10 coh100, b11 strike, b12 valid), geod_shearrate (8), geod_2ndinv (9), det_elev (12)"
            ],
            "signature": "High angular gradient of doubled-angle scarp strike |grad(cos 2theta, sin 2theta)| inside elevated geodetic shear-rate zones (>70th pct) with saddle curvature",
            "why_off_catalogue": "Regional catalogues map master range-bounding faults as disconnected lines, systematically omitting curved 0.5-3 km accommodation faults across relay ramps where geothermal permeability peaks",
            "differs_from_repo": "Prior relay bridges (GEMSDOE27 T-v2, H33-5) extrapolate synthetically from mapped fault tips (violating B-gates or blind to unmapped pairs); A8A-H4 measures strike rotation directly from 1 m LiDAR; Mimic: Lake Lahontan pluvial shorelines",
            "expected_dti": "targeted local gain in Walker Lane transtensional step-overs",
            "cost": "low",
            "data_status": "in-repo hash-pinned",
            "verdict": "Deferred to respect strict 3-experiment parallel-run budget."
        },
        {
            "id": "A8A-H5",
            "rank": 5,
            "status": "DATA-BLOCKED in sandbox (official free USGS URLs verified)",
            "title": "Sub-Kilometre Relocated Microseismic Planes & 2020 M6.5 Monte Cristo Range Distributed Surface Ruptures",
            "layers": [
                "USGS ComCat FDSN Event API (earthquake.usgs.gov/fdsnws/event/1/query), USGS ScienceBase 606f657fd34ef99870188ee5, Zenodo 5302368, ieq_n100a15 (16)"
            ],
            "signature": "RANSAC-fitted planar epicentre/hypocentre alignments (<500 m localization) + Koehler et al. (2021) field-mapped sinistral/oblique 2020 MCRE rupture traces",
            "why_off_catalogue": "Directly images active seismogenic faults at 2-12 km depth and the 28 km 2020 Monte Cristo rupture across previously unmapped Candelaria/playa faults where Band 16 (100 km kernel, r_3km=0.9935) is spatially constant",
            "differs_from_repo": "Replaces 100 km blurred seismic band with sub-km event alignments paired with RTP/LiDAR corroboration; Mimic: mining blasts & un-faulted geothermal swarm clouds",
            "expected_dti": "high in SE Walker Lane / Monte Cristo domain once prefetched",
            "cost": "external prefetch step required outside sandbox",
            "data_status": "official free public-domain USGS/Zenodo URLs verified; blocked by sandbox egress allowlist",
            "verdict": "Explicitly flagged DATA-BLOCKED in this sandbox; ready for CI/host prefetch."
        },
    ]
    hyp_doc["hypotheses"] = existing + a8a_hyps
    hyp_doc["updated_utc"] = "2026-10-26"
    hyp_path.write_text(json.dumps(hyp_doc, indent=1) + "\n")

    # 3. Update registry/irregularities.json with newly audited/resolved items (idempotent)
    irr_path = ROOT / "registry" / "irregularities.json"
    irr_doc = json.loads(irr_path.read_text())
    base_items = [it for it in irr_doc["items"] if not str(it.get("id", "")).startswith("IR-A8A-")]
    for it in base_items:
        if it.get("id") == "IR-32-INSTR-03":
            it["severity"] = "high (FIXED 2026-10-26 in GEMSDOE32-HOLDOUT-v3-visible-only)"
            it["mitigation"] = (
                "FIXED in place in src/gems32/holdout.py (EVALUATOR_VERSION = GEMSDOE32-HOLDOUT-v3-visible-only): "
                "PreparedCell now stores visible_sub, d_visible_sub, and visible_full, and evaluate_visible_only_holdout "
                "derives B-collars strictly from each draw's visible faults. Verified on D2.8: B=0 (0.09674) < B=1 (0.09898) "
                "< B=2 (0.09920, global peak matching live 0.2778!) > B=3 (0.09710)."
            )
    new_irrs = [
        {
            "id": "IR-A8A-BAND6-TC-01",
            "severity": "high (FIXED in MDRC)",
            "statement": "Band 6 ('tc') of training_features.tif was described in prior repo docs and IR-32-REDUND-01 / H62-1 as a 'magnetic tilt-angle derivative for edge detection'. Byte-level correlation against GeoDAWN external rasters proves Band 6 is airborne gamma-ray Radiometric Total Count (TC, Pearson r = +0.997140 with geodawn_rad_u8.tif Band 4 TC) and has near-zero correlation (r = +0.012796) with true Miller-Singh magnetic tilt arctan(V/H). This directly explains why H62-1 (taking zero-crossings of Band 6) failed at 0.5058 AUC.",
            "mitigation": "src/gems32/mdrc.py computes true Miller-Singh (1994) magnetic tilt zero-crossings and Salem tilt-depth directly from Band 2 (rtp) and Band 1 (tmi) via FFT vertical derivatives, while treating Band 6 and geodawn_rad_u8 K/U/Th as radiometric lithology/alteration channels."
        },
        {
            "id": "IR-A8A-LIDAR-BANDS-01",
            "severity": "high (FIXED in MDRC)",
            "statement": "lidar_scarp_features_u8.tif has 12 uint8 bands where Band 12 ('valid') is >0 on only 75.37% of the submission footprint (24.63% missing 3DEP 1 m LiDAR tiles encoded as 0). Prior src/gems32/h35_new.py read bands (1, 2, 5) assuming (ex_max, step_max, coh) without checking Band 12 valid, conflating missing LiDAR tiles with scarp-free terrain and mis-indexing Band 5 (p90_grad) as coherence (Band 10).",
            "mitigation": "src/gems32/mdrc.py reads exact band descriptions (b2 step_max, b3/b4 lapneg/lappos, b7/b8 downface/upface, b9 cross, b10 coh100, b11 strike, b12 valid) and sets missing tiles (b12 == 0) to native NaN for HistGradientBoostingClassifier missing-value routing."
        },
        {
            "id": "IR-A8A-GDR-LEAK-01",
            "severity": "high (mitigated & unit-tested)",
            "statement": "Both gdr_wellspring_in_footprint.csv (27,092 rows) and gdr_volcanic_vents_in_footprint.csv (21 rows) contain a precomputed column named dist_known_fault_px derived from the full fault catalogue. Including that column in any feature or halo leaks withheld test faults.",
            "mitigation": "src/gems32/mdrc.py explicitly drops dist_known_fault_px, asserts 'dist_known_fault_px' is absent before rasterization, and verifies all 57 channels via EXP1 leakage canary (max AUC = 0.62173 <= 0.90)."
        },
        {
            "id": "IR-A8A-DUP-PRIMARY-01",
            "severity": "high (FIXED 2026-10-26)",
            "statement": "Prior registry/submission_build.json headlined H32-WIN-46090 (D2.8 minus 400 speckles + 2400 dots, ~94.8% within-3px overlap with D2.8, violating the Parallel-Run <=70% uniqueness rule), carried a 0-byte all-zeros zip hash (0000...0000), and still claimed 'NO ORGANISER SCORE EXISTS for this or any artifact in this repository' despite h33-h33-2-b2's owner-reported 0.2778 receipt.",
            "mitigation": "registry/submission_build.json updated to point to the genuinely unique Arena8a deliverable (surface |rho|=0.4209, within-3px=64.96%<=70%, verified 197,576-byte zip sha256 c87912bf...), stamped clearly with automated verdict NEGATIVE / DO-NOT-SUBMIT, while recording h33-h33-2-b2 (0.2778, verified 186,378-byte zip sha256 5a6f3ee0...) accurately as the already-submitted portfolio champion."
        },
        {
            "id": "IR-A8A-PU-BIAS-01",
            "severity": "high (scientific finding)",
            "statement": "EXP1 vs EXP2/EXP3 revealed why supervised GBMs trained on labels.tif underperform H19-5/H33 on off-catalogue USGS SGMC faults even when they win visible-only holdout: label-free D1_LiDAR_Dipole (0.10267) and MDRC_Unsup_4Domain (0.07651) beat CHAMPION h33-2-b2 (0.06412) on SGMC, whereas supervised HistGB (treating ~labels as y=0 true negatives) suppresses real pre-Quaternary SGMC faults present inside ~labels (pulling SGMC-cal down to 0.05509).",
            "mitigation": "Gate G5 faithfully caught this off-catalogue suppression and issued an automated NEGATIVE (DO NOT SUBMIT) verdict; next-session path is positive-unlabeled (Elkan-Noto / anchor-set) learning rather than standard binary cross-entropy on ~labels."
        },
    ]
    irr_doc["items"] = base_items + new_irrs
    irr_path.write_text(json.dumps(irr_doc, indent=1) + "\n")

    # 4. Update registry/sources.json with 2026-10-25 leaderboard & official USGS/ScienceBase links
    src_path = ROOT / "registry" / "sources.json"
    src_doc = json.loads(src_path.read_text())
    srcs = [s for s in src_doc["sources"] if not str(s.get("id", "")).startswith("a8a_")]
    for s in srcs:
        if s.get("id") == "leaderboard":
            s["status"] = (
                "verified snapshots: 2026-10-03 (#1 DARD 0.3195), 2026-10-04 (#1 nchuzhoy 0.3262), "
                "2026-10-25 (#1 xiaofanhu 0.4413, #2 cfld__ 0.3916, #3 Batik Shirt Brothers 0.3904)"
            )
    srcs.extend([
        {
            "id": "a8a_usgs_3dep",
            "title": "USGS 3D Elevation Program (3DEP) 1-Meter DEM Specification",
            "url": "https://www.usgs.gov/3d-elevation-program",
            "role": "official source of 1 m LiDAR scarp derivatives (Domain I)",
            "status": "official public-domain USGS program; hash-pinned derivatives in .cache/gems_data/external"
        },
        {
            "id": "a8a_usgs_sgmc",
            "title": "USGS State Geologic Map Compilation (SGMC) Geodatabase (Horton et al., 2017)",
            "url": "https://doi.org/10.3133/ds1052",
            "role": "off-catalogue pre-Quaternary + bedrock fault holdout benchmark (62,703 off-cat px)",
            "status": "official USGS Data Series 1052; rasterized in derived_sgmc_faults_100m_u8.tif"
        },
        {
            "id": "a8a_usgs_comcat_api",
            "title": "USGS ComCat FDSN Event Web Service API",
            "url": "https://earthquake.usgs.gov/fdsnws/event/1/",
            "role": "A8A-H5 external microseismic catalogue source (free, public domain)",
            "status": "official free API; egress-blocked inside sandbox (deferred)"
        },
        {
            "id": "a8a_sciencebase_mcre",
            "title": "USGS ScienceBase 2020 M6.5 Monte Cristo Range Surface Rupture Dataset",
            "url": "https://www.sciencebase.gov/catalog/item/606f657fd34ef99870188ee5",
            "role": "A8A-H5 external surface-rupture vector dataset (Koehler et al., 2021)",
            "status": "official free USGS data release; egress-blocked inside sandbox (deferred)"
        },
    ])
    src_doc["sources"] = srcs
    src_path.write_text(json.dumps(src_doc, indent=1) + "\n")

    # 5. Append Arena8a row to docs/score-ledger.csv (idempotent)
    ledger_path = ROOT / "docs" / "score-ledger.csv"
    with ledger_path.open("r", newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    header, rows = reader[0], reader[1:]
    rows = [r for r in rows if not (len(r) > 0 and r[0] == "GEMSDOE32-Arena8a")]
    rows.append([
        "GEMSDOE32-Arena8a",
        Path(tif_rel).stem,
        "UNSCORED-negative",
        (
            f"HOLDOUT-DTI v3 visible-only {rc['holdout_dti']['primary_visible_only_holdout']['pooled_dti']:.4f} "
            f"[{rc['holdout_dti']['primary_visible_only_holdout']['ci95'][0]:.4f}-"
            f"{rc['holdout_dti']['primary_visible_only_holdout']['ci95'][1]:.4f}] (beats CTRL 0.0989 & D2.8 0.0992; "
            f"SGMC-cal {rc['holdout_dti']['secondary_sgmc_off_catalogue']['sgmc_prevalence_calibrated_dti']:.4f})"
        ),
        "OK TO DOWNLOAD; DO NOT SUBMIT (Gate G5 SGMC 0.0551 < champion 0.0641)",
        "https://buffedlizard55-lab.github.io/GEMSDOE32/docs/executive-summary.html",
        f"Unique TIF sha256 {rc['raster_sha256'][:12]} (44090 dots); automated verdict negative",
        "holdout-local",
        "2026-10-26",
    ])
    with ledger_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)

    print("Updated registry/{submission_build,hypotheses,irregularities,sources}.json and docs/score-ledger.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
