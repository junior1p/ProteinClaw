---
name: binder-design
description: >
  Guidance for choosing the right protein binder design tool.
  Use this skill when: (1) Deciding between BoltzGen or BindCraft,
  (2) Planning a binder design campaign,
  (3) Understanding trade-offs between different approaches,
  (4) Selecting tools for specific target types.
license: MIT
category: orchestration
tags: [guidance, tool-selection, workflow]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Binder Design Tool Selection

## Decision tree

```
De novo binder design?
│
├─ Standard target → BoltzGen ✓ (recommended)
│   All-atom output, single-step: backbone + sequence + side chains
│
├─ Need diversity/exploration → BoltzGen (multiple runs)
│   or BindCraft with varied hotspots
│
├─ Integrated end-to-end → BindCraft
│   Built-in AF2 validation loop
│
├─ Ligand binding → BoltzGen ✓
│   All-atom diffusion handles ligand context natively
│
└─ Antibody/Nanobody → IgGM or mBER
```

## Tool Comparison

| Tool | Strengths | Weaknesses | Best For |
|------|-----------|------------|----------|
| BoltzGen | All-atom, single-step, ligand-aware | Higher GPU requirement (L40S) | Standard (recommended) |
| BindCraft | End-to-end, built-in validation | Less diverse outputs | Production campaigns |
| IgGM | Antibody/nanobody CDR design | Specialized format | Ab/VHH design |
| mBER | VHH nanobody, mask-based design | VHH-specific | VHH optimization |

## Recommended Pipeline: BoltzGen → Chai → QC

```
Target → BoltzGen → Chai → QC filter
 (pdb)  (all-atom)   (val)   (rank)
```

### 1. Target preparation
- Trim to binding region + 10Å buffer
- Remove waters and ligands
- Renumber chains if needed

### 2. Hotspot selection
- Choose 3-6 exposed residues
- Prefer charged/aromatic residues
- Cluster spatially (within 10-15Å)

### 3. Design with BoltzGen
```yaml
# binder.yaml
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
```

```bash
modal run modal_boltzgen.py \
  --input-yaml binder.yaml \
  --protocol protein-anything \
  --num-designs 50
```

### 4. Alternative: BindCraft pipeline
For end-to-end design with integrated validation:
```bash
modal run modal_bindcraft.py \
  --input-pdb target.pdb \
  --hotspots "A45,A67,A89" \
  --number-of-final-designs 50
```

### 5. Validation + filtering

```bash
modal run modal_chai1.py --input-faa sequences.fasta --out-dir predictions/
```

Filter: pLDDT > 0.80, ipTM > 0.50, PAE_interface < 10, scRMSD < 2.0Å

## Campaign Scale Guide

| Stage | Count |
|-------|-------|
| BoltzGen designs | 50-200 |
| After Chai validation | all |
| After QC filtering | 50-100 |
| Experimental testing | 10-50 |

## Common Mistakes

- Using buried hotspots instead of surface-exposed ones
- Too many hotspots (over-constraining)
- Not generating enough diversity
- Including full protein instead of binding region
