---
name: iggm
description: >
  Antibody and nanobody CDR design using IgGM (generative model by TencentAI4S).
  Use this skill when:
  (1) Designing nanobody (VHH) CDR loops against a target,
  (2) Designing full antibody (heavy + light chain) CDRs,
  (3) Redesigning existing antibody CDRs,
  (4) Need antigen-conditioned antibody generation,
  (5) Generating diverse antibody candidates with specific epitope targeting.

  For VHH mask-based design (scaffold preserved), use mber.
  For general protein binder design, use boltzgen or bindcraft.
license: MIT
category: design-tools
tags: [antibody, nanobody, vhh, sequence-design, generative]
source: https://github.com/hgbrian/biomodals
---

# IgGM Antibody & Nanobody Design

IgGM is a generative model for functional antibody and nanobody design from TencentAI4S.
It designs CDR loops conditioned on a target antigen structure.

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| GPU VRAM | 16GB | 24GB (A10G) |

## FASTA Format (Critical)

IgGM uses a specific FASTA format with chain identifiers:

| Header | Meaning |
|--------|---------|
| `>H` | Heavy chain (or VHH for nanobody) |
| `>L` | Light chain (antibody only) |
| `>A`, `>B`, ... | Antigen chain ID in the PDB file |

Use **`X`** to mark positions to design (CDR loops).

### Nanobody (VHH) design
```
>H
QVQLVESGGGLVQPGGSLRLSCAASGFTFSXXXXXXXXXXXXXXXXXXXXXXTRV...CDR3...WGQGTLVTVSS
>A
(empty line — specifies chain A from antigen PDB)
```

### Full antibody design
```
>H
VQLVESGGGLVQPGGSLRLSCAASXXXXXXXYMN...CDR2...WVRQAPGKGLEW...CDR3...
>L
DIQMTQSPSSLS...XXXXXXWYQQKPGKAPKLL...CDR2...KASSLES...CDR3...
>A
(specifies chain A from antigen PDB)
```

## How to run

```bash
# Nanobody design against PDB target (chain A)
modal run modal_iggm.py \
  --input-fasta nanobody.fasta \
  --antigen antigen.pdb \
  --epitope "41,42,43" \
  --task design

# Antibody design
modal run modal_iggm.py \
  --input-fasta antibody.fasta \
  --antigen target.pdb \
  --task design \
  --num-designs 50

# Just CDR3 redesign (fix framework, design CDR3 only)
modal run modal_iggm.py \
  --input-fasta template.fasta \
  --antigen target.pdb \
  --task design
```

## Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input-fasta` | required | FASTA with X-marked positions |
| `--antigen` | required | Target PDB file |
| `--epitope` | None | Comma-separated residue numbers |
| `--task` | `design` | `design` or `optimize` |
| `--num-designs` | 10 | Number of sequences to generate |

## Output format

```
output/
├── design_0.fasta    # Designed sequences
├── design_0.pdb      # Co-folded complex
└── scores.json       # Confidence scores
```

## IgGM vs mBER

| Aspect | IgGM | mBER |
|--------|------|------|
| Input | X-masked FASTA | Masked VHH sequence |
| Antigen conditioning | Yes (explicit epitope) | Yes (via AF-Multimer) |
| Output type | CDR loops | Full VHH sequence |
| Antibody support | Yes (H+L) | No (VHH only) |
| Best for | De novo CDR design | VHH refinement |

## Decision tree

```
Antibody/nanobody design?
├─ Full antibody (H+L chains) → IgGM ✓
├─ Nanobody (VHH) de novo → IgGM ✓
├─ VHH with known scaffold → mBER ✓
└─ General protein binder → boltzgen or bindcraft
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: chain` | Antigen chain not found | Check PDB chain IDs match FASTA |
| `No X positions` | No design positions | Mark CDR positions with X |
| `CUDA out of memory` | Long antigen | Trim antigen to binding domain |

**Next**: Validate with `chai` or `protenix` → `protein-qc` for filtering.
