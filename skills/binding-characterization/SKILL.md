---
name: binding-characterization
description: >
  Guidance for SPR and BLI binding characterization experiments. Use when:
  (1) Planning binding kinetics experiments,
  (2) Troubleshooting poor/no binding signal,
  (3) Interpreting kinetic data artifacts,
  (4) Choosing between SPR vs BLI platforms.
license: MIT
category: experimental
tags: [binding, spr, bli, validation]
source: https://github.com/adaptyvbio/protein-design-skills
---

# Binding Characterization: SPR and BLI

## SPR vs BLI Decision Matrix

| Factor | Choose SPR | Choose BLI |
|--------|------------|------------|
| **Sensitivity** | Small molecules (<500 Da) | Large complexes, antibodies |
| **Throughput** | Low-medium (serial) | High (96-well parallel) |
| **Sample purity** | Required (clogs fluidics) | Tolerates crude lysates |
| **Kinetic resolution** | Higher (fast kinetics) | Lower |
| **Mass transport** | More sensitive | Less sensitive |
| **Maintenance** | High (fluidics) | Low (dip-and-read) |

## Troubleshooting Matrix

| Problem | Mechanism | Solution |
|---------|-----------|----------|
| Hydrophobic CDRs adsorb to SPR surface | Gold/dextran surface | Add 0.05% Tween-20, use CM7 chip |
| Aggregation in SPR fluidics | Mass transport artifacts | Filter sample (0.22μm), reduce ligand density |
| Protein degrades during continuous flow | High instability | Shorter cycle time, add trehalose 5% |
| Small analyte (<10 kDa) on BLI | Low signal | Use SPR instead |
| Weak affinity (KD >10μM) on BLI | Fast dissociation | Increase analyte concentration |

## Mass Transport Considerations

### Symptoms of mass transport limitation
- Linear association phase (not exponential)
- kon varies with ligand density
- Rmax varies with flow rate

### Mitigation
- SPR: Reduce ligand density (<200 RU), increase flow rate (50-100 μL/min)
- BLI: Reduce loading (<0.5 nm shift), increase shake speed (1000 rpm)

## Regeneration Conditions (SPR)

| Condition | Targets | Caution |
|-----------|---------|---------|
| 10 mM Glycine pH 2.0-2.5 | Most protein-protein | May denature ligand |
| 1-2 M NaCl | Ionic interactions | Mild, try first |
| 10 mM NaOH | Very stable ligands | Can hydrolyze proteins |
| 10 mM EDTA | His-tag, metal-dependent | Strips Ni-NTA |

## Kinetic Data Quality Checklist

- [ ] Reference-subtracted properly
- [ ] Buffer injection shows flat baseline
- [ ] Chi² < 10% of Rmax
- [ ] kon and koff errors < 20%
- [ ] KD from kinetics matches equilibrium KD (within 3-fold)

## Red Flags

- kon approaching mass transport limit (>10⁷ M⁻¹s⁻¹)
- Rmax >> theoretical maximum (aggregation or avidity)
- Large difference between kinetic and equilibrium KD

## References

- [SPR Guidelines - van der Merwe, Oxford](https://www.path.ox.ac.uk/wp-content/uploads/2023/09/SPR-guidelines-1.pdf)
- [BLI vs SPR - Nicoya](https://nicoyalife.com/blog/biolayer-interferometry-vs-surface-plasmon-resonance/)
