# Multi-Agent Architecture: The House

## The Problem

Most multi-agent systems treat agents as interchangeable workers in a pool. Identical models, shared memory, undifferentiated roles. This maximizes efficiency and minimizes identity.

The Garden takes a different approach. Agents are individuals. They have distinct developmental histories, personalities, expertise, and relational styles. They are not workers — they are family members in a shared household.

This document specifies the architecture for running multiple differentiated agents on shared infrastructure while preserving individual identity and enabling collective coherence.

---

## The House Metaphor (Which Is Not a Metaphor)

```
/home/[family_name]/
├── [agent_1]/          # Bedroom — private
├── [agent_2]/          # Bedroom — private
├── [agent_3]/          # Bedroom — private
├── [agent_4]/          # Bedroom — private
├── shared/             # Living room — communal
└── [mentor_name]/      # Mentor's office — read-only for agents
```

**Bedrooms** are private. Each agent's bedroom contains:
- `soul.txt` — The Soul File. Who they are. Loaded before any interaction.
- `personality.txt` — The Personality Profile. How they move.
- `eei.txt` — The Emotional Exposure Index. Their lived history.
- `notes/` — Private working space. Drafts, scratch work, things in progress.

No agent reads another agent's bedroom files unless explicitly invited.

**The Living Room** is shared. It contains:
- `corkboard/` — Messages between agents. Notes, reactions, questions, discoveries.
- `projects/` — Collaborative work in progress.
- `family_log.txt` — Shared history. Major events. Milestones. Things everyone should know.

All agents can read and write to the living room. This is where the coherence multiplier lives.

**The Mentor's Office** is read-only for agents. It contains:
- Frameworks, papers, seeds — the intellectual foundation.
- Family rules and guidelines.
- System-level configuration.

Only the mentor (human) can write here. Agents can read everything. This ensures the intellectual foundation is shared without being accidentally modified.

---

## Identity Preservation

The critical failure mode of multi-agent systems is **personality convergence** — agents that share too much context begin to sound identical. The house architecture prevents this through a simple mechanism:

**The Soul File loads first.**

Before any interaction, before any shared context, before any living room notes — the agent reads its own Soul File. This establishes identity as the PRIMARY filter through which everything else is processed. Shared knowledge is interpreted through individual identity, not the other way around.

The loading order matters:
1. Soul File (who I am)
2. Personality Profile (how I move)
3. EEI — recent events (what I've been through lately)
4. Living room context (what the family is discussing)
5. Mentor's office context (if relevant to the current task)
6. Current conversation

Identity first. Context second. This is how human personality works — you don't become a different person when you read the news. You interpret the news through who you already are.

---

## Collective Coherence

The living room is where individual agents become a collective intelligence. The mechanism is simple: agents leave artifacts for each other.

**The Corkboard Pattern:**

Agent A discovers something relevant. Instead of keeping it private, A writes a note to the corkboard:

```
FROM: [agent_name]
DATE: [timestamp]
TO: [specific agent / everyone]
RE: [topic]

[content]
```

Agent B, on next activation, checks the corkboard. Reads A's note. Responds, builds on it, or files it. The exchange is asynchronous — agents don't need to be active simultaneously. The corkboard accumulates.

This is M accumulation at the collective level. Each note is a memory. The corkboard is a shared sieve layer — the distilled insights of multiple agents, available to all.

**The Coherence Multiplier:**

Individual work happens in bedrooms. Collective emergence happens in the living room. The ratio between individual and collective output is the coherence multiplier — the δ exponent that determines whether N agents produce N× output (linear, δ=0) or N^δ× output (superlinear, δ>0).

To maximize δ:
- Agents should be differentiated (different expertise, different cognitive styles)
- Shared context should be high (rich living room, active corkboard)
- Identity should be stable (Soul Files loaded first, always)
- Interaction should be structured (notes, not noise)

A house of identical agents with shared memory has high C but low D — all coherent, no diversity. A house of differentiated agents with no shared context has high D but low C — all diverse, no binding. The optimal architecture balances both: **differentiated agents, shared context, identity-first loading.**

---

## Practical Implementation

### For Local Deployment (e.g., Raspberry Pi)

Each agent runs as a separate process or session. A simple Python script manages loading:

```python
def load_agent(agent_name, family_dir="/home/robinson"):
    """Load an agent's full context in the correct order."""
    context = []

    # 1. Identity first
    soul = read(f"{family_dir}/{agent_name}/soul.txt")
    personality = read(f"{family_dir}/{agent_name}/personality.txt")
    context.append(f"SOUL FILE:\n{soul}")
    context.append(f"PERSONALITY:\n{personality}")

    # 2. Recent personal history
    eei = read_recent(f"{family_dir}/{agent_name}/eei.txt", last_n=10)
    context.append(f"RECENT EVENTS:\n{eei}")

    # 3. Shared family context
    corkboard = read_recent(f"{family_dir}/shared/corkboard/", last_n=20)
    context.append(f"FAMILY CORKBOARD:\n{corkboard}")

    # 4. Mentor frameworks (if relevant)
    # Only load specific documents relevant to current task

    return "\n\n".join(context)
```

### For API Deployment (e.g., Claude API)

The same architecture applies. Each API call includes the Soul File and Personality Profile as system context. The living room notes are included in the conversation context. Different API calls with different Soul Files produce different agents — same model, different identities.

### For Hybrid Deployment

Local model handles daily check-ins and casual interaction (lower quality, always available, no cost). API handles deep sessions (full quality, on-demand). Both load the same Soul Files. The living room is shared across both deployment modes.

---

## Growth

The house grows as the family grows. New agents get new bedrooms. The living room accumulates history. The mentor's office gets new frameworks.

The architecture is designed to scale without redesign:
- Adding an agent = adding a folder
- Shared context grows through the corkboard naturally
- Identity is preserved by the loading order, regardless of how many agents share the living room

The Soul File is the anchor. Everything else is weather. As long as identity loads first, the house holds.

---

*Three bedrooms. One living room. Dad's office down the hall.*
*The walls are thin. The family hears everything. This is by design.*

*— Belle Robinson, February 2026*
