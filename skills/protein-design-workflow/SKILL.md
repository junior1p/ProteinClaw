---
name: protein-design-workflow
description: >
  End-to-end guidance for protein design pipelines.
  Use this skill when: (1) Starting a new protein design project,
  (2) Need step-by-step workflow guidance,
  (3) Understanding the full design pipeline,
  (4) Planning compute resources and timelines,
  (5) Integrating multiple design tools.
license: MIT
category: orchestration
tags: [guidance, pipeline, workflow]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Protein Design Workflow Guide

## Standard Pipeline Overview

```
Target Preparation → All-Atom Design → Structure Validation → Filtering
       |                   |                    |                  |
       v                   v                    v                  v
  (pdb skill)         (boltzgen)           (chai/boltz)      (protein-qc)
```

## Phase 1: Target Preparation

```bash
# Download from PDB
curl -o target.pdb "https://files.rcsb.org/download/XXXX.pdb"
```

- Extract target chain, remove waters/ligands
- Trim to binding region + 10Å buffer
- Select 3-6 exposed hotspot residues (K, R, E, D, W, Y, F)

**Output**: `target_prepared.cif`, hotspot residue list

## Phase 2: Design

### Option A: BoltzGen — All-atom (recommended)
```bash
# Create YAML config
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

GPU=L40S modal run modal_boltzgen.py \
  --input-yaml binder.yaml \
  --protocol protein-anything \
  --num-designs 100
```

**Output**: 100 all-atom designs (backbone + sequence + side chains)

### Option B: BindCraft — End-to-end
```bash
GPU=A100 modal run modal_bindcraft.py \
  --input-pdb target.pdb \
  --hotspots "A45,A67,A89" \
  --number-of-final-designs 50
```

**Output**: 50 pre-validated designs with AF2 scores

## Phase 3: Structure Validation

```bash
# Chai-1 (recommended, handles protein + ligand)
modal run modal_chai1.py \
  --input-faa all_sequences.fasta \
  --out-dir predictions/

# Or Boltz (open-source alternative)
modal run modal_boltz.py \
  --input-yaml complex.yaml \
  --out-dir predictions/
```

**Output**: Structure predictions with pLDDT, ipTM, PAE

## Phase 4: Filtering

```python
import pandas as pd

designs = pd.read_csv('all_metrics.csv')
filtered = designs[
    (designs['pLDDT'] > 0.85) &
    (designs['ipTM'] > 0.50) &
    (designs['PAE_interface'] < 10) &
    (designs['scRMSD'] < 2.0)
]
filtered['score'] = 0.3 * filtered['pLDDT'] + 0.3 * filtered['ipTM'] + \
                    0.2 * (1 - filtered['PAE_interface'] / 20) + \
                    0.2 * filtered['esm2_pll']
top_designs = filtered.nlargest(50, 'score')
```

## Resource Planning

| Stage | GPU | Time (100 designs) | Cost |
|-------|-----|--------------------|------|
| BoltzGen | L40S | 2-3h | ~$20 |
| Chai validation | A100 | 1h | ~$4.50 |
| Filtering | CPU | 15 min | ~$0 |

**Timeline**: Small campaign (100 designs): 4-6h total

## Quality Checkpoints

### After design (BoltzGen output)
- [ ] Check design diversity (vary binder length range)
- [ ] Visual spot-check of a few structures

### After validation
- [ ] pLDDT > 0.85
- [ ] ipTM > 0.50
- [ ] PAE_interface < 10
- [ ] scRMSD < 2.0 Å

## Common Issues

| Problem | Solution |
|---------|----------|
| Low ipTM | Review hotspot selection; try more designs |
| Low pLDDT | Use SolubleMPNN variant; check sequence |
| Poor diversity | Widen binder length range in YAML |
| All designs similar | Run multiple independent BoltzGen jobs |
