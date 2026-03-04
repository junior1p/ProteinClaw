#!/usr/bin/env python3
"""
Stage 4 Plan B: Chai-1 Monomer Stability — 8 designs
Top 3 (pLDDT≥75 from free run) + 5 relaxed elites
Est. cost: ~$0.56 on Modal A100
"""

import os
import time
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

INPUT_CSV = "/home/ubuntu/.openclaw/workspace/out/stage4_top100_input.csv"
OUTPUT_DIR = "/home/ubuntu/.openclaw/workspace/out/stage4_chai"
CHAI_SCRIPT = "/home/ubuntu/.openclaw/workspace/modal_chai1.py"
WORKSPACE   = "/home/ubuntu/.openclaw/workspace"

# Plan B: 8 designs
PLAN_B = [
    # Top 3 from free Stage 4 (pLDDT≥75 by Boltz2 complex)
    "rbx1_binder_323",
    "rbx1_binder_144",
    "rbx1_binder_197",
    # 5 relaxed elites: highest ipTM / lowest PAE / biggest BSA
    "rbx1_binder_430",   # highest ipTM (0.710) among relaxed
    "rbx1_binder_133",   # lowest PAE (2.97)
    "rbx1_binder_385",   # strong balanced
    "rbx1_binder_440",   # largest BSA (2229 Å²), highest composite
    "rbx1_binder_325",   # largest BSA (2251 Å²)
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_plddt_from_cif(cif_path):
    vals = []
    try:
        col_map = {}
        col_idx = 0
        in_atom_loop = False
        with open(cif_path) as f:
            for line in f:
                line = line.rstrip()
                if line.startswith('loop_'):
                    col_map = {}; col_idx = 0; in_atom_loop = False
                    continue
                if line.startswith('_atom_site.'):
                    field = line.strip().split('.')[-1]
                    col_map[field] = col_idx; col_idx += 1
                    in_atom_loop = True
                    continue
                if in_atom_loop and (line.startswith('ATOM') or line.startswith('HETATM')):
                    parts = line.split()
                    try:
                        atom_name = parts[col_map.get('label_atom_id', 3)]
                        b_val = float(parts[col_map.get('B_iso_or_equiv', 14)])
                        if atom_name == 'CA':
                            vals.append(b_val)
                    except (IndexError, ValueError, KeyError):
                        pass
    except Exception:
        pass
    return vals

# Load data
df = pd.read_csv(INPUT_CSV)
subset = df[df['design_id'].isin(PLAN_B)].set_index('design_id').reindex(PLAN_B).reset_index()
print(f"Stage 4 Plan B — {len(subset)} designs via Chai-1 monomer fold")
print(f"Est. time: ~12 min  |  Est. cost: ~$0.56\n")
print(f"{'ID':<25} {'len':>4} {'ipTM':>6} {'pLDDT_s3':>8} {'PAE':>5} {'BSA':>6}")
for _, r in subset.iterrows():
    print(f"  {r['design_id']:<23} {int(r['seq_len']):>4} {r['design_ptm']:>6.3f} {r['interface_pLDDT']:>8.1f} {r['min_pae']:>5.2f} {r['buried_surface_area']:>6.0f}")
print()

results = []
failed  = []
t_start = time.time()

for rank, (_, row) in enumerate(subset.iterrows(), 1):
    design_id = row['design_id']
    sequence  = row['sequence']
    seq_len   = int(row['seq_len'])

    print(f"[{rank}/8] {design_id} ({seq_len}aa) ...", end=" ", flush=True)

    fasta_content = f">protein|name={design_id}\n{sequence}\n"
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.faa', delete=False, dir=WORKSPACE
    ) as f:
        f.write(fasta_content)
        fasta_path = f.name

    chai_outdir = f"{OUTPUT_DIR}/chai_raw"

    try:
        t0  = time.time()
        cmd = ["modal", "run", CHAI_SCRIPT,
               "--input-faa", fasta_path,
               "--out-dir",   chai_outdir,
               "--run-name",  design_id]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=360, cwd=WORKSPACE)
        elapsed = time.time() - t0

        if res.returncode != 0:
            snippet = (res.stderr or res.stdout or "")[-300:].strip()
            print(f"FAILED (rc={res.returncode})")
            failed.append({'design_id': design_id, 'error': snippet})
            continue

        out_path  = Path(chai_outdir) / design_id
        cif_files = list(out_path.glob("pred.model_idx_*.cif"))

        if not cif_files:
            print("NO CIF OUTPUT")
            failed.append({'design_id': design_id, 'error': 'no cif files'})
            continue

        best_vals = None
        for cif_path in sorted(cif_files):
            vals = parse_plddt_from_cif(cif_path)
            if vals and (best_vals is None or np.mean(vals) > np.mean(best_vals)):
                best_vals = vals

        if not best_vals:
            print("pLDDT PARSE FAILED")
            failed.append({'design_id': design_id, 'error': 'plddt parse failed'})
            continue

        arr = np.array(best_vals)
        mean_plddt   = float(np.mean(arr))
        disorder_frac = float(np.mean(arr < 50))
        if mean_plddt < 1.5:          # scale 0-1 → 0-100 if needed
            mean_plddt   *= 100
            disorder_frac = float(np.mean(arr*100 < 50))

        passes = (mean_plddt >= 75.0) and (disorder_frac < 0.10)
        tag    = "✅" if passes else "✗ "
        print(f"{tag} pLDDT={mean_plddt:.1f}  disorder={disorder_frac:.1%}  ({elapsed:.0f}s)")

        results.append({
            'design_id':             design_id,
            'sequence':              sequence,
            'seq_len':               seq_len,
            'composite_score_s3':    float(row['composite_score']),
            'interface_pLDDT_s3':    float(row['interface_pLDDT']),
            'buried_surface_area':   float(row['buried_surface_area']),
            'min_pae':               float(row['min_pae']),
            'design_ptm':            float(row['design_ptm']),
            'hbonds':                int(row['hbonds']),
            'batch':                 row['batch'],
            'monomer_pLDDT_chai1':   mean_plddt,
            'disorder_fraction':     disorder_frac,
            'passes_stage4':         passes,
        })

    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        failed.append({'design_id': design_id, 'error': 'timeout 360s'})
    except Exception as e:
        print(f"ERROR: {e}")
        failed.append({'design_id': design_id, 'error': str(e)})
    finally:
        if os.path.exists(fasta_path):
            os.unlink(fasta_path)

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("STAGE 4 PLAN B COMPLETE")
print(f"{'='*60}")

if results:
    rdf = pd.DataFrame(results).sort_values('monomer_pLDDT_chai1', ascending=False).reset_index(drop=True)
    rdf.to_csv(f"{OUTPUT_DIR}/stage4_planb_all.csv", index=False)
    passing = rdf[rdf['passes_stage4']]
    passing.to_csv(f"{OUTPUT_DIR}/stage4_planb_passing.csv", index=False)

    print(f"  Completed : {len(rdf)}/8")
    print(f"  ✅ PASS (pLDDT≥75 + disorder<10%): {len(passing)}")
    print()
    cols = ['design_id','monomer_pLDDT_chai1','disorder_fraction',
            'interface_pLDDT_s3','design_ptm','min_pae','hbonds','seq_len']
    print(rdf[cols].to_string(index=False))
else:
    print("  No results — check Modal setup.")

if failed:
    pd.DataFrame(failed).to_csv(f"{OUTPUT_DIR}/stage4_planb_failed.csv", index=False)
    for f in failed:
        print(f"  FAILED: {f['design_id']} — {f['error'][:80]}")

print(f"\n  Wall time : {(time.time()-t_start)/60:.1f} min")
print(f"  Output    : {OUTPUT_DIR}/")
