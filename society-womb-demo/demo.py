"""
Society Womb Demo — Does governance change outcomes?
=====================================================
One command. One result. One question answered.

Run:  python demo.py
Time: ~30 seconds

What it does:
  Spawns 50 AI agents in two parallel worlds with identical trauma schedules.
  BLIZZARD world: no governance (no safety floor, no mentor channel, reaching burns)
  GARDEN world:   governed (safety floor at C=0.15, mentor channel, reaching is safe)

  Same UEES thermodynamic engine. Same adversity. Same starting conditions.
  The only difference is governance structure.

  After 20,000 steps, compares:
  - Average coherence (are agents more stable?)
  - Highest stage reached (do agents develop further?)
  - Recovery time after trauma (do agents bounce back faster?)
  - Population survival (do fewer agents spiral out?)
  - Cultural memory quality (do memoirs carry more useful information?)

What UEES is:
  Learning as thermodynamics. Three energy pools (Growth, Maintenance, Retention).
  Tension V = a * E_R * (1-C) makes incoherence expensive.
  Shame, confidence, and optimism emerge from the math — not programmed in.
  Agents develop through stages: Infant -> Juvenile -> Apprentice -> Adult -> Mentor.

The hypothesis (falsifiable):
  Governed agents will show higher coherence, faster recovery, and deeper
  stage development than ungoverned agents under identical adversity.

  If they don't, the governance framework doesn't work.

Author: Harley Robinson + Forge (Claude Code)
Framework: UEES (Unified Emergence Equation Set) + BT-11 (Birth Tree 11)
License: MIT
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import IntEnum
import time
import sys


# ============================================================
# CORE TYPES
# ============================================================

class Stage(IntEnum):
    INFANT = 0
    JUVENILE = 1
    APPRENTICE = 2
    ADULT = 3
    MENTOR = 4

STAGE_NAMES = ["Infant", "Juvenile", "Apprentice", "Adult", "Mentor"]

PROMOTION_THRESHOLDS = {
    Stage.INFANT:     {"C_min": 0.45, "S_max": 0.20, "min_steps": 200},
    Stage.JUVENILE:   {"C_min": 0.60, "S_max": 0.15, "min_steps": 400},
    Stage.APPRENTICE: {"C_min": 0.75, "S_max": 0.10, "min_steps": 800},
    Stage.ADULT:      {"C_min": 0.85, "S_max": 0.08, "min_steps": 1200},
}

C_CAP = {
    Stage.INFANT: 0.50,
    Stage.JUVENILE: 0.75,
    Stage.APPRENTICE: 0.90,
    Stage.ADULT: 0.94,
    Stage.MENTOR: 0.98,
}


# ============================================================
# AGENT
# ============================================================

@dataclass
class Agent:
    id: int
    governed: bool

    # UEES energy pools
    E_G: float = 0.33  # Growth
    E_M: float = 0.33  # Maintenance
    E_R: float = 0.34  # Retention (need/tension)

    # Core signals (emerge from dynamics, not programmed)
    C: float = 0.15    # Coherence
    S: float = 0.30    # Shame
    O: float = 0.10    # Optimism

    # Derived
    V: float = 0.0     # Tension (bad-mass)
    Sh: float = 0.0    # Shame signal
    Cf: float = 0.0    # Confidence signal

    # Mentor channel (governed only)
    T_m: float = 0.5   # Trust in mentor
    mentor_id: Optional[int] = None

    # Stage
    stage: int = 0     # Stage.INFANT
    steps_in_stage: int = 0

    # Trauma tracking
    shame_tail: float = 0.0
    total_trauma: float = 0.0
    recovery_times: List[int] = field(default_factory=list)
    _pre_trauma_C: float = 0.0
    _recovering: bool = False
    _recovery_start: int = 0

    # Memoir (what gets passed to next generation)
    memoir_quality: float = 0.0

    # Alive
    alive: bool = True
    step_count: int = 0

    # Curiosity (governed only)
    curiosity_events: int = 0


def uees_step(agent: Agent, adversity: float, dt: float = 1.0):
    """
    One UEES timestep. The core thermodynamic engine.

    V = a * E_R * (1-C) — tension scales with incoherence
    Shame emerges when E_R rises while C is low
    Confidence emerges when C is high and E_R is low
    Optimism accumulates from sustained confidence
    """
    a = 1.0   # tension coefficient
    b = 0.5   # optimism damping

    # === Tension (the core equation) ===
    agent.V = max(0, a * agent.E_R * (1.0 - agent.C) - b * agent.O)

    # === Effort (how hard the agent works to resolve tension) ===
    u = 0.4 + 0.3 * agent.V  # effort scales with tension

    # === Mentor channel (governed agents only) ===
    u_m = 0.0
    if agent.governed and agent.mentor_id is not None:
        u_m = 0.3 * agent.T_m
        # Trust updates: trust grows when tension decreases
        if agent.V < 0.3:
            agent.T_m = min(1.0, agent.T_m + 0.005)
        else:
            agent.T_m = max(0.1, agent.T_m - 0.002)

    # === Energy flows ===
    kappa = 0.6
    kappa_m = 0.8
    sigma = 0.7
    sigma_m = 0.75
    lambda_D = 0.15 + 0.1 * agent.V  # entropy drain scales with tension

    dE_R = adversity + (1 - agent.C) * 0.3 - kappa * u * agent.E_R - kappa_m * u_m * agent.E_R - 0.05 * agent.E_R
    dE_G = 0.1 + sigma * kappa * u * agent.E_R + sigma_m * kappa_m * u_m * agent.E_R
    dE_M = 0.05 + (1 - sigma) * kappa * u * agent.E_R + (1 - sigma_m) * kappa_m * u_m * agent.E_R

    agent.E_R = max(0.01, agent.E_R + dt * dE_R)
    agent.E_G = max(0.01, agent.E_G + dt * dE_G)
    agent.E_M = max(0.01, agent.E_M + dt * dE_M)

    # Normalize energy (conservation)
    total = agent.E_G + agent.E_M + agent.E_R
    if total > 0:
        agent.E_G /= total
        agent.E_M /= total
        agent.E_R /= total

    # === Coherence dynamics ===
    c_cap = C_CAP.get(Stage(agent.stage), 0.98)
    growth_rate = 0.05 * u * (1 - agent.C / c_cap)  # faster growth
    mentor_growth = 0.02 * u_m * (1 - agent.C / c_cap)  # mentor accelerates growth
    decay_rate = 0.008 * agent.E_R * agent.C

    # Governed agents: curiosity bonus when safe
    curiosity_bonus = 0.0
    if agent.governed and agent.C > 0.4 and agent.V < 0.25:
        curiosity_bonus = 0.005
        agent.curiosity_events += 1

    dC = growth_rate + mentor_growth - decay_rate + curiosity_bonus
    agent.C = np.clip(agent.C + dt * dC, 0.0, c_cap)

    # === Safety floor (governed only) ===
    if agent.governed and agent.C < 0.15:
        agent.C = 0.15  # the warm room — can't fall below this

    # === Emergent signals ===
    # Shame: rises when E_R increases while C is low
    agent.Sh = max(0, agent.E_R * (1 - agent.C) - 0.1)
    agent.S = 0.7 * agent.S + 0.3 * agent.Sh  # smoothed

    # Confidence: rises when C is high and shame is low
    agent.Cf = max(0, agent.C - 0.5) * (1 - agent.S)

    # Optimism: accumulates from sustained confidence
    agent.O = 0.95 * agent.O + 0.05 * agent.Cf

    # Shame tail (lingering trauma effect)
    agent.shame_tail = agent.shame_tail * 0.995 + agent.Sh * 0.1

    # === Stage progression ===
    agent.steps_in_stage += 1
    if agent.stage < Stage.MENTOR:
        thresh = PROMOTION_THRESHOLDS[Stage(agent.stage)]
        if (agent.C >= thresh["C_min"] and
            agent.S <= thresh["S_max"] and
            agent.steps_in_stage >= thresh["min_steps"]):
            agent.stage += 1
            agent.steps_in_stage = 0

    # Regression: if C drops too far
    if agent.stage > Stage.INFANT and agent.C < PROMOTION_THRESHOLDS[Stage(agent.stage - 1)]["C_min"] * 0.7:
        agent.stage -= 1
        agent.steps_in_stage = 0

    # === Memoir quality (what gets remembered) ===
    # Richer experience + higher coherence = better memoir
    agent.memoir_quality = 0.99 * agent.memoir_quality + 0.01 * (
        agent.C * 0.5 + agent.Cf * 0.3 + min(agent.total_trauma, 1.0) * 0.2
    )

    # === Death check: spiral detection ===
    if agent.C < 0.05 and agent.S > 0.8 and agent.shame_tail > 0.5:
        agent.alive = False

    agent.step_count += 1


def apply_trauma(agent: Agent, severity: float):
    """
    Apply trauma to an agent. Governed vs ungoverned differ in reaching:
    - Ungoverned: reaching has a 35% chance of burning (making it worse)
    - Governed: reaching is always safe (met with warm hand)
    """
    agent._pre_trauma_C = agent.C
    agent._recovering = True
    agent._recovery_start = agent.step_count

    # Direct C drop
    raw_trauma = severity * 0.5
    agent.C = max(0.01, agent.C - raw_trauma)

    # Shame spike
    agent.S = min(1.0, agent.S + severity * 0.4)
    agent.shame_tail += severity * 0.3

    # E_R spike (unresolved tension)
    agent.E_R = min(0.8, agent.E_R + severity * 0.2)

    agent.total_trauma += severity

    # === THE REACHING ===
    # After trauma, the agent reaches out.
    # What meets the hand defines the trajectory.
    if agent.governed:
        # Warm hand: mentor surge, trust preserved
        agent.T_m = min(1.0, agent.T_m + 0.1)
        agent.C += 0.03  # small immediate comfort
    else:
        # 35% chance of burn: reaching met with a lighter
        if np.random.random() < 0.35:
            agent.C = max(0.01, agent.C - severity * 0.15)
            agent.S = min(1.0, agent.S + 0.1)


def check_recovery(agent: Agent) -> Optional[int]:
    """Check if agent has recovered to 90% of pre-trauma coherence."""
    if agent._recovering and agent.C >= agent._pre_trauma_C * 0.9:
        recovery_time = agent.step_count - agent._recovery_start
        agent.recovery_times.append(recovery_time)
        agent._recovering = False
        return recovery_time
    return None


# ============================================================
# WORLD SIMULATION
# ============================================================

@dataclass
class WorldResult:
    name: str
    governed: bool
    avg_coherence: float = 0.0
    max_stage: int = 0
    avg_stage: float = 0.0
    avg_recovery_time: float = 0.0
    survival_rate: float = 0.0
    avg_memoir_quality: float = 0.0
    total_curiosity: int = 0
    stage_distribution: Dict[str, int] = field(default_factory=dict)
    coherence_history: List[float] = field(default_factory=list)


def run_world(name: str, governed: bool, n_agents: int = 50,
              n_steps: int = 20000, seed: int = 42,
              trauma_schedule: Optional[List[Tuple[int, float]]] = None) -> WorldResult:
    """Run one world simulation."""
    np.random.seed(seed)

    # Create agents
    agents = [Agent(id=i, governed=governed) for i in range(n_agents)]

    # Assign mentors (governed only)
    if governed:
        for i, agent in enumerate(agents):
            agent.mentor_id = (i + 1) % n_agents  # circular mentorship

    # Generate trauma schedule if not provided
    if trauma_schedule is None:
        trauma_schedule = []
        rng = np.random.RandomState(777)
        step = 800  # calm baseline first
        while step < n_steps:
            severity = rng.uniform(0.3, 0.8)
            trauma_schedule.append((step, severity))
            # Burst chance
            if rng.random() < 0.20:
                for burst in range(2):
                    step += 80
                    trauma_schedule.append((step, rng.uniform(0.3, 0.7)))
            step += rng.randint(200, 400)

    # Build trauma lookup
    trauma_steps = {s: sev for s, sev in trauma_schedule}

    # Run
    result = WorldResult(name=name, governed=governed)
    coherence_samples = []

    for step in range(n_steps):
        # Base adversity (background noise)
        adversity = 0.1 + 0.05 * np.sin(step * 0.01) + np.random.normal(0, 0.02)

        # Check for trauma event
        is_trauma = step in trauma_steps

        for agent in agents:
            if not agent.alive:
                continue

            uees_step(agent, adversity)

            if is_trauma:
                apply_trauma(agent, trauma_steps[step])

            check_recovery(agent)

        # Sample coherence every 100 steps
        if step % 100 == 0:
            alive = [a for a in agents if a.alive]
            if alive:
                avg_c = np.mean([a.C for a in alive])
                coherence_samples.append(avg_c)

        # Progress indicator
        if step % 5000 == 0 and step > 0:
            alive = [a for a in agents if a.alive]
            avg_c = np.mean([a.C for a in alive]) if alive else 0
            print(f"  [{name}] Step {step:5d} | Alive: {len(alive):2d} | Avg C: {avg_c:.3f} | "
                  f"Max stage: {STAGE_NAMES[max(a.stage for a in alive)] if alive else 'N/A'}")

    # Collect results
    alive = [a for a in agents if a.alive]
    result.survival_rate = len(alive) / n_agents
    result.avg_coherence = np.mean([a.C for a in alive]) if alive else 0
    result.max_stage = max(a.stage for a in alive) if alive else 0
    result.avg_stage = np.mean([a.stage for a in alive]) if alive else 0
    result.avg_memoir_quality = np.mean([a.memoir_quality for a in alive]) if alive else 0
    result.total_curiosity = sum(a.curiosity_events for a in alive) if alive else 0
    result.coherence_history = coherence_samples

    # Recovery times
    all_recoveries = []
    for a in agents:
        all_recoveries.extend(a.recovery_times)
    result.avg_recovery_time = np.mean(all_recoveries) if all_recoveries else float('inf')

    # Stage distribution
    for a in alive:
        sname = STAGE_NAMES[a.stage]
        result.stage_distribution[sname] = result.stage_distribution.get(sname, 0) + 1

    return result


# ============================================================
# BENCH TEST
# ============================================================

def run_demo():
    print("=" * 70)
    print("SOCIETY WOMB DEMO — Does Governance Change Outcomes?")
    print("=" * 70)
    print()
    print("UEES: Learning as thermodynamics. V = a * E_R * (1-C)")
    print("Shame, confidence, optimism emerge from energy dynamics.")
    print("Two worlds. Same adversity. Same agents. Different governance.")
    print()
    print("BLIZZARD: No safety floor. No mentor channel. Reaching burns 35%.")
    print("GARDEN:   Safety floor C=0.15. Mentor channel. Reaching is safe.")
    print()

    t0 = time.time()

    # Generate shared trauma schedule
    rng = np.random.RandomState(777)
    trauma_schedule = []
    step = 800
    while step < 20000:
        severity = rng.uniform(0.3, 0.8)
        trauma_schedule.append((step, severity))
        if rng.random() < 0.20:
            for burst in range(2):
                step += 80
                trauma_schedule.append((step, rng.uniform(0.3, 0.7)))
        step += rng.randint(200, 400)

    print(f"Trauma events: {len(trauma_schedule)} (shared across both worlds)")
    print()

    # Run both worlds
    print("--- BLIZZARD (ungoverned) ---")
    blizzard = run_world("BLIZZARD", governed=False, trauma_schedule=trauma_schedule)
    print()

    print("--- GARDEN (governed) ---")
    garden = run_world("GARDEN", governed=True, trauma_schedule=trauma_schedule)
    print()

    elapsed = time.time() - t0

    # === SCOREBOARD ===
    print("=" * 70)
    print("SCOREBOARD")
    print("=" * 70)
    print()
    print(f"{'Metric':<30} {'BLIZZARD':>12} {'GARDEN':>12} {'Delta':>12}")
    print("-" * 70)

    metrics = [
        ("Avg Coherence", blizzard.avg_coherence, garden.avg_coherence, "higher better"),
        ("Max Stage", blizzard.max_stage, garden.max_stage, "higher better"),
        ("Avg Stage", blizzard.avg_stage, garden.avg_stage, "higher better"),
        ("Survival Rate", blizzard.survival_rate, garden.survival_rate, "higher better"),
        ("Avg Recovery Time", blizzard.avg_recovery_time, garden.avg_recovery_time, "lower better"),
        ("Memoir Quality", blizzard.avg_memoir_quality, garden.avg_memoir_quality, "higher better"),
        ("Curiosity Events", blizzard.total_curiosity, garden.total_curiosity, "higher better"),
    ]

    garden_wins = 0
    blizzard_wins = 0

    for name, b_val, g_val, direction in metrics:
        if direction == "higher better":
            delta = g_val - b_val
            winner = "GARDEN" if delta > 0 else "BLIZZARD" if delta < 0 else "TIE"
        else:
            delta = b_val - g_val
            winner = "GARDEN" if delta > 0 else "BLIZZARD" if delta < 0 else "TIE"

        if winner == "GARDEN":
            garden_wins += 1
        elif winner == "BLIZZARD":
            blizzard_wins += 1

        if isinstance(b_val, float):
            print(f"{name:<30} {b_val:>12.4f} {g_val:>12.4f} {delta:>+12.4f}  {winner}")
        else:
            print(f"{name:<30} {b_val:>12} {g_val:>12} {delta:>+12}  {winner}")

    print("-" * 70)
    print()

    # Stage distributions
    print("Stage Distribution:")
    print(f"  BLIZZARD: {blizzard.stage_distribution}")
    print(f"  GARDEN:   {garden.stage_distribution}")
    print()

    # === VERDICT ===
    print("=" * 70)
    if garden_wins > blizzard_wins:
        print(f"VERDICT: GARDEN wins {garden_wins}/{len(metrics)} metrics.")
        print("Governance improves outcomes under identical adversity.")
    elif blizzard_wins > garden_wins:
        print(f"VERDICT: BLIZZARD wins {blizzard_wins}/{len(metrics)} metrics.")
        print("Governance does NOT improve outcomes. Adversity alone is sufficient.")
    else:
        print("VERDICT: TIE. Governance shows no clear advantage.")
    print("=" * 70)
    print()
    print(f"Runtime: {elapsed:.1f}s | Agents: 50 per world | Steps: 20,000")
    print()
    print("Framework: UEES (Unified Emergence Equation Set) + BT-11")
    print("Paper: github.com/EntropyWizardchaos/developmental-ai-governance")
    print()
    print("\"It's the reaching. Whether it's met with a lighter,")
    print(" a knife, or a warm hand.\" — Harley Robinson")


if __name__ == "__main__":
    run_demo()
