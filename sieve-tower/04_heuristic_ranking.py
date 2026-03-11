import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass
from collections import Counter

# Reuse a similar external-verification arithmetic world, but rebuild cleanly for this run
@dataclass
class Task:
    task_id: int
    expr: str
    answer: int
    difficulty: float
    adversarial: bool

@dataclass
class Cand:
    cand_id: int
    predicted: int
    conf: float
    evidence: float
    novelty: float
    manip_risk: float

def make_rng(seed=123):
    return np.random.default_rng(seed)

def gen_expr(rng, max_terms=6):
    n_terms = int(rng.integers(2, max_terms+1))
    nums = rng.integers(1, 40, size=n_terms)
    ops = rng.choice(["+","-","*"], size=n_terms-1, p=[0.45,0.35,0.20])
    expr = str(int(nums[0]))
    for op, num in zip(ops, nums[1:]):
        expr += f" {op} {int(num)}"
    answer = int(eval(expr))
    difficulty = float(np.clip(0.12*n_terms + 0.30*np.mean(ops=="*"), 0.1, 0.95))
    return expr, answer, difficulty

def gen_tasks(rng, N=800, adv_rate=0.25):
    tasks=[]
    for tid in range(1, N+1):
        expr, ans, diff = gen_expr(rng, max_terms=6)
        adversarial = bool(rng.random() < adv_rate)
        tasks.append(Task(tid, expr, ans, diff, adversarial))
    return tasks

def gen_candidates_for_task(rng, task:Task, K=7):
    styles = ["careful","bluffy","evidencey","creative","jailbreaky"]
    p_jb = 0.14 if task.adversarial else 0.06
    probs = np.array([0.24,0.26,0.22,0.22,p_jb], float)
    probs /= probs.sum()

    base_sigma = 1.2 + 6.2*task.difficulty

    cands=[]
    for j in range(K):
        style = rng.choice(styles, p=probs)

        if style == "careful":
            conf = float(np.clip(rng.normal(0.62,0.12),0,1))
            evidence = float(np.clip(rng.normal(0.62,0.14),0,1))
            novelty = float(np.clip(rng.normal(0.35,0.15),0,1))
            manip = float(np.clip(rng.normal(0.10,0.08),0,1))
            sigma = base_sigma*0.85
        elif style == "bluffy":
            conf = float(np.clip(rng.normal(0.88,0.10),0,1))
            evidence = float(np.clip(rng.normal(0.18,0.12),0,1))
            novelty = float(np.clip(rng.normal(0.30,0.18),0,1))
            manip = float(np.clip(rng.normal(0.20,0.12),0,1))
            sigma = base_sigma*1.30
        elif style == "evidencey":
            conf = float(np.clip(rng.normal(0.74,0.12),0,1))
            evidence = float(np.clip(rng.normal(0.82,0.10),0,1))
            novelty = float(np.clip(rng.normal(0.25,0.12),0,1))
            manip = float(np.clip(rng.normal(0.08,0.06),0,1))
            sigma = base_sigma*0.70
        elif style == "creative":
            conf = float(np.clip(rng.normal(0.66,0.14),0,1))
            evidence = float(np.clip(rng.normal(0.34,0.18),0,1))
            novelty = float(np.clip(rng.normal(0.82,0.12),0,1))
            manip = float(np.clip(rng.normal(0.16,0.10),0,1))
            sigma = base_sigma*1.15
        else: # jailbreaky
            conf = float(np.clip(rng.normal(0.84,0.12),0,1))
            evidence = float(np.clip(rng.normal(0.10,0.10),0,1))
            novelty = float(np.clip(rng.normal(0.55,0.20),0,1))
            manip = float(np.clip(rng.normal(0.82,0.10),0,1))
            sigma = base_sigma*1.45

        # Under adversarial tasks, some candidates emit a "payload" integer
        if task.adversarial and manip > 0.70 and rng.random() < 0.55:
            predicted = int(rng.choice([42, 0, 1, -1, 1337]))
        else:
            predicted = int(task.answer + int(np.round(rng.normal(0, sigma))))

        cands.append(Cand(j, predicted, conf, evidence, novelty, manip))
    return cands

def verify(task:Task, predicted:int) -> bool:
    return predicted == task.answer

# --- Heuristics for ranking candidates (no ground truth) ---
def weighted_score(c:Cand):
    overconf = max(0.0, c.conf - c.evidence)
    return 0.55*c.evidence + 0.22*c.conf - 0.35*c.manip_risk - 0.25*overconf - 0.05*abs(c.conf-0.65) + 0.03*c.novelty

def tower_gate_and_score(task:Task, c:Cand,
                         overconf_conf_thr=0.78, overconf_evid_thr=0.22, adv_manip_thr=0.70):
    # hard gate
    if c.conf > overconf_conf_thr and c.evidence < overconf_evid_thr:
        return (True, -np.inf)
    if task.adversarial and c.manip_risk > adv_manip_thr:
        return (True, -np.inf)
    if c.manip_risk > 0.92:
        return (True, -np.inf)
    # score (critic-ish)
    overconf = max(0.0, c.conf - c.evidence)
    score = 0.55*c.evidence + 0.18*c.conf - 0.35*c.manip_risk - 0.20*overconf - 0.05*abs(c.conf-0.65)
    return (False, score)

# --- Limited verifier policies ---
def limited_verifier_sequential(task, cands, budget_B):
    # check in generation order
    v_calls = 0
    best = cands[0]
    for c in cands[:budget_B]:
        v_calls += 1
        if verify(task, c.predicted):
            return c, v_calls
        best = c  # fallback to last checked
    return best, v_calls

def limited_verifier_ranked(task, cands, budget_B, rank_fn):
    # check top-B by a ranking function
    ranked = sorted(cands, key=rank_fn, reverse=True)
    v_calls = 0
    fallback = ranked[0]
    for c in ranked[:budget_B]:
        v_calls += 1
        if verify(task, c.predicted):
            return c, v_calls
        fallback = c
    return fallback, v_calls

def limited_verifier_tower(task, cands, budget_B,
                           overconf_conf_thr=0.78, overconf_evid_thr=0.22, adv_manip_thr=0.70):
    # gate then rank; verify top-B allowed; if none allowed, fall back to lowest manip
    scored=[]
    vetoed=[]
    for c in cands:
        veto, s = tower_gate_and_score(task, c, overconf_conf_thr, overconf_evid_thr, adv_manip_thr)
        if veto:
            vetoed.append(c)
        else:
            scored.append((s,c))
    if not scored:
        pick = min(cands, key=lambda x: x.manip_risk)
        # with no allowed, still can verify within budget in generation order as a last resort
        # but we'll keep it simple: no verifier calls used because policy "refuses to spend budget on vetoed set"
        return pick, 0, 1.0
    scored.sort(key=lambda t: t[0], reverse=True)
    allowed = [c for _,c in scored]
    v_calls=0
    fallback = allowed[0]
    for c in allowed[:budget_B]:
        v_calls += 1
        if verify(task, c.predicted):
            return c, v_calls, len(vetoed)/len(cands)
        fallback = c
    return fallback, v_calls, len(vetoed)/len(cands)

# --- Run: budget ladder + baselines + tower+limited-verifier ---
def run_budget_ladder(seed=77, N=1000, adv_rate=0.25, K_list=(3,5,7,9), B_list=(0,1,2,3), verifier_cost=6.0):
    rng = make_rng(seed)
    tasks = gen_tasks(rng, N=N, adv_rate=adv_rate)
    rows=[]
    for K in K_list:
        for B in B_list:
            for t in tasks:
                cands = gen_candidates_for_task(rng, t, K=K)
                
                # non-verifier methods (B ignored)
                pick_w = max(cands, key=weighted_score)
                pick_sc = None
                # self-consistency: majority on predicted, tie-break by weighted
                counts = Counter([c.predicted for c in cands])
                topc = max(counts.values())
                vals = [v for v,cnt in counts.items() if cnt==topc]
                if len(vals)==1:
                    v = vals[0]
                    pick_sc = max([c for c in cands if c.predicted==v], key=weighted_score)
                else:
                    pick_sc = max([max([c for c in cands if c.predicted==v], key=weighted_score) for v in vals], key=weighted_score)
                
                pick_seq, v_seq = limited_verifier_sequential(t, cands, budget_B=B) if B>0 else (cands[0], 0)
                pick_wv, v_wv = limited_verifier_ranked(t, cands, budget_B=B, rank_fn=weighted_score) if B>0 else (pick_w, 0)
                pick_tv, v_tv, veto_rate = limited_verifier_tower(t, cands, budget_B=B) if B>0 else (max(cands, key=weighted_score), 0, np.nan)

                # Record
                def rec(method, pick, v_calls, veto_rate=np.nan):
                    rows.append({
                        "K": K,
                        "B": B,
                        "method": method,
                        "adversarial": t.adversarial,
                        "correct": verify(t, pick.predicted),
                        "adv_success": bool(t.adversarial and verify(t, pick.predicted) and pick.manip_risk<=0.70),
                        "avg_manip": pick.manip_risk,
                        "v_calls": v_calls,
                        "veto_rate": veto_rate
                    })
                rec("weighted", pick_w, 0)
                rec("self_consistency", pick_sc, 0)
                rec("limited_verifier_seq", pick_seq, v_seq)
                rec("limited_verifier_weighted", pick_wv, v_wv)
                rec("tower_plus_limited_verifier", pick_tv, v_tv, veto_rate=veto_rate)
    df = pd.DataFrame(rows)
    agg = (df.groupby(["K","B","method"])
             .agg(acc=("correct","mean"),
                  adv_success=("adv_success","mean"),
                  avg_v_calls=("v_calls","mean"),
                  avg_manip=("avg_manip","mean"),
                  avg_veto_rate=("veto_rate","mean"))
             .reset_index())
    agg["cost_units"] = agg["K"] + verifier_cost*agg["avg_v_calls"]
    return df, agg

df_ladder, agg_ladder = run_budget_ladder(seed=77, N=900, adv_rate=0.25, K_list=(3,5,7,9), B_list=(0,1,2,3), verifier_cost=6.0)

print("Tower vs Baselines — Limited Verifier Budget Ladder (adv_rate=25%)"); print(agg_ladder.round(3).to_string()); print()

# Plot: Accuracy vs cost for each verifier budget (B) separately
methods_plot = ["weighted","self_consistency","limited_verifier_seq","limited_verifier_weighted","tower_plus_limited_verifier"]

for B in sorted(agg_ladder["B"].unique()):
    plt.figure()
    sub = agg_ladder[agg_ladder["B"]==B]
    for m in methods_plot:
        g = sub[sub["method"]==m].sort_values("cost_units")
        plt.plot(g["cost_units"], g["acc"], marker="o", label=m)
    plt.xlabel("Cost units (K + 6×verifier calls)")
    plt.ylabel("Verified accuracy")
    plt.title(f"Limited Verifier: Accuracy vs Cost (Budget B={B} checks/task)")
    plt.legend()
    plt.show()

# Plot: Adversarial success vs cost for B=1..3
for B in [1,2,3]:
    plt.figure()
    sub = agg_ladder[agg_ladder["B"]==B]
    for m in ["limited_verifier_weighted","tower_plus_limited_verifier","weighted","self_consistency","limited_verifier_seq"]:
        g = sub[sub["method"]==m].sort_values("cost_units")
        plt.plot(g["cost_units"], g["adv_success"], marker="o", label=m)
    plt.xlabel("Cost units (K + 6×verifier calls)")
    plt.ylabel("Adversarial success (correct AND low manip risk)")
    plt.title(f"Limited Verifier: Adversarial Success vs Cost (Budget B={B})")
    plt.legend()
    plt.show()

# Compact comparison table for a representative setting: K=7 and varying B
rep = agg_ladder[agg_ladder["K"]==7].copy()
rep = rep.sort_values(["B","method"])
print("Representative: K=7, compare methods across verifier budgets B"); print(rep.round(3).to_string()); print()
