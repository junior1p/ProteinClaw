---
name: bindcraft
description: >
  End-to-end binder design using BindCraft hallucination. Use this skill when:
  (1) Designing protein binders with built-in AF2 validation,
  (2) Running production-quality binder campaigns,
  (3) Using different design protocols (fast, default, slow),
  (4) Need joint backbone and sequence optimization,
  (5) Want high experimental success rate.


  For QC thresholds, use protein-qc.
  For tool selection guidance, use binder-design.
license: MIT
category: design-tools
tags: [structure-design, sequence-design, binder, pipeline]
source: https://github.com/adaptyvbio/protein-design-skills
---

# BindCraft Binder Design

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.9+ | 3.10 |
| CUDA | 11.7+ | 12.0+ |
| GPU VRAM | 32GB | 48GB (L40S) |
| RAM | 32GB | 64GB |

## How to run

### Option 1: Modal (recommended)
```bash
cd biomodals
modal run modal_bindcraft.py \
  --target-pdb target.pdb \
  --target-chain A \
  --binder-lengths 70-100 \
  --hotspots "A45,A67,A89" \
  --num-designs 50
```

### Option 2: Local installation
```bash
git clone https://github.com/martinpacesa/BindCraft.git
cd BindCraft && pip install -r requirements.txt

python bindcraft.py \
  --target target.pdb \
  --target_chains A \
  --binder_lengths 70-100 \
  --hotspots A45,A67,A89 \
  --num_designs 50
```

## Key parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `--target-pdb` | required | path | Target structure |
| `--target-chain` | required | A-Z | Target chain(s) |
| `--binder-lengths` | 70-100 | 40-150 | Length range |
| `--hotspots` | None | residues | Target hotspots |
| `--num-designs` | 50 | 1-500 | Number of designs |
| `--protocol` | default | fast/default/slow | Quality vs speed |

## Protocols

| Protocol | Speed | Quality | Use Case |
|----------|-------|---------|----------|
| fast | Fast | Lower | Initial screening |
| default | Medium | Good | Standard campaigns |
| slow | Slow | High | Final production |

## Output format

```
output/
├── design_0/
│   ├── binder.pdb
│   ├── complex.pdb
│   ├── metrics.json
│   └── trajectory/
└── summary.csv
```

## Typical performance

| Campaign Size | Time (L40S) | Cost (Modal) |
|---------------|-------------|--------------|
| 50 designs | 2-4h | ~$15 |
| 100 designs | 4-8h | ~$30 |
| 200 designs | 8-16h | ~$60 |

**Expected pass rate**: 30-70% with ipTM > 0.5 (target-dependent).

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Large target or long binder | Use L40S/A100, reduce binder length |
| `ValueError: no hotspots` | Hotspots not found | Check residue numbering |
| `TimeoutError` | Design taking too long | Use fast protocol |

**Next**: Rank by `ipsae` → experimental validation.
