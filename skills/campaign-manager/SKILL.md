---
name: campaign-manager
description: >
  Goal-oriented binder design campaign planning and health assessment.
  Use this skill when: (1) Planning a complete binder design campaign,
  (2) Converting high-level goals into runnable pipelines,
  (3) Assessing campaign health and pass rates,
  (4) Diagnosing why designs are failing QC,
  (5) Estimating time, cost, and expected yields,
  (6) Selecting between design tools for a specific target.

  This skill orchestrates the other protein design tools.
license: MIT
category: orchestration
tags: [planning, campaign, coordination]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Campaign Manager

## Goal-Oriented Planning

When user says "I need 10 good binders for EGFR":

```
Goal: 10 high-quality binders
├── Recommended: boltzgen → chai → protein-qc
├── 100-200 BoltzGen designs → Chai validation → ~10-20% pass QC
├── Estimated time: 4-8 hours
└── Estimated cost: ~$30-60 (Modal GPU compute)
```

## Recommended Pipeline (BoltzGen)

```bash
# Step 1: Prepare target (5 min)
curl -o target.pdb "https://files.rcsb.org/download/{PDB_ID}.pdb"

# Step 2: Create YAML config
cat > binder.yaml << 'EOF'
entities:
  - protein:
      id: B
      sequence: 70..100
  - file:
      path: target.cif
      include:
        - chain:
            id: A
      binding_types:
        - chain:
            id: A
            binding: 45,67,89
EOF

# Step 3: Generate all-atom designs (2-4h, ~$20)
GPU=L40S modal run modal_boltzgen.py \
  --input-yaml binder.yaml \
  --protocol protein-anything \
  --num-designs 100

# Step 4: Validate (1-2h, ~$10)
modal run modal_chai1.py --input-faa designs.fasta --out-dir predictions/

# Step 5: Filter and rank (protein-qc skill)
```

## Alternative Pipeline (BindCraft — integrated)

```bash
# Single command, end-to-end
GPU=A100 modal run modal_bindcraft.py \
  --input-pdb target.pdb \
  --hotspots "A45,A67,A89" \
  --number-of-final-designs 50
```

## Campaign Size Recommendations

| Goal | BoltzGen designs | Expected Passing | Final candidates |
|------|-----------------|-----------------|-----------------|
| 5 binders | 50 | ~5-10 | 5 |
| 10 binders | 100 | ~10-20 | 10 |
| 20 binders | 200 | ~20-40 | 20 |
| 50 binders | 500 | ~50-100 | 50 |

## Campaign Health Assessment

```python
def assess_campaign(csv_path):
    df = pd.read_csv(csv_path)
    plddt_pass = (df['pLDDT'] > 0.85).mean()
    iptm_pass = (df['ipTM'] > 0.50).mean()
    all_pass = ((df['pLDDT'] > 0.85) & (df['ipTM'] > 0.5) & (df['scRMSD'] < 2.0)).mean()

    health = "EXCELLENT" if all_pass > 0.15 else \
             "GOOD" if all_pass > 0.10 else \
             "MARGINAL" if all_pass > 0.05 else "POOR"

    issues = []
    if plddt_pass < 0.20:
        issues.append("Low pLDDT - backbone or sequence issue")
    if iptm_pass < 0.20:
        issues.append("Low ipTM - hotspot or interface issue")

    return {"health": health, "pass_rate": all_pass, "issues": issues}
```

| Health | Pass Rate | Action |
|--------|-----------|--------|
| EXCELLENT | > 15% | Proceed to selection |
| GOOD | 10-15% | Normal yield |
| MARGINAL | 5-10% | Review failure tree |
| POOR | < 5% | Diagnose and restart |

## Cost Estimates (Modal)

| Tool | GPU | Typical Job | Cost |
|------|-----|-------------|------|
| BoltzGen | L40S | 100 designs/2h | ~$20 |
| BindCraft | A100 | 50 designs/4h | ~$18 |
| Chai | A100 | 200 preds/1h | ~$4.50 |
| Boltz | L40S | 200 preds/1h | ~$4 |

**Standard campaign (100 designs)**: ~$25-30 total
