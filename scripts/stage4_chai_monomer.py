#!/usr/bin/env python3
"""
Stage 4: Chai-1 Monomer Stability — Batch Runner
Runs 100 designs one by one via: modal run modal_chai1.py --input-faa <fasta>
Parses pLDDT from output CIFs, applies filters, saves results.
"""

import os
import sys
import time
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_CSV = "/home/ubuntu/.openclaw/workspace/out/stage4_top100_input.csv"
OUTPUT_DIR = "/home/ubuntu/.openclaw/workspace/out/stage4"
CHAI_SCRIPT = "/home/ubuntu/.openclaw/workspace/modal_chai1.py"
WORKSPACE = "/home/ubuntu/.openclaw/workspace"

PLDDT_THRESHOLD = 80.0       # mean monomer pLDDT (Chai-1 outputs 0-100)
DISORDER_THRESHOLD = 0.10    # max fraction residues pLDDT < 50

os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_plddt_from_cif(cif_path):
    """Parse CA atom pLDDT values from a Chai-1 CIF output file."""
    vals = []
    try:
        col_map = {}
        col_idx = 0
        in_atom_loop = False
        with open(cif_path) as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('loop_'):
                    col_map = {}
                    col_idx = 0
                    in_atom_loop = False
                    continue
                if line.startswith('_atom_site.'):
                    field = line.strip().split('.')[-1]
                    col_map[field] = col_idx
                    col_idx += 1
                    in_atom_loop = True
                    continue
                if in_atom_loop and (line.startswith('ATOM') or line.startswith('HETATM')):
                    parts = line.split()
                    try:
                        atom_id_col = col_map.get('label_atom_id', 3)
                        b_iso_col = col_map.get('B_iso_or_equiv', 14)
                        atom_name = parts[atom_id_col]
                        b_val = float(parts[b_iso_col])
                        if atom_name == 'CA':
                            vals.append(b_val)
                    except (IndexError, ValueError, KeyError):
                        pass
    except Exception as e:
        pass
    return vals


# ── Load top 100 ──────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV)
print(f"Loaded {len(df)} designs for Stage 4")
print(f"Seq length: {df['seq_len'].min()}–{df['seq_len'].max()} aa")
print(f"Filter: monomer pLDDT ≥ {PLDDT_THRESHOLD}, disorder < {DISORDER_THRESHOLD*100:.0f}%")
print(f"GPU: A100 via Modal, ~1.5 min/design, est. cost ~$7\n")

results = []
failed = []
t_start = time.time()

for idx, row in df.iterrows():
    design_id = row['design_id']
    sequence = row['sequence']
    seq_len = int(row['seq_len'])
    rank = idx + 1

    # ETA
    elapsed_total = time.time() - t_start
    eta_str = ""
    if rank > 2:
        avg_per = elapsed_total / (rank - 1)
        remaining = avg_per * (100 - rank + 1)
        eta_str = f"  ETA ~{remaining/60:.0f}m"

    print(f"[{rank:3d}/100] {design_id} ({seq_len}aa){eta_str}", end=" ", flush=True)

    # Write temp FASTA — protein monomer only (no ligand → monomer fold)
    fasta_content = f">protein|name={design_id}\n{sequence}\n"
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.faa', delete=False, dir=WORKSPACE
    ) as f:
        f.write(fasta_content)
        fasta_path = f.name

    chai_outdir = f"{OUTPUT_DIR}/chai_out"

    try:
        t0 = time.time()
        cmd = [
            "modal", "run", CHAI_SCRIPT,
            "--input-faa", fasta_path,
            "--out-dir", chai_outdir,
            "--run-name", design_id,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=360, cwd=WORKSPACE
        )
        elapsed = time.time() - t0

        if result.returncode != 0:
            err_snippet = (result.stderr or result.stdout or "")[-300:].strip()
            print(f"→ FAILED (rc={result.returncode})")
            failed.append({'design_id': design_id, 'error': err_snippet})
            continue

        # Find output CIFs
        out_path = Path(chai_outdir) / design_id
        cif_files = list(out_path.glob("pred.model_idx_*.cif"))

        if not cif_files:
            print("→ NO CIF OUTPUT")
            failed.append({'design_id': design_id, 'error': 'no cif files found'})
            continue

        # Pick model with highest mean pLDDT
        best_vals = None
        for cif_path in sorted(cif_files):
            vals = parse_plddt_from_cif(cif_path)
            if vals:
                if best_vals is None or np.mean(vals) > np.mean(best_vals):
                    best_vals = vals

        if not best_vals:
            print("→ pLDDT PARSE FAILED")
            failed.append({'design_id': design_id, 'error': 'plddt parse failed'})
            continue

        arr = np.array(best_vals)
        mean_plddt = float(np.mean(arr))
        disorder_frac = float(np.mean(arr < 50))

        # Chai-1 uses 0-100 scale directly; if values look 0-1, scale up
        if mean_plddt < 1.5:
            mean_plddt *= 100
            arr *= 100
            disorder_frac = float(np.mean(arr < 50))

        passes = (mean_plddt >= PLDDT_THRESHOLD) and (disorder_frac < DISORDER_THRESHOLD)
        tag = "✅ PASS" if passes else "✗"
        print(f"→ {tag}  pLDDT={mean_plddt:.1f}  disorder={disorder_frac:.1%}  ({elapsed:.0f}s)")

        results.append({
            'rank_stage3': rank,
            'design_id': design_id,
            'sequence': sequence,
            'seq_len': seq_len,
            'composite_score_s3': float(row['composite_score']),
            'interface_pLDDT_s3': float(row['interface_pLDDT']),
            'buried_surface_area': float(row['buried_surface_area']),
            'min_pae': float(row['min_pae']),
            'design_ptm': float(row['design_ptm']),
            'hbonds': int(row['hbonds']),
            'batch': row['batch'],
            'monomer_pLDDT': mean_plddt,
            'disorder_fraction': disorder_frac,
            'passes_stage4': passes,
        })

    except subprocess.TimeoutExpired:
        print("→ TIMEOUT (360s)")
        failed.append({'design_id': design_id, 'error': 'timeout 360s'})
    except Exception as e:
        print(f"→ ERROR: {e}")
        failed.append({'design_id': design_id, 'error': str(e)})
    finally:
        if os.path.exists(fasta_path):
            os.unlink(fasta_path)

    # Checkpoint every 10
    if rank % 10 == 0 and results:
        tmp = pd.DataFrame(results)
        tmp.to_csv(f"{OUTPUT_DIR}/stage4_checkpoint.csv", index=False)
        n_pass = tmp['passes_stage4'].sum()
        print(f"  --- Checkpoint {rank}/100: {n_pass} passing so far ---")


# ── Save final results ─────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("STAGE 4 COMPLETE")
print(f"{'='*60}")

if results:
    rdf = pd.DataFrame(results)
    rdf.to_csv(f"{OUTPUT_DIR}/stage4_all_results.csv", index=False)

    passing = rdf[rdf['passes_stage4']].sort_values('monomer_pLDDT', ascending=False).reset_index(drop=True)
    passing.to_csv(f"{OUTPUT_DIR}/stage4_passing.csv", index=False)

    print(f"  Completed:  {len(rdf)}/100")
    print(f"  Failed:     {len(failed)}")
    print(f"  ✅ PASS (pLDDT≥{PLDDT_THRESHOLD:.0f} + disorder<{DISORDER_THRESHOLD:.0%}): {len(passing)}")

    if len(passing) > 0:
        print(f"\n  Top passing designs:")
        cols = ['design_id','monomer_pLDDT','disorder_fraction',
                'interface_pLDDT_s3','design_ptm','min_pae','hbonds','seq_len']
        print(passing[cols].head(20).to_string(index=False))
    else:
        print("\n  No designs passed. Consider relaxing threshold to pLDDT ≥ 75.")
        # Show top 10 by monomer_pLDDT anyway
        top_any = rdf.sort_values('monomer_pLDDT', ascending=False).head(10)
        print("\n  Top 10 by monomer pLDDT (regardless of filter):")
        print(top_any[['design_id','monomer_pLDDT','disorder_fraction']].to_string(index=False))
else:
    print("  No results collected — check Modal setup.")

if failed:
    fdf = pd.DataFrame(failed)
    fdf.to_csv(f"{OUTPUT_DIR}/stage4_failed.csv", index=False)
    print(f"\n  Failed ({len(failed)}): {', '.join(fdf['design_id'].head(5).tolist())}...")

total_time = time.time() - t_start
print(f"\n  Total wall time: {total_time/60:.1f} min")
print(f"  Output: {OUTPUT_DIR}/")
