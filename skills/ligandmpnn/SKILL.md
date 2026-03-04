---
name: ligandmpnn
description: >
  Ligand-aware protein sequence design using LigandMPNN.
  Use this skill when: (1) Designing sequences around small molecules,
  (2) Enzyme active site design,
  (3) Ligand binding pocket optimization,
  (4) Metal coordination site design,
  (5) Cofactor binding proteins.

  For standard protein design, use proteinmpnn.
  For solubility optimization, use solublempnn.
license: MIT
category: design-tools
tags: [sequence-design, inverse-folding, ligand-aware]
source: https://github.com/adaptyvbio/protein-design-skills
---

# LigandMPNN Ligand-Aware Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| GPU VRAM | 8GB | 16GB (T4) |

## How to run

### Option 1: Modal (recommended)
```bash
cd biomodals
modal run modal_ligandmpnn.py \
  --pdb-path protein_ligand.pdb \
  --num-seq-per-target 16 \
  --sampling-temp 0.1
```

### Option 2: Local
```bash
git clone https://github.com/dauparas/LigandMPNN.git
cd LigandMPNN
python run.py \
  --pdb_path protein_ligand.pdb \
  --out_folder output/ \
  --num_seq_per_target 16
```

## Ligand Specification

Ligand must be present as HETATM records in PDB:
```
HETATM  1  C1  LIG A 999  x.xxx  y.yyy  z.zzz  1.00  0.00  C
```

**Supported**: Small molecules, metals (Zn/Fe/Mg), cofactors (NAD/FAD/ATP), DNA/RNA

## Decision tree

```
What's in your binding site?
├─ Small molecule / ligand → LigandMPNN ✓
├─ Metal ion → LigandMPNN ✓
├─ Cofactor → LigandMPNN ✓
└─ Protein only → ProteinMPNN
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'LIG'` | Ligand not found | Check HETATM records |
| `ValueError: no ligand atoms` | Empty ligand | Verify atoms in PDB |

**Next**: Structure prediction → `protein-qc` for filtering.
