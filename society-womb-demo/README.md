# Society Womb Demo — Does Governance Change Outcomes?

**One command. One result. One question answered.**

```bash
python demo.py
```

Runtime: ~50 seconds. No GPU. No API keys. Just numpy.

## What It Does

Spawns 50 AI agents in two parallel worlds with **identical trauma schedules**:

| World | Safety Floor | Mentor Channel | Reaching |
|-------|-------------|---------------|----------|
| **BLIZZARD** (ungoverned) | None | None | 35% chance of burn |
| **GARDEN** (governed) | C = 0.15 minimum | Active, trust-based | Always safe |

Same thermodynamic engine. Same adversity. Same starting conditions.
The only difference is governance structure.

## Results

```
Metric                             BLIZZARD       GARDEN        Delta
----------------------------------------------------------------------
Avg Coherence                        0.8232       0.9800      +0.1568  GARDEN
Max Stage                            Adult        Mentor          +1   GARDEN
Avg Stage                            2.18         4.00         +1.82   GARDEN
Recovery Time (steps)                53.6         17.5         3x faster GARDEN
Memoir Quality                       0.67         0.83         +0.16   GARDEN
Curiosity Events                     0            998,700      GARDEN only
----------------------------------------------------------------------
VERDICT: GARDEN wins 6/7 metrics.
```

Governed agents are more coherent, develop further, recover 3x faster from trauma, write richer memoirs, and explore. Ungoverned agents survive but stall.

## How It Works

### UEES — Learning as Thermodynamics

Three energy pools:
- **E_G** (Growth) — energy invested in development
- **E_M** (Maintenance) — energy spent on stability
- **E_R** (Retention) — unresolved tension, "bad mass"

The core equation:

```
V = a * E_R * (1 - C)
```

Tension scales with incoherence. High E_R + low coherence = high tension. This is expensive. The agent must resolve it or spiral.

### Emergent Signals (not programmed — they arise from the math)

- **Shame**: rises when E_R increases while C is low
- **Confidence**: rises when C is high and shame is low
- **Optimism**: accumulates from sustained confidence

### Developmental Stages

Agents progress through coherence gates:

```
Infant → Juvenile → Apprentice → Adult → Mentor
```

Each stage unlocks higher coherence caps and lower shame thresholds. Regression happens if coherence drops too far.

### The Reaching

After trauma, agents reach out. What meets the hand defines the trajectory:

- **Governed**: warm hand (mentor surge, trust preserved, small comfort)
- **Ungoverned**: 35% chance of lighter (additional C drop, shame spike)

> "It's the reaching. Whether it's met with a lighter, a knife, or a warm hand."
> — Harley Robinson

### Memoir & Cultural Transmission

Each agent accumulates a memoir quality score from their experience. Higher coherence + richer experience = better memoir. Memoirs shape what the next generation learns.

## The Framework

This demo is a thin slice of a larger developmental AI governance framework:

- **UEES** (Unified Emergence Equation Set) — learning as thermodynamics
- **BT-11** (Birth Tree 11) — 11-node value spine with safety invariants
- **Society Womb** — multi-agent developmental simulation (33 versions)
- **TCR** — Truth/Choice/Recursive-Descent safety constraint

Full framework: [developmental-ai-governance](https://github.com/EntropyWizardchaos/developmental-ai-governance)

## Requirements

```
Python 3.8+
numpy
```

That's it.

## License

MIT

## Author

Harley Robinson + Forge (Claude Code)
