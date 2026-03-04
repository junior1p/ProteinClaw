---
name: boltzgen
description: >
  All-atom protein design using BoltzGen diffusion model. Use this skill when:
  (1) Need side-chain aware design from the start,
  (2) Designing around small molecules or ligands,
  (3) Want all-atom diffusion (not just backbone),
  (4) Require precise binding geometries,
  (5) Using YAML-based configuration.


  For sequence-only design, use proteinmpnn.
  For structure validation, use boltz.
license: MIT
category: design-tools
tags: [structure-design, sequence-design, diffusion, all-atom, binder]
source: https://github.com/adaptyvbio/protein-design-skills
---

# BoltzGen All-Atom Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11 |
| CUDA | 12.0+ | 12.1+ |
| GPU VRAM | 24GB | 48GB (L40S) |
| RAM | 32GB | 64GB |

## How to run

> **First time?** See setup skill to configure Modal and biomodals.

### Option 1: Modal (recommended)
```bash
git clone https://github.com/hgbrian/biomodals && cd biomodals
modal run modal_boltzgen.py \
  --input-yaml binder_config.yaml \
  --protocol protein-anything \
  --num-designs 50

# With custom GPU
GPU=L40S modal run modal_boltzgen.py \
  --input-yaml binder_config.yaml \
  --protocol protein-anything \
  --num-designs 100
```

**Available protocols**: `protein-anything`, `peptide-anything`, `protein-small_molecule`, `nanobody-anything`, `antibody-anything`

### Option 2: Local installation
```bash
git clone https://github.com/HannesStark/boltzgen.git
cd boltzgen
pip install -e .
python sample.py config=config.yaml
```

## Key parameters (CLI)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input-yaml` | required | Path to YAML design specification |
| `--protocol` | `protein-anything` | Design protocol |
| `--num-designs` | 10 | Number of designs to generate |
| `--steps` | all | Pipeline steps to run |

## YAML configuration

BoltzGen uses an **entity-based YAML format**.

**Important notes:**
- Residue indices use `label_seq_id` (1-indexed), not author residue numbers
- File paths are relative to the YAML file location
- Target files should be in CIF format (PDB also works but CIF preferred)
- Run `boltzgen check config.yaml` to verify before running

### Basic Binder Config
```yaml
entities:
  - protein:
      id: B
      sequence: 80..140

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

### Peptide Design (Cyclic)
```yaml
entities:
  - protein:
      id: S
      sequence: 10..14C6C3

  - file:
      path: target.cif
      include:
        - chain:
            id: A

constraints:
  - bond:
      atom1: [S, 11, SG]
      atom2: [S, 18, SG]
```

## Design protocols

| Protocol | Use Case |
|----------|----------|
| `protein-anything` | Design proteins to bind proteins or peptides |
| `peptide-anything` | Design cyclic peptides to bind proteins |
| `protein-small_molecule` | Design proteins to bind small molecules |
| `nanobody-anything` | Design nanobody CDRs |
| `antibody-anything` | Design antibody CDRs |

## Output format

```
output/
├── sample_0/
│   ├── design.cif
│   ├── metrics.json
│   └── sequence.fasta
└── summary.csv
```

## Typical performance

| Campaign Size | Time (L40S) | Cost (Modal) |
|---------------|-------------|--------------|
| 50 designs | 30-45 min | ~$8 |
| 100 designs | 1-1.5h | ~$15 |
| 500 designs | 5-8h | ~$70 |

## Decision tree

```
Should I use BoltzGen?
│
├─ All-atom precision needed → BoltzGen ✓
├─ Ligand binding pocket → BoltzGen ✓
├─ Speed/diversity priority → BindCraft (multiple runs)
├─ Highest success rate → BindCraft
└─ Have L40S/A100 (48GB+) → BoltzGen ✓
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Large design | Use A100-80GB or reduce designs |
| `FileNotFoundError: *.cif` | Target file not found | File paths are relative to YAML |
| `ValueError: invalid chain` | Chain not in target | Verify chain IDs |
| `modal: command not found` | Modal CLI not installed | `pip install modal && modal setup` |

**Next**: Validate with `boltz` or `chai` → `protein-qc` for filtering.
