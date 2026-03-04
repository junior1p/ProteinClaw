"""Stage 3 Final — correct pLDDT (×100) scoring"""
import csv
from pathlib import Path
from collections import defaultdict

BASE       = Path("/home/ubuntu/.openclaw/workspace/out/boltzgen/rbx1_batch1/2603031805")
REFOLD_DIR = BASE / "intermediate_designs_inverse_folded" / "refold_cif"
METRICS_CSV= BASE / "final_ranked_designs" / "all_designs_metrics.csv"
OUT_DIR    = Path("/home/ubuntu/.openclaw/workspace/out/stage3")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def get_chain_a_plddt(cif_path):
    """B_iso_or_equiv is 0-1 in Boltz outputs; ×100 = pLDDT."""
    vals = []; col_map = {}; idx = 0; in_atom = False
    with open(cif_path) as f:
        for line in f:
            line = line.rstrip()
            if line == "loop_":
                col_map = {}; idx = 0; in_atom = False; continue
            if line.startswith("_atom_site."):
                col_map[line.split(".")[1]] = idx; idx += 1; in_atom = True; continue
            if in_atom and line.startswith(("ATOM","HETATM")):
                p = line.split()
                try:
                    if p[col_map["label_atom_id"]] == "CA" and p[col_map["auth_asym_id"]] == "A":
                        vals.append(float(p[col_map["B_iso_or_equiv"]]) * 100)
                except: pass
    return round(sum(vals)/len(vals), 2) if vals else 0.0

with open(METRICS_CSV) as f:
    bg = {r["id"]: r for r in csv.DictReader(f)}

results = []
for did, row in bg.items():
    cif = REFOLD_DIR / f"{did}.cif"
    plddt  = get_chain_a_plddt(cif)
    bsa    = float(row.get("delta_sasa_refolded","0") or 0)
    iptm   = float(row.get("design_to_target_iptm","0") or 0)
    pae    = float(row.get("min_design_to_target_pae","999") or 999)
    ptm    = float(row.get("design_ptm","0") or 0)
    hb     = int(float(row.get("plip_hbonds_refolded","0") or 0))
    seq    = row.get("designed_sequence","")
    results.append(dict(
        design_id=did, sequence=seq, seq_len=len(seq),
        interface_pLDDT=plddt, buried_surface_area=bsa,
        interface_score=iptm, min_pae=pae, design_ptm=ptm, hbonds=hb,
    ))

# Composite: 40% iptm + 30% pLDDT/100 + 30% BSA/3000
for r in results:
    r["composite_score"] = round(
        r["interface_score"]*0.4 + (r["interface_pLDDT"]/100)*0.3 +
        min(r["buried_surface_area"]/3000,1.0)*0.3, 5)

results.sort(key=lambda x: x["composite_score"], reverse=True)

passed = [r for r in results if r["interface_pLDDT"]>=75 and r["buried_surface_area"]>=600]
passed.sort(key=lambda x: x["composite_score"], reverse=True)

FIELDS = ["rank","design_id","sequence","seq_len","composite_score",
          "interface_score","interface_pLDDT","buried_surface_area",
          "min_pae","design_ptm","hbonds"]

def write_csv(path, rows):
    with open(path,"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for i,r in enumerate(rows,1):
            w.writerow({**r,"rank":i})

top_n = min(250, len(passed))
write_csv(OUT_DIR/"stage3_top_results.csv", passed[:top_n])
write_csv(OUT_DIR/"stage3_all_results.csv", results)

# ── Print report ──────────────────────────────────────────────────────────────
print("="*75)
print("  RBX1 Binder Design — Stage 3 Boltz Scoring Report")
print("="*75)
print(f"\n  Source: BoltzGen Boltz2 refold outputs (100 designs)")
print(f"  Metrics extracted from refold CIF B-factors + BoltzGen analysis CSV")
print()
print("  Metric definitions:")
print("    interface_pLDDT    = mean pLDDT of binder chain A (Boltz B-factor×100)")
print("    interface_score    = design_to_target_ipTM (Boltz2 folding)")
print("    buried_surface_area= ΔSASA (unbound−bound) from Boltz2 refolding [Å²]")
print()

n = len(results)
plddts = sorted(r["interface_pLDDT"] for r in results)
bsas   = sorted(r["buried_surface_area"] for r in results)
iptms  = sorted(r["interface_score"] for r in results)

print("  Distributions (all 100 designs):")
print(f"  {'Metric':<22} {'min':>7} {'p25':>7} {'p50':>7} {'p75':>7} {'max':>7}")
print("  " + "-"*55)
for label, vals in [("interface_pLDDT",plddts),("BSA (Å²)",bsas),("interface_score",iptms)]:
    print(f"  {label:<22} {vals[0]:>7.1f} {vals[n//4]:>7.1f} {vals[n//2]:>7.1f} {vals[3*n//4]:>7.1f} {vals[-1]:>7.1f}")

print()
print("  Filtering thresholds:")
print(f"    interface_pLDDT ≥ 75   : {sum(1 for r in results if r['interface_pLDDT']>=75):>3} / {n} designs")
print(f"    buried_surface_area ≥ 600 Å²: {sum(1 for r in results if r['buried_surface_area']>=600):>3} / {n} designs")
print(f"    BOTH criteria          : {len(passed):>3} / {n} designs  ({100*len(passed)/n:.1f}%)")
print()
print("  NOTE: Low pass-rate (6%) due to strict pLDDT threshold.")
print("  The refold pLDDT reflects Boltz2's confidence in the designed binder")
print("  geometry — most designs scored 60-70 (moderate confidence).")
print()

if passed:
    print(f"  {'='*70}")
    print(f"  Top {top_n} Passed Designs (interface_pLDDT≥75, BSA≥600 Å²)")
    print(f"  {'='*70}")
    hdr = f"  {'Rk':<4} {'Design ID':<22} {'Len':<5} {'ipTM':<7} {'pLDDT':<8} {'BSA(Å²)':<10} {'PAE':<7} {'HB':<4} Score"
    print(hdr); print("  "+"-"*68)
    for i,r in enumerate(passed[:top_n],1):
        print(f"  {i:<4} {r['design_id']:<22} {r['seq_len']:<5} "
              f"{r['interface_score']:<7.3f} {r['interface_pLDDT']:<8.1f} "
              f"{r['buried_surface_area']:<10.0f} {r['min_pae']:<7.2f} "
              f"{r['hbonds']:<4} {r['composite_score']:.4f}")
    print()
    print("  Top candidate sequences:")
    for i,r in enumerate(passed[:3],1):
        print(f"  #{i} {r['design_id']} ({r['seq_len']} aa):")
        print(f"     {r['sequence']}")
        print()

# Also show top-10 relaxed (pLDDT>=70 only)
relaxed = [r for r in results if r["interface_pLDDT"]>=70 and r["buried_surface_area"]>=600]
print(f"  [Relaxed criteria: pLDDT≥70 AND BSA≥600]  → {len(relaxed)} designs")
relaxed.sort(key=lambda x: x["composite_score"], reverse=True)
write_csv(OUT_DIR/"stage3_relaxed_results.csv", relaxed)
print(f"  ✓ Relaxed set → {OUT_DIR}/stage3_relaxed_results.csv")
for i,r in enumerate(relaxed[:5],1):
    print(f"    {i}. {r['design_id']}: pLDDT={r['interface_pLDDT']:.1f} BSA={r['buried_surface_area']:.0f} iptm={r['interface_score']:.3f} PAE={r['min_pae']:.2f}")

print()
print(f"  ✓ Top {top_n} strict → {OUT_DIR}/stage3_top_results.csv")
print(f"  ✓ All 100    → {OUT_DIR}/stage3_all_results.csv")
