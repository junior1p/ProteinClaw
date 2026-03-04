---
name: foldseek
description: >
  Structure similarity search with Foldseek. Use this skill when:
  (1) Finding similar structures in PDB/AFDB databases,
  (2) Structural homology search,
  (3) Database queries by 3D structure,
  (4) Finding remote homologs not detected by sequence,
  (5) Clustering structures by similarity.

  For sequence similarity, use uniprot BLAST.
  For structure prediction, use chai or boltz.
license: MIT
category: utilities
tags: [search, structure, database, similarity]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Foldseek Structure Search

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 8GB | 16GB |
| Disk | 10GB | 50GB (local databases) |

No GPU required.

## How to run

### Option 1: Web Server (Quick, rate-limited)
```bash
curl -X POST "https://search.foldseek.com/api/ticket" \
  -F "q=@query.pdb" \
  -F "database[]=afdb50" \
  -F "database[]=pdb100"
```

### Option 2: Local installation
```bash
conda install -c conda-forge -c bioconda foldseek

# Search PDB
foldseek easy-search query.pdb /path/to/pdb100 results.m8 tmp/

# Search AlphaFold DB
foldseek easy-search query.pdb /path/to/afdb50 results.m8 tmp/
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--min-seq-id` | 0.0 | Minimum sequence identity |
| `-e` | 0.001 | E-value threshold |
| `--alignment-type` | 2 | 0=3Di, 1=TM, 2=3Di+AA |

## Databases

| Database | Description | Size |
|----------|-------------|------|
| `pdb100` | PDB clustered at 100% | ~200K structures |
| `afdb50` | AlphaFold DB at 50% | ~67M structures |
| `swissprot` | SwissProt structures | ~500K structures |

## Common Use Cases

### Novelty check
```bash
foldseek easy-search design.pdb afdb50 novelty.m8 tmp/
# Novel if: top hit identity < 30%
```

### Find similar natural structures
```bash
foldseek easy-search design.pdb pdb100 similar_natural.m8 tmp/
```

### Scaffold search for motif grafting
```bash
foldseek easy-search motif.pdb pdb100 scaffolds.m8 tmp/ \
  --min-seq-id 0.0 -e 10
```

## Decision Tree

```
Searching by?
├─ 3D structure → Foldseek ✓
├─ Sequence → Use BLAST (uniprot skill)
└─ Both → Run both, compare results
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| No hits | Too strict cutoff | Lower e-value, try larger database |
| `Database not found` | Wrong path | Check database location |
| Out of memory | Large database | Use web server |

**Next**: Download hits with `pdb` skill → use for scaffold design.
