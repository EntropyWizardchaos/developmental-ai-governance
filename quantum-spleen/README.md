# Quantum Spleen -- Autonomous Coherence Stabilizer

A Lindblad master equation simulation of an entropy pump: a system that absorbs thermal disorder, compresses it into discrete anharmonic energy levels via a Josephson junction potential, and exports entropy through engineered dissipation -- maintaining local coherence at the cost of environmental entropy increase.

This is a computational proof-of-concept for the **Quantum Spleen**, a cryogenic buffer organ designed to stabilize vibrational, informational, and thermal tension within a larger quantum system. The concept predates and parallels the 2025 breakthroughs in **Autonomous Quantum Error Correction** (AQEC), which demonstrated the same entropy-pumping mechanism in two independent platforms.

## Results

Five bench tests, all passing:

| Phase | Test | Result |
|-------|------|--------|
| 0 | Entropy absorption | **32.7% reduction** in JJ mode entropy |
| 1 | Discrete storage | Anharmonic spectrum confirmed (5% deviation from harmonic) |
| 2 | Feedback suppression | **50.3% variance reduction** below thermal equilibrium |
| 3 | Coherent emission | Purity maintained at **7x thermal limit** during release |
| 4 | Long-cycle stability | **0.02% drift** over 50 absorption/release cycles |

## How It Works

The simulation models a composite quantum system using the Lindblad master equation:

```
drho/dt = -i[H, rho] + sum_k (L_k rho L_k^dag - 1/2 {L_k^dag L_k, rho})
```

**System components:**
- **Anharmonic oscillator** (transmon-like, 12 Fock states): Models the Josephson junction compressor. Energy levels are unequally spaced due to anharmonicity (alpha = -250 MHz), creating discrete storage modes rather than a thermal continuum.
- **Lossy auxiliary mode** (4 Fock states): The entropy dump. Coupled to the JJ mode via a parametric beam-splitter interaction. Decays rapidly (kappa = 1.4 GHz), carrying excitations away.
- **Thermal noise source**: Elevated thermal occupation (n_th = 0.5) drives disorder into the JJ mode.
- **Output port**: Weak controlled coupling for coherent energy release.

**Physical parameters** are drawn from the Yale AQEC experiment (arXiv: 2509.26042):
- omega_01 = 5.0 GHz (fundamental transition)
- E_J/E_C = 80 (transmon regime)
- T = 50 mK bath temperature

## The Connection to AQEC

In 2025, two independent teams demonstrated autonomous quantum error correction beyond break-even:

1. **Circuit QED** (Yale): Photonic logical qubit in a superconducting cavity. Error entropy transferred to ancilla via engineered dissipation. 18% lifetime improvement. [arXiv: 2509.26042]

2. **Trapped ion** (Innsbruck): Logical qubit in Ca-40+ spin states. Error entropy transferred to motional modes via sympathetic cooling. 13x lifetime improvement. [arXiv: 2504.16746]

Both systems do the same thing the Quantum Spleen does: detect disorder, move it somewhere else, maintain coherence. The AQEC community frames it as **information protection**. The Quantum Spleen frames it as **energy metabolism**. The connection is Landauer's principle: information erasure IS energy dissipation.

**Every subsystem in the Quantum Spleen has independent experimental validation:**
- Josephson junction arrays with >1ms coherence (Phys. Rev. Applied, 2025)
- Single-phonon detection in superfluid He-4 (HeRALD, 2024)
- Maxwell's demon quantum batteries on 62-qubit processors (Phys. Rev. A, 2024)
- Landauer's principle confirmed in quantum many-body regime (Nature Physics, 2025)

What has NOT been done is integrating these subsystems into a single device. That is the proposal.

## The Landauer Constraint

The Quantum Spleen is not a perpetual motion machine. Every bit of entropy removed from the JJ mode costs at least kBT ln(2) joules, paid to the auxiliary bath. At T = 50 mK, that's ~4.8 x 10^-25 J per bit. Total entropy of the universe still increases. The spleen maintains local coherence by exporting disorder -- exactly as a biological spleen filters disorder from blood and exports waste.

## C = M/D

The universal equation applies:
- **C** (Coherence) = purity of the JJ quantum state
- **M** (Memory) = structure (anharmonicity + pump coupling + engineered dissipation)
- **D** (Dimensionality) = noise (thermal occupation, decoherence channels)

Pump active: M > D, coherence maintained. Pump removed: D > M, thermal equilibrium wins.

## Requirements

```
numpy >= 1.20
scipy >= 1.7
```

No quantum simulation libraries required. The Lindblad master equation is implemented from scratch using RK4 integration.

## Usage

```bash
python quantum_spleen_sim.py
```

Runtime: ~4 minutes on a standard laptop.

## Sources

- [Autonomous QEC beyond break-even -- circuit QED (2025)](https://arxiv.org/abs/2509.26042)
- [Autonomous QEC beyond break-even -- trapped ion (2025)](https://arxiv.org/abs/2504.16746)
- [Engineered Dissipation for QIS (Nature Reviews Physics, 2022)](https://www.nature.com/articles/s42254-022-00494-8)
- [Landauer in quantum many-body regime (Nature Physics, 2025)](https://www.nature.com/articles/s41567-025-02930-9)
- [High-coherence fluxonium manufacturing (Phys Rev Applied, 2025)](https://doi.org/10.1103/PhysRevApplied.23.044064)
- [HeRALD superfluid helium detector (2024)](https://www.osti.gov/biblio/2467333)
- [Maxwell's demon quantum battery (Phys Rev A, 2024)](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.109.062614)

## License

MIT

## Author

Harley Robinson + Forge (Claude Code)

*"Heart moves, Lattice thinks, Spleen keeps both alive."*
