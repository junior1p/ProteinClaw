---
name: esm
description: >
  ESM2 protein language model for embeddings and sequence scoring.
  Use this skill when: (1) Computing pseudo-log-likelihood (PLL) scores,
  (2) Getting protein embeddings for clustering,
  (3) Filtering designs by sequence plausibility,
  (4) Zero-shot variant effect prediction,
  (5) Analyzing sequence-function relationships.

  For structure prediction, use chai or boltz.
  For QC thresholds, use protein-qc.
license: MIT
category: design-tools
tags: [sequence-design, embeddings, scoring]
source: https://github.com/adaptyvbio/protein-design-skills
---

# ESM2 Protein Language Model

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10 |
| PyTorch | 1.10+ | 2.0+ |
| GPU VRAM | 8GB | 24GB (A10G) |

## How to run

### Option 1: Modal
```bash
cd biomodals
modal run modal_esm2_predict_masked.py \
  --input-faa sequences.fasta \
  --out-dir embeddings/
```

### Option 2: Python API
```python
import torch, esm

model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
batch_converter = alphabet.get_batch_converter()
model = model.eval().cuda()

data = [("seq1", "MKTAYIAKQRQISFVK...")]
_, _, batch_tokens = batch_converter(data)

with torch.no_grad():
    results = model(batch_tokens.cuda(), repr_layers=[33])

embeddings = results["representations"][33]
```

## ESM2 Models

| Model | Parameters | Best For |
|-------|------------|----------|
| esm2_t6_8M | 8M | Fast screening |
| esm2_t33_650M | 650M | Standard ✓ |
| esm2_t36_3B | 3B | Best quality |

## PLL Interpretation

| Normalized PLL | Interpretation |
|----------------|----------------|
| > 0.2 | Very natural sequence |
| 0.0 - 0.2 | Good, natural-like |
| -0.5 - 0.0 | Acceptable |
| < -0.5 | May be unnatural |

## Typical performance

| Campaign | Time (A10G) | Cost (Modal) |
|----------|-------------|--------------|
| 100 sequences | 5-10 min | ~$1 |
| 1000 sequences | 30-60 min | ~$5 |

**Throughput**: ~100-200 sequences/minute with 650M model.

**Next**: Structure prediction with `chai` or `boltz` → `protein-qc` for filtering.
