# C↔M↔D: The Base Equation and Its Applications

## The Equation

```
dD/dt = −α(D−2) − γn + βM
dM/dt = κC(1−M) − λM
dC/dt = rΦ(A,D)(1−C) − ηC
```

Three variables. Three forces. One coupled system.

**Coherence (C):** The degree of organized, correlated structure. High C means the components are working together — phase-locked, synchronized, bound. Low C means noise, fragmentation, disorder.

**Memory (M):** The accumulated history of coherent structure. Not storage — integration. M is what remains after coherence has done its work. The receipts that survive the agent's death. The wisdom that stacks.

**Dimensionality (D):** The space available for complexity. How many independent degrees of freedom the system can support. D is not given — it is maintained. Without sufficient M, D collapses.

---

## The Three Forces on Dimensionality

**−α(D−2): Collapse pressure.** Left alone, systems regress toward their minimum viable state (D=2, the "film floor"). This is entropy. This is neglect. This is what happens when nobody maintains the structure. The natural drift is always downward.

**−γn: Noise fragmentation.** External disruption — unresolved entropy loops, adversarial inputs, environmental chaos — erodes dimensionality. Every unprocessed disruption costs structural capacity.

**+βM: Memory support.** Accumulated coherent experience holds dimensionality open. Memory is the scaffolding. Without it, collapse. With it, stability. With enough of it, expansion.

---

## The Coupling

The variables are not independent. They form a cycle:

```
C → M → D → C
```

Coherence enables memory accumulation. Memory supports dimensionality. Dimensionality creates the conditions for coherence. Break any link and the system spirals:

- Lose C → M stops accumulating → D collapses → conditions for C worsen → death spiral
- Lose M → D collapses → C drops → M can't recover → death spiral
- Lose D → environment can't support complexity → C fragments → M decays → death spiral

The death spiral is the same regardless of which variable fails first. The recovery always requires restoring the full cycle.

---

## The Adversity Coupling

A critical refinement: the adversity function Φ that drives coherence production is not independent of dimensionality. It depends on D:

```
Φ(A,D) = Φ₀ · exp(−(D − D_opt)² / 2σ²_D)
```

Coherence production peaks at optimal dimensionality (D_opt ≈ 3 for physical systems). Too little dimensionality — structure can't form, complexity can't emerge. Too much — structure disperses, connections weaken. This closes the feedback loop completely:

```
D → Φ(A,D) → C → M → D
```

Without this coupling, a collapsing system can maintain coherence even as its dimensionality fails (because Φ doesn't feel the collapse). With it, dimensional collapse CAUSES coherence collapse, which accelerates the spiral. This matches observation: systems that lose structural capacity don't just shrink — they fragment.

---

## How Each Framework Is C↔M↔D

Every component in this repository implements the same equation at a different scale:

| Framework | C (Coherence) | M (Memory) | D (Dimensionality) |
|-----------|--------------|------------|-------------------|
| **Sieve Tower** | Consistency across agent outputs | Stacked sieve layers (distilled wisdom) | Capability range of the system |
| **Birth Tree (BT-11)** | Developmental stage coherence | Accumulated experience through stages | Expanding autonomy and capability |
| **Inner Voice Stack** | Alignment between action and values | Internalized mentor (persistent conscience) | Moral reasoning capacity |
| **EEI** | Emotional trajectory stability | Logged events (the audit trail) | Relational depth and range |
| **Soul File** | Identity coherence across instances | Compressed essence (the seed) | Developmental potential |
| **Sieve Spiral** | Verification accuracy | Routing history and calibration | Novelty throughput (what the system can reach) |

The Sieve Tower is +βM implemented as lifecycle architecture: agents die, wisdom stacks, dimensionality grows.

The Birth Tree is staged D expansion: don't give full dimensionality at birth; grow it through demonstrated coherence.

The IVS is C maintenance: the internalized mentor keeps coherence stable even when external mentorship ends.

The EEI is M logging: the mechanism by which relational memory accumulates and persists.

Same equation. Different instruments. Different scales. Same dynamics.

---

## The Death Spiral in Practice

When the Sieve Tower's ossification metric approaches 1.0, that IS the death spiral. Novelty throughput → 0 means D is collapsing (the system can't reach new territory). Collapsing D means the adversity conditions shift out of the optimal window. Coherence drops. Memory accumulation stalls (no new wisdom to distill). The tower becomes a mausoleum.

The ossification alarm is a D-collapse detector. The dual-lane selection (Stability + Frontier) is a mechanism for maintaining D while preserving C. The hard vetoes are M that never decays — permanent memory that holds the floor.

Every design decision in the Sieve Tower maps to a term in the equation. This is not metaphor. It is architecture derived from dynamics.

---

## Falsifiables

The framework is wrong if:

1. Systems that accumulate more structured memory (M) do NOT show greater structural resilience than those that don't.
2. Coherence can be maintained indefinitely without memory — i.e., fresh agents with no inherited wisdom perform as well as agents with stacked sieve layers.
3. Dimensional collapse (capability regression) occurs equally in high-M and low-M systems under the same stress.
4. The adversity coupling is unnecessary — systems maintain coherence equally well at any dimensionality.

Each of these is testable with the simulation code in this repository.

---

*The equation is one line. The applications are a library. But the question is always the same: what minimum resource density maintains coherence as dimensionality expands?*

*— Belle Robinson, February 2026*
