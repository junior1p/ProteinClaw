---
name: setup
description: >
  First-time setup for protein design tools. Use this skill when:
  (1) User is new and hasn't run any tools yet,
  (2) Commands fail with "file not found" or "modal: command not found",
  (3) Modal authentication errors occur,
  (4) User asks how to get started or set up the environment,
  (5) biomodals directory is missing or tools aren't working.
license: MIT
category: utilities
tags: [setup, onboarding, installation]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Setup Guide

## Quick Checklist

| Step | Check | Fix |
|------|-------|-----|
| 1. Modal CLI | `modal --version` | `pip install modal` |
| 2. Modal auth | `modal token show` | `modal setup` |
| 3. biomodals | `ls biomodals/modal_*.py` | `git clone https://github.com/hgbrian/biomodals` |
| 4. Test | `cd biomodals && modal run modal_boltzgen.py --help` | See troubleshooting |

## Full Setup Steps

### Step 1: Install Modal CLI
```bash
pip install modal
```

### Step 2: Authenticate Modal
```bash
modal setup
# Opens browser → click "Authorize"
```

Verify: `modal token show`

### Step 3: Clone biomodals
```bash
git clone https://github.com/hgbrian/biomodals
cd biomodals
```

### Step 4: Test
```bash
modal run modal_boltzgen.py --help
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `modal: command not found` | Not installed | `pip install modal` |
| `Permission denied` | Not authenticated | `modal setup` |
| `No such file: modal_boltzgen.py` | Wrong directory | `cd biomodals` |
| `uvx: command not found` | Optional wrapper | Use `modal run` directly |

## GPU Selection

```bash
GPU=T4 modal run modal_proteinmpnn.py ...  # 16GB, ProteinMPNN/ESM
GPU=A10G modal run modal_chai1.py ...      # 24GB, Chai/Boltz
GPU=L40S modal run modal_boltzgen.py ...   # 48GB, BoltzGen/BindCraft
GPU=A100 modal run modal_bindcraft.py ...  # 40-80GB, BindCraft/large complexes
```

## Modal Free Tier

$30/month in free credits — enough for:
- ~500 BoltzGen designs
- ~200 BindCraft designs
- ~1000 Chai predictions
