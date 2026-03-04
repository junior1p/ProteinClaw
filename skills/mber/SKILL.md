---
name: mber
description: >
  VHH nanobody design using mBER (Manifold Binder Engineering and Refinement).
  Use this skill when:
  (1) Designing VHH nanobody CDRs against a target protein,
  (2) Have an existing VHH scaffold and want to redesign CDR1/CDR2/CDR3,
  (3) Optimizing a known VHH binder,
  (4) Targeting specific hotspot residues on the antigen,
  (5) Multi-chain antigen targets (with chain offsets).

  For de novo antibody/nanobody CDR design, use iggm.
  For general protein binder design, use boltzgen or bindcraft.
license: MIT
category: design-tools
tags: [antibody, nanobody, vhh, sequence-design, mask-based]
source: https://github.com/hgbrian/biomodals
---

# mBER VHH Nanobody Design

mBER uses structure templates and sequence conditioning (via AlphaFold-Multimer)
to design VHH nanobody binders against a target protein.

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| GPU VRAM | 40GB | 80GB (A100) |

## How to run

### Basic VHH design
```bash
# Design VHH against a PDB target (downloads PDB automatically)
modal run modal_mber.py \
  --target-pdb 7STF.pdb \
  --target-name PDL1

# Or by PDB ID
wget https://files.rcsb.org/download/7STF.pdb
modal run modal_mber.py --target-pdb 7STF.pdb --target-name PDL1
```

### Custom masked VHH sequence (* = positions to design)
```bash
modal run modal_mber.py \
  --target-pdb target.pdb \
  --target-name MyTarget \
  --masked-binder-seq "EVQLVESGGGLVQPGGSLRLSCAASG*********WFRQAPGKEREF***********NADSVKGRFTISRDNAKNTLYLQMNSLRAEDTAVYYC************WGQGTLVTVSS"
```

The `*` characters specify **which positions to design** (typically CDR1, CDR2, CDR3).
Framework regions remain fixed.

### With specific chains and hotspots
```bash
modal run modal_mber.py \
  --target-pdb target.pdb \
  --target-name MyTarget \
  --chains A,B \
  --target-hotspot-residues A110,B120
```

### Multi-chain with non-contiguous numbering
```bash
# Use chain-offsets to prevent folding chains as single chain
modal run modal_mber.py \
  --target-pdb target.pdb \
  --target-name MyTarget \
  --chains A,B \
  --chain-offsets B:200 \
  --target-hotspot-residues A6
```

## Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--target-pdb` | required | Target PDB file |
| `--target-name` | required | Name for output files |
| `--masked-binder-seq` | default CDRs | VHH sequence with `*` for design positions |
| `--chains` | A | Target chains to include |
| `--target-hotspot-residues` | None | Residues to target (e.g., `A110,B120`) |
| `--chain-offsets` | None | Offset for multi-chain numbering (e.g., `B:200`) |
| `--output-dir` | `./out/mber` | Output directory |

## Default design regions

By default, mBER designs the three CDR loops of the VHH:
- **CDR1**: positions ~26-35
- **CDR2**: positions ~50-58
- **CDR3**: positions ~97-110

The framework (FR1, FR2, FR3, FR4) is kept fixed.

## Output format

```
out/mber/
├── design_0.pdb       # VHH-target complex
├── design_0.fasta     # Designed VHH sequence
└── scores.json        # AF-Multimer confidence scores
```

## mBER vs IgGM

| Aspect | mBER | IgGM |
|--------|------|------|
| Input | Masked VHH sequence | X-masked FASTA |
| Method | AF-Multimer conditioning | Generative model |
| Antibody support | No (VHH only) | Yes (H+L) |
| Best for | VHH scaffold refinement | De novo CDR design |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Large target | Use A100-80GB |
| `Chain not found` | Wrong chain ID | Check PDB chain IDs |
| `Invalid masked sequence` | Wrong length | Match VHH framework length |

**Next**: Validate with `chai` or `protenix` → `protein-qc` for filtering.
