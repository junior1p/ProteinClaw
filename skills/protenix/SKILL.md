---
name: protenix
description: >
  Structure prediction using Protenix, ByteDance's open-source PyTorch reproduction
  of AlphaFold 3. Use this skill when:
  (1) Predicting protein/DNA/RNA/ligand/ion complex structures,
  (2) Need AF3-level accuracy with open-source code,
  (3) MSA-free fast prediction (--no-use-msa),
  (4) Multi-seed ensemble predictions,
  (5) Alternative to Chai or Boltz for validation.

  For QC thresholds, use protein-qc.
  For Chai prediction, use chai.
  For Boltz prediction, use boltz.
license: MIT
category: design-tools
tags: [structure-prediction, validation, af3, open-source]
source: https://github.com/hgbrian/biomodals
---

# Protenix Structure Prediction

Protenix is an open-source PyTorch reproduction of AlphaFold 3 by ByteDance.
Supports: protein, DNA, RNA, ligand (SMILES), ion.

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.12+ | 3.12 |
| GPU VRAM | 24GB | 48GB (L40S) |

## How to run

### FASTA input (simplest)
```bash
# Single protein
echo ">protein|A
MAWTPLLLLLLSHCTGSLSQPVLTQPTSLSASPGASARFTCTLRSGINVGTYRIYWYYQQKPGSLP" > test.faa

modal run modal_protenix.py --input-faa test.faa
```

### Protein complex
```bash
cat > complex.faa << 'EOF'
>protein|A
MKTAYIAKQRQISFVKSHFSRQLERRLEQLKQLEQQ...
>protein|B
MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFL...
EOF

modal run modal_protenix.py --input-faa complex.faa --seeds "42,43,44"
```

### With ligand (SMILES)
```bash
cat > protein_ligand.faa << 'EOF'
>protein|A
MKTAYIAKQRQISFVKSHFSRQLE...
>ligand|caffeine
CN1C=NC2=C1C(=O)N(C(=O)N2C)C
EOF

modal run modal_protenix.py --input-faa protein_ligand.faa
```

### With MSA (higher accuracy, slower)
```bash
modal run modal_protenix.py --input-faa complex.faa --use-msa
```

### JSON input (native Protenix format)
```json
[
    {
        "name": "my_complex",
        "sequences": [
            {"proteinChain": {"sequence": "MKTAYIAKQRQISFVK...", "count": 1}},
            {"proteinChain": {"sequence": "MVLSPADKTNVKAA...", "count": 1}}
        ]
    }
]
```
```bash
modal run modal_protenix.py --input-json complex.json
```

## Key parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input-faa` | - | FASTA input file |
| `--input-json` | - | JSON input (native format) |
| `--seeds` | `"42"` | Random seeds, comma-separated |
| `--use-msa` | off | Enable MSA (higher accuracy) |
| `--no-use-msa` | on | Skip MSA (faster) |

## Supported entity types

| FASTA header | Type | Example |
|---|---|---|
| `>protein\|A` | Protein chain A | standard proteins |
| `>dna\|A` | DNA chain | `ATCGATCG` |
| `>rna\|A` | RNA chain | `AUCGAUCG` |
| `>ligand\|name` | Small molecule | SMILES string as sequence |
| `>ion\|name` | Metal ion | `ZN`, `MG`, `CA` |

## Output format

```
output/
├── predictions/
│   ├── my_complex_seed-42_sample-0.cif    # Best model
│   ├── my_complex_seed-42_sample-1.cif
│   └── confidence_my_complex_seed-42.json # pLDDT, pTM, ipTM
```

## Protenix vs Chai vs Boltz

| Feature | Protenix | Chai-1 | Boltz-1 |
|---------|----------|--------|---------|
| Based on | AF3 | Novel | Novel |
| MSA | Optional | No | No |
| DNA/RNA | Yes | Yes | Yes |
| Speed (no MSA) | Fast | Fast | Fast |
| GPU needed | L40S | A100 | L40S |

## Typical performance

| Campaign | Time (L40S) | Cost (Modal) |
|----------|-------------|--------------|
| 100 complexes | 30-45 min | ~$8 |
| 500 complexes | 2-3h | ~$35 |

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Complex too large | Use A100-80GB |
| `KeyError: 'iptm'` | Single chain | Ensure 2+ chains |
| `Invalid entity type` | Bad FASTA header | Check `protein\|A`, `ligand\|name` |

**Next**: `protein-qc` for filtering and ranking.
