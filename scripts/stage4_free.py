#!/usr/bin/env python3
"""
Stage 4 (Free): Monomer Stability from existing BoltzGen CIFs
- Extract full-chain pLDDT from Boltz2 refold CIFs (already computed in Stage 2)
- Filter: mean monomer pLDDT >= 80, disorder_fraction < 10%
- Zero GPU cost — reuses existing data
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_CSV     = "/home/ubuntu/.openclaw/workspace/out/stage4_top100_input.csv"
BATCH1_REFOLD = "/home/ubuntu/.openclaw/workspace/out/boltzgen/rbx1_batch1/2603031805/intermediate_designs_inverse_folded/fold_out_npz"
BATCH2_REFOLD = "/home/ubuntu/.openclaw/workspace/out/boltzgen/rbx1_batch2/2603032107/intermediate_designs_inverse_folded/fold_out_npz"
OUTPUT_DIR    = "/home/ubuntu/.openclaw/workspace/out/stage4"

PLDDT_MIN      = 80.0   # mean full-chain pLDDT
DISORDER_MAX   = 0.10   # fraction of residues with pLDDT < 50

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ── Helper: parse full-chain pLDDT from Boltz2 CIF ───────────────────────────
def parse_full_chain_plddt(cif_path):
    """
    Extract pLDDT for ALL CA atoms in chain A (the binder).
    Boltz2 CIFs store pLDDT in B_iso_or_equiv as 0-1; multiply x100.
    """
    vals = []
    col_map = {}
    col_idx = 0
    in_atom = False
    with open(cif_path) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('loop_'):
                col_map = {}; col_idx = 0; in_atom = False
                continue
            if line.startswith('_atom_site.'):
                col_map[line.strip().split('.')[-1]] = col_idx
                col_idx += 1; in_atom = True
                continue
            if in_atom and (line.startswith('ATOM') or line.startswith('HETATM')):
                parts = line.split()
                try:
                    atom  = parts[col_map.get('label_atom_id', 3)]
                    chain = parts[col_map.get('label_asym_id', 6)]
                    b_val = float(parts[col_map.get('B_iso_or_equiv', 14)])
                    if atom == 'CA' and chain == 'A':
                        # Boltz2 range is 0-1 → multiply x100
                        vals.append(b_val * 100 if b_val <= 1.0 else b_val)
                except (IndexError, ValueError, KeyError):
                    pass
    return vals

# ── Find CIF for a design ─────────────────────────────────────────────────────
def find_cif(design_id, batch):
    num = design_id.split('_')[-1]  # e.g. "440" from "rbx1_binder_440"
    if batch == 'batch1':
        base = Path(BATCH1_REFOLD)
    else:
        base = Path(BATCH2_REFOLD)
    # Boltz2 names: rbx1_binder_NNN.npz → look for matching CIF in parent
    # The CIFs live one level up in intermediate_designs_inverse_folded
    parent = base.parent
    # Try direct name
    cif = parent / f"rbx1_binder_{num}.cif"
    if cif.exists():
        return cif
    # Also check intermediate_designs (pre-refold CIFs)
    batch_dir = base.parent.parent  # boltzgen run dir
    cif2 = batch_dir / "intermediate_designs" / f"rbx1_binder_{num}.cif"
    if cif2.exists():
        return cif2
    return None

# ── Main ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV)
print(f"Stage 4 (Free): Processing {len(df)} designs from existing CIFs")
print(f"Filter: mean pLDDT ≥ {PLDDT_MIN}, disorder < {DISORDER_MAX:.0%}\n")

results = []
missing = []

for _, row in df.iterrows():
    did   = row['design_id']
    batch = row['batch']

    cif_path = find_cif(did, batch)
    if cif_path is None:
        missing.append(did)
        continue

    vals = parse_full_chain_plddt(cif_path)
    if not vals:
        missing.append(did)
        continue

    arr           = np.array(vals)
    mean_plddt    = float(np.mean(arr))
    disorder_frac = float(np.mean(arr < 50))
    pct_above_80  = float(np.mean(arr >= 80))

    passes = (mean_plddt >= PLDDT_MIN) and (disorder_frac < DISORDER_MAX)

    results.append({
        'design_id':           did,
        'batch':               batch,
        'seq_len':             int(row['seq_len']),
        'monomer_pLDDT':       round(mean_plddt, 2),
        'disorder_fraction':   round(disorder_frac, 4),
        'pct_residues_ge80':   round(pct_above_80, 4),
        'interface_pLDDT_s3':  float(row['interface_pLDDT']),
        'buried_surface_area': float(row['buried_surface_area']),
        'min_pae':             float(row['min_pae']),
        'design_ptm':          float(row['design_ptm']),
        'hbonds':              int(row['hbonds']),
        'composite_score_s3':  float(row['composite_score']),
        'passes_stage4':       passes,
    })

rdf = pd.DataFrame(results)
rdf.to_csv(f"{OUTPUT_DIR}/stage4_all_results.csv", index=False)

passing = rdf[rdf['passes_stage4']].sort_values('monomer_pLDDT', ascending=False).reset_index(drop=True)
passing.to_csv(f"{OUTPUT_DIR}/stage4_passing.csv", index=False)

# ── Report ────────────────────────────────────────────────────────────────────
print(f"{'='*62}")
print(f"STAGE 4 RESULTS  (zero GPU cost)")
print(f"{'='*62}")
print(f"  Processed:   {len(rdf)} / {len(df)}")
print(f"  Missing CIF: {len(missing)}")
print(f"  pLDDT dist:  min={rdf['monomer_pLDDT'].min():.1f}  "
      f"median={rdf['monomer_pLDDT'].median():.1f}  "
      f"max={rdf['monomer_pLDDT'].max():.1f}")
print(f"  ✅ PASS (pLDDT≥{PLDDT_MIN:.0f} + disorder<{DISORDER_MAX:.0%}): "
      f"{len(passing)} / {len(rdf)}")

if len(passing) > 0:
    print(f"\n  Top designs passing Stage 4:")
    cols = ['design_id','monomer_pLDDT','disorder_fraction',
            'interface_pLDDT_s3','design_ptm','min_pae','hbonds','seq_len']
    print(passing[cols].head(20).to_string(index=False))
else:
    print(f"\n  ⚠️  No designs pass pLDDT≥80.")
    print(f"  Showing top 15 by monomer_pLDDT:")
    top = rdf.sort_values('monomer_pLDDT', ascending=False).head(15)
    cols = ['design_id','monomer_pLDDT','disorder_fraction',
            'interface_pLDDT_s3','design_ptm','min_pae','seq_len']
    print(top[cols].to_string(index=False))
    # Suggest relaxed threshold
    for t in [75, 70]:
        n = (rdf['monomer_pLDDT'] >= t).sum()
        print(f"  → At pLDDT≥{t}: {n} designs would pass")

if missing:
    print(f"\n  Missing CIFs: {missing[:5]}{'...' if len(missing)>5 else ''}")

print(f"\n  Saved: {OUTPUT_DIR}/stage4_all_results.csv")
print(f"         {OUTPUT_DIR}/stage4_passing.csv")
