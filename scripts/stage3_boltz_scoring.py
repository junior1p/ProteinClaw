"""
Stage 3: Boltz complex scoring from BoltzGen refold outputs
Metrics:
  - interface_pLDDT  : mean pLDDT of designed chain (chain A) from refold CIF B-factors
  - interface_score  : design_to_target_iptm from BoltzGen Boltz2 folding step
  - buried_surface_area : delta_sasa_refolded (SASA_unbound - SASA_bound, Å²)
"""
import csv
from pathlib import Path
from collections import defaultdict

BASE       = Path("/home/ubuntu/.openclaw/workspace/out/boltzgen/rbx1_batch1/2603031805")
REFOLD_DIR = BASE / "intermediate_designs_inverse_folded" / "refold_cif"
METRICS_CSV= BASE / "final_ranked_designs" / "all_designs_metrics.csv"
OUT_DIR    = Path("/home/ubuntu/.openclaw/workspace/out/stage3")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_design_plddt(cif_path):
    """Return mean pLDDT (×100) for the designed chain (chain A)."""
    chain_plddt = defaultdict(list)
    col_map = {}
    idx = 0
    in_atom_block = False

    with open(cif_path) as f:
        for line in f:
            line = line.rstrip()
            if line == "loop_":
                col_map = {}; idx = 0; in_atom_block = False
                continue
            if line.startswith("_atom_site."):
                col_map[line.split(".")[1]] = idx
                idx += 1
                in_atom_block = True
                continue
            if in_atom_block and line.startswith(("ATOM", "HETATM")):
                parts = line.split()
                try:
                    chain = parts[col_map["auth_asym_id"]]
                    atom  = parts[col_map["label_atom_id"]]
                    biso  = float(parts[col_map["B_iso_or_equiv"]])
                    if atom == "CA":
                        chain_plddt[chain].append(biso)
                except (KeyError, IndexError, ValueError):
                    pass

    # chain A = binder; if absent take first non-B chain
    vals = chain_plddt.get("A") or next(
        (v for k, v in chain_plddt.items() if k != "B" and v), []
    )
    return round(sum(vals) / len(vals) * 100, 2) if vals else 0.0


# ── load BoltzGen metrics ────────────────────────────────────────────────────
print("Loading BoltzGen metrics …")
bg_metrics = {}
with open(METRICS_CSV) as f:
    for row in csv.DictReader(f):
        bg_metrics[row["id"]] = row
print(f"  {len(bg_metrics)} designs loaded")

# ── compute per-design scores ────────────────────────────────────────────────
print("Computing interface scores …")
results = []
for did, row in bg_metrics.items():
    cif_path = REFOLD_DIR / f"{did}.cif"
    if not cif_path.exists():
        print(f"  SKIP (no CIF): {did}")
        continue

    iplddt = parse_design_plddt(cif_path)
    iptm   = float(row.get("design_to_target_iptm") or 0)
    bsa    = float(row.get("delta_sasa_refolded")    or 0)
    pae    = float(row.get("min_design_to_target_pae") or 999)
    ptm    = float(row.get("design_ptm")             or 0)
    hb     = int(float(row.get("plip_hbonds_refolded") or 0))
    seq    = row.get("designed_sequence") or row.get("designed_chain_sequence", "")
    num_d  = int(float(row.get("num_design") or 0))

    results.append(dict(
        design_id      = did,
        sequence       = seq,
        seq_len        = len(seq),
        num_design     = num_d,
        interface_score= round(iptm,  5),
        interface_pLDDT= round(iplddt,2),
        buried_surface_area = round(bsa, 2),
        min_pae        = round(pae,  3),
        design_ptm     = round(ptm,  5),
        hbonds         = hb,
    ))

print(f"  {len(results)} designs processed")

# ── filtering ────────────────────────────────────────────────────────────────
print("\n=== Stage 3 Filtering ===")
print("  Criteria: interface_pLDDT ≥ 75  AND  buried_surface_area ≥ 600 Å²")

passed = [r for r in results
          if r["interface_pLDDT"] >= 75 and r["buried_surface_area"] >= 600]

print(f"  Total : {len(results)}")
print(f"  Passed: {len(passed)}  ({100*len(passed)/len(results):.1f}%)")
print(f"  Failed: {len(results)-len(passed)}  ({100*(len(results)-len(passed))/len(results):.1f}%)")

# composite score: 40% iptm + 30% pLDDT + 30% BSA (norm to 3000 Å²)
def composite(r):
    return (r["interface_score"] * 0.4
            + (r["interface_pLDDT"] / 100) * 0.3
            + min(r["buried_surface_area"] / 3000, 1.0) * 0.3)

for r in results: r["composite_score"] = round(composite(r), 5)
passed.sort(key=lambda x: x["composite_score"], reverse=True)
results.sort(key=lambda x: x["composite_score"], reverse=True)

# ── output ───────────────────────────────────────────────────────────────────
FIELDS = ["rank","design_id","sequence","seq_len","num_design",
          "composite_score","interface_score","interface_pLDDT",
          "buried_surface_area","min_pae","design_ptm","hbonds"]

def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(rows, 1):
            w.writerow({**r, "rank": i})

top_n = min(250, len(passed))
write_csv(OUT_DIR / "stage3_top_results.csv",  passed[:top_n])
write_csv(OUT_DIR / "stage3_all_results.csv",  results)
print(f"\n  ✓ Top {top_n} → {OUT_DIR}/stage3_top_results.csv")
print(f"  ✓ All 100 → {OUT_DIR}/stage3_all_results.csv")

# ── summary table ─────────────────────────────────────────────────────────────
print(f"\n{'='*85}")
print(f"  Stage 3 — Top {min(20,top_n)} passed designs")
print(f"{'='*85}")
hdr = f"{'Rk':<4} {'Design ID':<22} {'Len':<5} {'#Des':<5} {'ipTM':<7} {'pLDDT':<8} {'BSA(Å²)':<10} {'PAE':<7} {'HB':<4} Score"
print(hdr); print("-"*85)
for i, r in enumerate(passed[:20], 1):
    print(f"{i:<4} {r['design_id']:<22} {r['seq_len']:<5} {r['num_design']:<5} "
          f"{r['interface_score']:<7.3f} {r['interface_pLDDT']:<8.1f} "
          f"{r['buried_surface_area']:<10.0f} {r['min_pae']:<7.2f} "
          f"{r['hbonds']:<4} {r['composite_score']:.4f}")

# ── distributions ─────────────────────────────────────────────────────────────
print(f"\nMetric distributions (all {len(results)} designs):")
for label, key in [("interface_pLDDT","interface_pLDDT"),
                   ("BSA (Å²)","buried_surface_area"),
                   ("ipTM","interface_score"),
                   ("min_PAE","min_pae")]:
    vals = sorted(r[key] for r in results)
    n = len(vals)
    print(f"  {label:<18}: "
          f"min={vals[0]:.1f}  p25={vals[n//4]:.1f}  "
          f"median={vals[n//2]:.1f}  p75={vals[3*n//4]:.1f}  max={vals[-1]:.1f}")
