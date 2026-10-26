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

    # 1. Update evidence/arena8a_run_card.json with post-merge sibling uniqueness audit (H42, R6-1, H-GEO-CONDUIT, 13gems lattice),
    #    write registry/arena8a_submission.json, preserve registry/submission_build.json's current_release_review contract,
    #    and update registry/current_status.json with Arena8a as newest_unique while keeping h42_candidate + round6_candidate.
    tif_rel = rc["raster_path"]
    zip_rel = rc["zip_path"]
    nan_rel = f"docs/downloads/{rc['nan_twin_filename']}"
    tif_bytes = (ROOT / tif_rel).stat().st_size
    nan_bytes = (ROOT / nan_rel).stat().st_size

    rc["correlation_and_overlap_vs_registry"]["post_merge_sibling_audit_2026_10_26"] = {
        "H42_HWCI": {"ref_dots": 37654, "spearman": 0.06003, "cand_in_3px_ref": 0.22064, "ref_in_3px_cand": 0.42551, "sym_within_3px": 0.22064},
        "R6_STEPPROFILE": {"ref_dots": 37654, "spearman": 0.00251, "cand_in_3px_ref": 0.19367, "ref_in_3px_cand": 0.21520, "sym_within_3px": 0.19367},
        "H_GEO_CONDUIT": {"ref_dots": 37654, "spearman": 0.07314, "cand_in_3px_ref": 0.33575, "ref_in_3px_cand": 0.41252, "sym_within_3px": 0.33575},
        "CALIB_LATTICE_S5_206895": {
            "ref_dots": 206895,
            "spearman": 0.00447,
            "cand_in_3px_ref_literal": 0.99036,
            "ref_in_3px_cand": 0.15872,
            "sym_within_3px": 0.15872,
            "note": "Synthetic 5-px covering grid (IR-42-UNIQ-01 / IR-A41-UNIQ-01): random dots score 0.9988 and 0.2778 champion scores 0.9992 on one-way within-3px; reported literally and symmetrically.",
        },
    }
    (ROOT / "evidence" / "arena8a_run_card.json").write_text(json.dumps(rc, indent=2) + "\n")

    champ_tif_rel = "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    champ_zip_rel = "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.zip"

    arena8a_sub = {
        "name": Path(tif_rel).stem,
        "note": rc["submission_note"],
        "verdict": rc["verdict"],
        "ok_to_download": rc["ok_to_download"],
        "ok_to_submit": rc["ok_to_submit"],
        "file": {
            "path": tif_rel,
            "sha256": rc["raster_sha256"],
            "bytes": tif_bytes,
            "positive_px": rc["emitted_positive_pixels"],
        },
        "file_nan": {
            "path": nan_rel,
            "sha256": rc["nan_twin_sha256"],
            "bytes": nan_bytes,
            "positive_px": rc["emitted_positive_pixels"],
        },
        "zip": {
            "path": zip_rel,
            "sha256": rc["zip_sha256"],
            "bytes": rc["zip_bytes"],
        },
        "candidate_id": rc["submission_name"],
        "hypothesis": "A8A-H1 (MDRC_Crest_CreditBar)",
        "visible_only_holdout_dti": rc["holdout_dti"]["primary_visible_only_holdout"]["pooled_dti"],
        "visible_only_holdout_ci95": rc["holdout_dti"]["primary_visible_only_holdout"]["ci95"],
        "sgmc_prevalence_calibrated_dti": rc["holdout_dti"]["secondary_sgmc_off_catalogue"]["sgmc_prevalence_calibrated_dti"],
        "anchor_champion": {
            "path": champ_tif_rel,
            "zip_path": champ_zip_rel,
            "zip_sha256": "5a6f3ee02e6392089d53361976dbc9d5dec43ef4205001097c6806fe487bef11",
            "zip_bytes": 186378,
        },
        "run_card": "evidence/arena8a_run_card.json",
    }
    (ROOT / "registry" / "arena8a_submission.json").write_text(json.dumps(arena8a_sub, indent=2) + "\n")

    # Preserve origin/main's registry/submission_build.json contract (current_release_review sha256)
    sub_build_path = ROOT / "registry" / "submission_build.json"
    sub_build = json.loads(sub_build_path.read_text())
    sub_build["ok_to_submit"] = False
    sub_build["verdict"] = "negative"
    sub_build["arena8a_candidate"] = "registry/arena8a_submission.json"
    sub_build_path.write_text(json.dumps(sub_build, indent=2) + "\n")

    # Update registry/current_status.json: promote Arena8a MDRC to newest_unique (DO NOT SUBMIT) while keeping h42_candidate & round6_candidate
    cs_path = ROOT / "registry" / "current_status.json"
    if cs_path.exists():
        cs = json.loads(cs_path.read_text())
        prev_newest = cs.get("newest_unique") or {}
        if prev_newest and "h42-hwci" in str(prev_newest.get("file", "")) and "h42_candidate" not in cs:
            cs["h42_candidate"] = prev_newest
        cs["updated_utc"] = "2026-10-26T02:05:00Z"
        cs["any_file_ok_to_submit"] = False
        cs["newest_unique"] = {
            "file": tif_rel,
            "zip": zip_rel,
            "receipt": f"docs/downloads/checks-{Path(tif_rel).name}.json",
            "sha256": rc["raster_sha256"],
            "bytes": tif_bytes,
            "dots": rc["emitted_positive_pixels"],
            "submission_name": rc["submission_name"],
            "note": rc["submission_note"],
            "verdict": "DO NOT SUBMIT",
            "ok_to_submit": False,
            "hypothesis": "A8A-H1 Multi-Domain Ridge-Crest Concordance (MDRC, 44,090 dots, B=2)",
            "gates": {
                "G1_canary": True,
                "G2_format_01": True,
                "G3_lane_unique_genuine": True,
                "G4_visible_only_holdout_vs_ctrl_and_d28": True,
                "G4_subbar_3x_submodular_random": False,
                "G5_sgmc_beats_champion": False,
            },
            "reasons": [
                "Fold-local visible-only HOLDOUT-DTI (GEMSDOE32-HOLDOUT-v3-visible-only, 22,232 withheld positives) = 0.1068 [0.0877, 0.1285], beating BOTH CTRL-35ch (0.0989) and D2.8 vis-B2 (0.0992, winning 7/8 cells, paired diff 95% CI [+0.0040, +0.0111]), while reaching 2.29x vs the conservative 3.0x submodular-random sub-bar (0.1398).",
                "Gate G5 FAILED on off-catalogue USGS SGMC faults (62,703 off-cat px): MDRC scores 0.0551 (beating CTRL-35ch 0.0502 by +9.8%), but trails the 0.2778 champion (0.0641) because binary cross-entropy on ~labels treats unmapped pre-Quaternary SGMC faults as y=0 negatives (IR-A8A-PU-BIAS-01; unsupervised D1_LiDAR_Dipole scored 0.1027 and MDRC_Unsup_4Domain scored 0.0765).",
                "Lane-unique against all 19 genuine detector/submission rasters (pre-placement surface |rho| <= 0.4209 <= 0.90; final within-3px <= 64.96% <= 70%: 52.89% vs 0.2778 champion, 22.06% vs H42, 19.37% vs R6-1, 33.58% vs H-GEO-CONDUIT; literal one-way overlap vs 206,895-dot 5-px calibration lattice is 99.04% vs 99.92% for champion, IR-42-UNIQ-01).",
            ],
            "holdout": {
                "MDRC_Crest_CreditBar_44090": {"dti": 0.1068, "ci95": [0.0877, 0.1285]},
                "MDRC_Crest_37654": {"dti": 0.1055, "ci95": [0.0857, 0.1277]},
                "D28_vis_B2_incumbent": {"dti": 0.0992, "ci95": [0.0815, 0.1204]},
                "CTRL_35ch_OOF": {"dti": 0.0989, "ci95": [0.0802, 0.1197]},
                "RANDOM_B2_submod": {"dti": 0.0466, "ci95": [0.0369, 0.0580]},
            },
            "holdout_label": "HOLDOUT-DTI, GEMSDOE32-HOLDOUT-v3-visible-only (fold-local B=2), 22,232 withheld positives, 95% CI",
            "off_catalogue_instrument": {
                "D1_LiDAR_Dipole_unsup": {"dti": 0.1027, "ci95": [0.0910, 0.1145]},
                "MDRC_Unsup_4Domain": {"dti": 0.0765, "ci95": [0.0665, 0.0870]},
                "CHAMPION_0.2778": {"dti": 0.0641, "ci95": [0.0555, 0.0732]},
                "MDRC_Crest_CreditBar_44090": {"dti": 0.0551, "ci95": [0.0472, 0.0634]},
                "CTRL_35ch_OOF": {"dti": 0.0502, "ci95": [0.0426, 0.0582]},
            },
            "off_catalogue_label": "SGMC prevalence-calibrated DTI (>200 m off-catalogue, 62,703 px)",
            "uniqueness": {
                "registry_rasters": 20,
                "max_spearman": 0.4209,
                "worst_informative_overlap": 0.6496,
                "worst_informative_raster": "GEMSDOE25/30:d2.8-44090 (52.89% vs 0.2778 champion; 19.37% vs R6-1; 22.06% vs H42)",
                "calibration_lattice_oneway_fraction": 0.99036,
            },
            "run_card": "evidence/arena8a_run_card.json",
        }
        cs_path.write_text(json.dumps(cs, indent=1) + "\n")

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
