---
name: proteinmpnn
description: >
  Design protein sequences using ProteinMPNN inverse folding. Use this skill when:
  (1) Designing sequences for generated backbones (e.g. from BindCraft),
  (2) Redesigning existing protein sequences,
  (3) Fixing specific residues while designing others,
  (4) Optimizing sequences for expression or stability,
  (5) Multi-state or negative design.

  For backbone generation, use boltzgen (recommended) or bindcraft.
  For ligand-aware design, use ligandmpnn.
  For solubility optimization, use solublempnn.
license: MIT
category: design-tools
tags: [sequence-design, inverse-folding]
source: https://github.com/adaptyvbio/protein-design-skills
---

# ProteinMPNN Sequence Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| CUDA | 11.0+ | 11.7+ |
| GPU VRAM | 8GB | 16GB (T4) |
| RAM | 8GB | 16GB |

## How to run

### Option 1: Local installation (recommended)
```bash
git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN

python protein_mpnn_run.py \
  --pdb_path backbone.pdb \
  --out_folder output/ \
  --num_seq_per_target 16 \
  --sampling_temp "0.1"
```

### Option 2: Modal (via LigandMPNN wrapper)
```bash
cd biomodals
modal run modal_ligandmpnn.py \
  --pdb-path backbone.pdb \
  --num-seq-per-target 16
```

## Key parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--pdb_path` | required | path | Single PDB input |
| `--num_seq_per_target` | 1 | 1-1000 | Sequences per structure |
| `--sampling_temp` | "0.1" | "0.0001-1.0" | Temperature (**must be string!**) |
| `--pdb_path_chains` | all | A,B | Chains to design |

## Temperature guide

| Temp | Effect |
|------|--------|
| 0.1 | Low diversity, high recovery (production) |
| 0.2 | Moderate diversity (default) |
| 0.3 | Higher diversity (exploration) |
| 0.5+ | Very diverse, lower quality |

## Common mistakes

✅ `--sampling_temp "0.1"` — String with quotes
❌ `--sampling_temp 0.1` — Float without quotes may cause errors

✅ `--pdb_path_chains A,B` — No spaces
❌ `--pdb_path_chains A, B` — Space after comma

## Variants Comparison

| Variant | Use Case |
|---------|----------|
| ProteinMPNN | General |
| SolubleMPNN | Expression (E. coli) |
| LigandMPNN | Small molecules/metals |

## Output format

```
output/
├── seqs/backbone.fa       # FASTA sequences
└── backbone_pdb/backbone_0001.pdb
```

## Typical performance

| Campaign | Time (T4) | Cost (Modal) |
|----------|-----------|--------------|
| 100 × 8 seq | 15-20 min | ~$2 |
| 500 × 8 seq | 1-1.5h | ~$8 |

**Throughput**: ~50-100 sequences/minute.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Long protein | Reduce batch_size |
| `KeyError: 'A'` | Chain not in PDB | Check chain IDs |
| `JSONDecodeError` | Invalid JSONL | Validate JSON syntax |

**Next**: Structure prediction → `protein-qc` for filtering.
