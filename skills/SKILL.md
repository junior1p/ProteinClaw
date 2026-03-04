---
name: protein-design
description: >
  Computational protein design toolkit. Use this skill group when:
  (1) Designing protein binders from scratch,
  (2) Predicting protein structures (Chai, Boltz, Protenix),
  (3) Sequence design with ProteinMPNN/LigandMPNN/SolubleMPNN,
  (4) Quality control and filtering of protein designs,
  (5) Planning and managing binder design campaigns,
  (6) Experimental characterization (SPR, BLI, cell-free expression),
  (7) Searching protein databases (PDB, UniProt, AFDB),
  (8) Antibody/nanobody design (IgGM, mBER).

  This is the top-level index. Sub-skills handle specific tools.
license: MIT
category: orchestration
tags: [protein-design, binder, structure-prediction, sequence-design, qc]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Protein Design Skill Group

A comprehensive toolkit for computational protein design, adapted from
[adaptyvbio/protein-design-skills](https://github.com/adaptyvbio/protein-design-skills)
and [hgbrian/biomodals](https://github.com/hgbrian/biomodals).

## Quick Decision Guide

### "I want to design a binder"
→ Start with `binder-design` or `campaign-manager`

### "I need to design proteins (all-atom)"
→ `boltzgen` (recommended) or `bindcraft` (integrated end-to-end)

### "I have backbones, need sequences"
→ `proteinmpnn`, `ligandmpnn` (ligand), or `solublempnn` (E. coli expression)

### "I need to validate my designs"
→ `chai`, `boltz`, or `protenix` (AF3-like)

### "I need to rank/filter designs"
→ `protein-qc` for thresholds, `ipsae` for ranking

### "I need a protein structure"
→ `pdb` (fetch), `foldseek` (structural search), `uniprot` (sequence)

### "I need antibody/nanobody design"
→ `iggm` (antibody/nanobody CDRs) or `mber` (VHH mask-based)

### "I need to express/test my protein"
→ `cell-free-expression` for CFPS, `binding-characterization` for SPR/BLI

### "I'm just getting started"
→ `setup` first, then `protein-design-workflow` for the full pipeline

## All Available Sub-Skills

### Design Tools
| Skill | Description |
|-------|-------------|
| `boltzgen` | All-atom binder design — **recommended starting point** |
| `bindcraft` | End-to-end binder design with integrated validation |
| `proteinmpnn` | General sequence design for existing backbones |
| `ligandmpnn` | Ligand/metal-aware sequence design |
| `solublempnn` | Solubility-optimized sequence design |

### Structure Prediction
| Skill | Description |
|-------|-------------|
| `chai` | Chai-1 structure prediction (protein, ligand, RNA) |
| `boltz` | Boltz-1 open-source AF3-like prediction |
| `protenix` | Protenix: ByteDance AF3 open reproduction |
| `esm` | ESM2 embeddings and sequence scoring |

### Antibody / Nanobody
| Skill | Description |
|-------|-------------|
| `iggm` | IgGM: generative model for antibody & nanobody CDR design |
| `mber` | mBER: VHH nanobody mask-based design |

### Evaluation
| Skill | Description |
|-------|-------------|
| `protein-qc` | QC metrics, thresholds, composite scoring |
| `ipsae` | ipSAE ranking (1.4× better than ipTM) |

### Databases & Utilities
| Skill | Description |
|-------|-------------|
| `pdb` | Fetch and prepare structures from RCSB PDB |
| `uniprot` | Protein sequence and annotation lookup |
| `foldseek` | Structural similarity search |

### Experimental
| Skill | Description |
|-------|-------------|
| `binding-characterization` | SPR/BLI experimental guidance |
| `cell-free-expression` | CFPS optimization and troubleshooting |

### Orchestration
| Skill | Description |
|-------|-------------|
| `binder-design` | Tool selection guidance |
| `campaign-manager` | Campaign planning and health assessment |
| `protein-design-workflow` | End-to-end pipeline guide |
| `setup` | First-time environment setup |
